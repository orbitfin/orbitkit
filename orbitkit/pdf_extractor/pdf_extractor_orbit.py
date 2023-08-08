import json
import os
import tempfile
import boto3
import pdfplumber
import logging
import datetime
import pytz
from orbitkit import id_srv
from orbitkit.util.util_aws import s3_split_path
from orbitkit.util import get_from_dict_or_env
from orbitkit.util import ExtenCons
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
    def __init__(self,
                 s3_path: str,
                 version: str = 'ov2',
                 stop_page: int = 400,
                 txt_vector: str = 'txt-vector',
                 temp_folder: Optional[str] = None,
                 *args, **kwargs):

        self.version = version
        self.s3_path = s3_path
        self.stop_page = stop_page
        self.txt_vector = txt_vector
        self.temp_folder = temp_folder

        # Try to get key aws pair
        aws_access_key_id = get_from_dict_or_env(
            kwargs, "aws_access_key_id", "AWS_ACCESS_KEY_ID",
        )

        aws_secret_access_key = get_from_dict_or_env(
            kwargs, "aws_secret_access_key", "AWS_SECRET_ACCESS_KEY",
        )

        self._s3_resource = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self._s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

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

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  按页面提取文本 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  按页面提取文本 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  按页面提取文本 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        '''Validation
        如果 pdf 页面超过 400 页，则先不提取
        '''
        with pdfplumber.open(file_local_path_in) as pdf_p_judge:
            # 先得到总页数
            total_page_pages = pdf_p_judge.pages
            if len(total_page_pages) > self.stop_page:
                raise TooManyPagesException()

        # >>>>>>>>>>>>>>>>>>>>>>>>>> 开始页面文本提取
        issue_token_cid_mark = 0
        issue_token_cid = ')(cid:'
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
                    validated_page_arr.append(1)  # 只是用来记述，没有别的意义

                    # cid calculation
                    if issue_token_cid in page_item['sentence']:
                        issue_token_cid_mark += str(page_item['sentence']).count(issue_token_cid)

                        if issue_token_cid_mark > 20:
                            raise CidEncryptionException()

        # Validation ------------------------------------------------------------------------------------
        '''Validation
        如果验证不通过，则说明 pdf 提取的问题是有问题的，没必要继续进行提取
        '''
        if len(validated_page_arr) <= 0:
            raise OcrBrokenException()
        if issue_token_cid_mark > 20:
            raise CidEncryptionException()
        # Validation ------------------------------------------------------------------------------------

        self._s3_client.upload_file(
            os.path.join(input_folder, 'pages.txt'), s3_path_obj['bucket'], os.path.join(self.txt_vector, s3_path_obj['store_path'], 'pages.txt'),
            ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value}
        )
        logger.info("[page] Store page result successfully...")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 提取文本 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 提取文本 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 提取文本 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
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

                        f_blocks.write(json.dumps(text_block_obj, ensure_ascii=False))
                        f_blocks.write('\n')
                except StopIteration:
                    break

        self._s3_client.upload_file(
            os.path.join(input_folder, 'blocks.txt'), s3_path_obj['bucket'], os.path.join(self.txt_vector, s3_path_obj['store_path'], 'blocks.txt'),
            ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value}
        )
        logger.info("[block] Store block result successfully...")

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

        object_put = self._s3_resource.Object(s3_path_obj['bucket'], os.path.join(self.txt_vector, s3_path_obj['store_path'], 'metadata.txt'))
        object_put.put(Body=json.dumps(extract_meta, ensure_ascii=False), ContentType=ExtenCons.EXTEN_TEXT_TXT_UTF8.value)
        logger.info("[meta] Store extract meta info successfully...")
