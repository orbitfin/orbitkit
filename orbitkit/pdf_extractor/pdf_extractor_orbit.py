import json
import os
import tempfile
import pdfplumber
import logging
import datetime
import pytz
from orbitkit import id_srv
from orbitkit.util import s3_split_path, S3Util, get_from_dict_or_env, ExtenCons, s3_path_join
from orbitkit.pdf_extractor.pdf_block_extractor_v2 import PdfBlockExtractV2
from orbitkit.pdf_extractor.exceptions import CidEncryptionException, OcrBrokenException, TooManyPagesException
from typing import Optional

logger = logging.getLogger(__name__)

"""默认的目录生成规则
文件名称/
- pages.txt
- pages.txt.vector
- blocks.txt
- blocks.txt.vector
- raw-azure-backup.json（如果使用 azure 解析的话，则存储一份原生备份）

文件格式：
- {'id': 'l_9Kk4iDUL', 'page': 125, 'seq_no': 31, 'sentence': 'xxx', 'type': 'sentence', 'text_location': {'location': [[752.7609, 423.47514, 774.3009, 416.99514]]}, 'others': 'xxx'}
- {'id': 'p_9Kk4iDUL', 'page': 1, 'sentence': 'xxx', 'others': 'xxx'}
"""


class PdfExtractor:
    issue_token_cid = ")(cid:"
    issue_token_cid_mark_count = 20

    def __init__(self,
                 s3_path: str,
                 version: str = "ov2",
                 stop_page: int = 400,
                 txt_vector: str = "txt-vector",
                 temp_folder: Optional[str] = None,
                 page_and_block: str = "both",
                 *args, **kwargs):

        self.version = version
        self.s3_path = s3_path
        self.stop_page = stop_page
        self.txt_vector = txt_vector
        self.temp_folder = temp_folder
        self.page_and_block = page_and_block

        if self.page_and_block not in ["both", "page", "block"]:
            raise Exception("Param exception.")

        # Try to get key aws pair
        aws_access_key_id = get_from_dict_or_env(
            kwargs, "aws_access_key_id", "AWS_ACCESS_KEY_ID",
        )

        aws_secret_access_key = get_from_dict_or_env(
            kwargs, "aws_secret_access_key", "AWS_SECRET_ACCESS_KEY",
        )

        self.s3_util = S3Util(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self._s3_resource = self.s3_util.get_s3_resource()
        self._s3_client = self.s3_util.get_s3_client()

    def extract(self):
        if self.temp_folder:
            if not os.path.exists(self.temp_folder):
                raise Exception('The temp folder given not exists...')
            self.extract_detail(self.temp_folder)
        else:
            with tempfile.TemporaryDirectory() as tmp_dir:
                input_folder = os.path.join(tmp_dir, 'input')
                if not os.path.exists(input_folder):
                    os.makedirs(input_folder)

                self.extract_detail(input_folder)

    def extract_detail(self, input_folder):
        s3_path_obj = s3_split_path(self.s3_path)

        # 开始尝试提取...
        # 下载文件到 input folder
        file_local_path_in = os.path.join(input_folder, 'tmp_filename.pdf')
        self._s3_resource.Bucket(s3_path_obj['bucket']).download_file(s3_path_obj['store_path'], file_local_path_in)
        logger.info('Download file successfully...')

        '''Validation
        如果 pdf 页面超过"指定"页数，则先不提取
        '''
        with pdfplumber.open(file_local_path_in) as pdf_p_judge:
            # 先得到总页数
            total_page_pages = pdf_p_judge.pages
            if len(total_page_pages) > self.stop_page:
                raise TooManyPagesException()

        page_ex = block_ex = True
        if self.page_and_block == "page":
            block_ex = False
        if self.page_and_block == "block":
            page_ex = False

        # 按页面提取文本
        if page_ex:
            self.extract_detail_page(total_page_pages, file_local_path_in, input_folder, s3_path_obj)

        # 提取文本
        if block_ex:
            self.extract_detail_block(file_local_path_in, input_folder, s3_path_obj)

        # 存储 metadata
        self.extract_detail_metadata(s3_path_obj)

    def extract_detail_page(self, total_page_pages, file_local_path_in, input_folder, s3_path_obj):
        issue_token_cid_mark = 0
        validated_page_arr = []

        with open(os.path.join(input_folder, 'pages.txt'), 'w+', encoding='utf-8') as f_pages:
            for pdf_page in total_page_pages:
                # 每次都打开一遍 pdf，只提取当前页的可以避免 memory leak 问题
                with pdfplumber.open(file_local_path_in) as pdfp:
                    page = pdfp.pages[pdf_page.page_number - 1]
                    logger.info(f"Start processing page [{str(page)}]...")
                    # 得到当前页的数据
                    page_item = {
                        'id': f"p_{id_srv.get_random_short_id()}",
                        'page': page.page_number,
                        'sentence': page.extract_text().strip(),
                    }
                    if page_item['sentence'] == '':
                        continue

                    f_pages.write(json.dumps(page_item, ensure_ascii=False))
                    f_pages.write('\n')
                    validated_page_arr.append(1)  # 只是用来记述，没有别的意义，说明有提取成功的数据

                    # cid calculation
                    if PdfExtractor.issue_token_cid in page_item['sentence']:
                        issue_token_cid_mark += str(page_item['sentence']).count(PdfExtractor.issue_token_cid)

                        if issue_token_cid_mark > PdfExtractor.issue_token_cid_mark_count:
                            raise CidEncryptionException()

        # Validation ------------------------------------------------------------------------------------
        '''Validation
        如果验证不通过，则说明 pdf 提取的问题是有问题的，没必要继续进行提取
        '''
        if len(validated_page_arr) <= 0:
            raise OcrBrokenException()
        if issue_token_cid_mark > PdfExtractor.issue_token_cid_mark_count:
            raise CidEncryptionException()
        # Validation ------------------------------------------------------------------------------------

        pages_txt_key = s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'pages.txt')
        self._s3_client.upload_file(os.path.join(input_folder, 'pages.txt'), s3_path_obj['bucket'], pages_txt_key,
                                    ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value})
        if self.s3_util.check_file_exist(s3_path_obj["bucket"], pages_txt_key) is False:
            raise Exception("[page] Store page result failed...")
        logger.info("[page] Store page result successfully...")

    def extract_detail_block(self, file_local_path_in, input_folder, s3_path_obj):
        issue_token_cid_mark = 0
        validated_page_arr = []

        pdf_block_extract = PdfBlockExtractV2(local_path=file_local_path_in, extend_meta={})
        pdf_block_extract_gen = pdf_block_extract.extract_iter()
        with open(os.path.join(input_folder, 'blocks.txt'), 'w+', encoding='utf-8') as f_blocks:
            while True:
                try:
                    page_data = next(pdf_block_extract_gen)
                    for _text_block in page_data:
                        text_block_obj = {
                            'id': _text_block['id'],
                            'page': _text_block['page'],
                            'seq_no': _text_block['seq_no'],
                            'sentence': _text_block['sentence'],
                            'type': _text_block['type'],
                            'text_location': _text_block['text_location'],
                        }

                        if text_block_obj['sentence'] == '':
                            continue

                        f_blocks.write(json.dumps(text_block_obj, ensure_ascii=False))
                        f_blocks.write('\n')
                        validated_page_arr.append(1)  # 只是用来记述，没有别的意义，说明有提取成功的数据

                        # cid calculation
                        if PdfExtractor.issue_token_cid in text_block_obj['sentence']:
                            issue_token_cid_mark += str(text_block_obj['sentence']).count(PdfExtractor.issue_token_cid)

                            if issue_token_cid_mark > PdfExtractor.issue_token_cid_mark_count / 2:
                                raise CidEncryptionException()
                except StopIteration:
                    break

        # Validation ------------------------------------------------------------------------------------
        '''Validation
        如果验证不通过，则说明 pdf 提取的问题是有问题的，没必要继续进行提取
        '''
        if len(validated_page_arr) <= 0:
            raise OcrBrokenException()
        if issue_token_cid_mark > PdfExtractor.issue_token_cid_mark_count:
            raise CidEncryptionException()
        # Validation ------------------------------------------------------------------------------------

        blocks_txt_key = s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'blocks.txt')
        self._s3_client.upload_file(os.path.join(input_folder, 'blocks.txt'), s3_path_obj['bucket'], blocks_txt_key,
                                    ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value})
        if self.s3_util.check_file_exist(s3_path_obj["bucket"], blocks_txt_key) is False:
            raise Exception("[block] Store block result failed...")
        logger.info("[block] Store block result successfully...")

    def extract_detail_metadata(self, s3_path_obj):
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 存储 metadata >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 存储 metadata >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 存储 metadata >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        extract_meta = {
            "extraction": {
                "version": "ov2",
                "sub_version": "",
                "finished_time": datetime.datetime.now(tz=pytz.timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
            },
            "metadata": {},
            "others": {}
        }

        object_put = self._s3_resource.Object(s3_path_obj['bucket'], s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'metadata.txt'))
        object_put.put(Body=json.dumps(extract_meta, ensure_ascii=False), ContentType=ExtenCons.EXTEN_TEXT_TXT_UTF8.value)
        logger.info("[meta] Store extract meta info successfully...")
