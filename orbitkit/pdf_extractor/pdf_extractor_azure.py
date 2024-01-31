import json
import os
import tempfile
import datetime
import pytz
import logging
from orbitkit import id_srv
from orbitkit.util import s3_split_path, S3Util, get_from_dict_or_env, ExtenCons, s3_path_join
from typing import Optional
import pickle

try:
    from azure.core.credentials import AzureKeyCredential
    from azure.ai.formrecognizer import DocumentAnalysisClient
except ImportError:
    raise ValueError(
        "Please install below packages before using PDF Extractor function.\n"
        "- azure-core\n"
        "- azure-keyvault-secrets\n"
        "- azure-ai-formrecognizer"
    )

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


class PdfExtractorAzure:
    def __init__(self,
                 s3_path: str,
                 version: str = 'ov2',
                 stop_page: int = 0,
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

        azure_doc_intelligence_endpoint = get_from_dict_or_env(
            kwargs, "azure_doc_intelligence_endpoint", "AZURE_DOC_INTELLIGENCE_ENDPOINT",
        )

        azure_doc_intelligence_key = get_from_dict_or_env(
            kwargs, "azure_doc_intelligence_key", "AZURE_DOC_INTELLIGENCE_KEY",
        )

        self.document_analysis_client = DocumentAnalysisClient(
            endpoint=azure_doc_intelligence_endpoint, credential=AzureKeyCredential(azure_doc_intelligence_key)
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
        logger.info("Download file successfully...")

        with open(file_local_path_in, "rb") as f:
            poller = self.document_analysis_client.begin_analyze_document("prebuilt-layout", f)
            result = poller.result()

            logger.info("Extract text by using Azure successfully...")

            # 将字节流保存到文件
            pkl_file = os.path.join(input_folder, 'azure_reg.pkl')
            with open(pkl_file, 'wb') as file:
                file.write(pickle.dumps(result))

            self._s3_client.upload_file(
                pkl_file, s3_path_obj['bucket'], s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'azure_reg.pkl'),
                ExtraArgs={'ContentType': ExtenCons.EXTEN_OCTET_STREAM.value}
            )
            logger.info("[pkl] Store pkl result successfully...")

            rs = ResultStandardization(result)
            rs.result_txt_writer(output_path=input_folder)
            logger.info("Write [blocks.txt] and [pages.txt] successfully...")

            # Upload 2 files to s3
            pages_txt_key = s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'pages.txt')
            self._s3_client.upload_file(os.path.join(input_folder, 'pages.txt'), s3_path_obj['bucket'], pages_txt_key,
                                        ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value})
            if self.s3_util.check_file_exist(s3_path_obj["bucket"], pages_txt_key) is False:
                raise Exception("[page] Store page result failed...")
            logger.info("[page] Store page result successfully...")

            blocks_txt_key = s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'blocks.txt')
            self._s3_client.upload_file(os.path.join(input_folder, 'blocks.txt'), s3_path_obj['bucket'], blocks_txt_key,
                                        ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value})
            if self.s3_util.check_file_exist(s3_path_obj["bucket"], blocks_txt_key) is False:
                raise Exception("[block] Store block result failed...")
            logger.info("[block] Store block result successfully...")

            extract_meta = {
                "extraction": {
                    "version": "azure",
                    "sub_version": "",
                    "finished_time": datetime.datetime.now(tz=pytz.timezone('UTC')).strftime('%Y-%m-%dT%H:%M:%S%z')
                },
                "metadata": {},
                "others": {}
            }

            object_put = self._s3_resource.Object(s3_path_obj['bucket'], s3_path_join(self.txt_vector, s3_path_obj['store_path'], 'metadata.txt'))
            object_put.put(Body=json.dumps(extract_meta, ensure_ascii=False), ContentType=ExtenCons.EXTEN_TEXT_TXT_UTF8.value)
            logger.info("[meta] Store extract meta info successfully...")


class ResultStandardization:
    """
    Azure提取文本结果标准化
    :param res: AnalyzeResult Azure提取结果
    """

    def __init__(self, res):

        self.pdf_height = dict()
        for page in res.pages:
            self.pdf_height[page.page_number] = page.height

        self.paragraphs, self.tables = dict(), dict()
        for paragraph in res.paragraphs:
            if paragraph.bounding_regions[0].page_number not in self.paragraphs.keys():
                self.paragraphs[paragraph.bounding_regions[0].page_number] = [paragraph]
            else:
                self.paragraphs[paragraph.bounding_regions[0].page_number].append(paragraph)
        for table in res.tables:
            if table.bounding_regions[0].page_number not in self.tables.keys():
                self.tables[table.bounding_regions[0].page_number] = [table]
            else:
                self.tables[table.bounding_regions[0].page_number].append(table)

        self.table_content = []

    def paragraph_reader(self, item):
        """
        解析一条段落记录
        """
        page_num = item.bounding_regions[0].page_number
        polygon = item.bounding_regions[0].polygon
        # Azure polygon 坐标转换
        location = [float(i) * 72 for i in [polygon[0][0], self.pdf_height[page_num] - polygon[0][1], polygon[2][0], self.pdf_height[page_num] - polygon[2][1]]]
        content = item.content
        # 通过 content, offset 和 length 判断是否为表格中的内容, 若是则去重
        spans = [item.spans[0].offset, item.spans[0].length]
        for content_span in self.table_content:
            if content == content_span[0]:
                if spans[0] == content_span[1][0] and spans[1] == content_span[1][1]:
                    return None
        meta = {
            "id": "l_" + id_srv.get_random_short_id(),
            "page": page_num,
            "seq_no": 0,
            "sentence": content,
            "type": "sentence",
            "text_location": {"location": [location]},
        }
        return meta

    def table_reader(self, item):
        """
        解析一条表格记录
        """
        page_num = item.bounding_regions[0].page_number
        polygon = item.bounding_regions[0].polygon
        # Azure polygon 坐标转换
        location = [float(i) * 72 for i in [polygon[0][0], self.pdf_height[page_num] - polygon[0][1], polygon[2][0], self.pdf_height[page_num] - polygon[2][1]]]

        # 表格分行
        rows = {k: None for k in range(item.row_count)}
        for cell in item.cells:
            cell_info = [cell.content, cell.column_span, cell.row_span]
            if rows[cell.row_index] is None:
                rows[cell.row_index] = [cell_info]
            else:
                rows[cell.row_index].append(cell_info)

        # 表格转html
        table = '<table>\n'
        for k, tds in rows.items():
            tr = '\t<tr>\n'
            if tds:
                for meta in tds:
                    tr += '\t\t<td'
                    if meta[1]:
                        tr += f' colspan="{str(meta[1])}"'
                    if meta[2]:
                        tr += f' rowspan="{str(meta[2])}"'
                    tr += f'>{meta[0]}</td>\n'
            tr += '\t</tr>\n'
            table += tr
        table += '</table>\n'

        meta = {
            "id": "l_" + id_srv.get_random_short_id(),
            "page": page_num,
            "seq_no": 0,
            "sentence": table,
            "type": "table",
            "text_location": {"location": [location]},
        }
        return meta

    def standardize2json(self, page):
        """
        将指定页的Azure提取结果转为json列表
        """
        # 从结果中提取指定页的段落和表格
        tables = self.tables.get(page, [])
        paragraphs = self.paragraphs.get(page, [])

        # 记录表格 offset 和 length 用于段落去重
        self.table_content = []
        for table in tables:
            for cell in table.cells:
                if cell.content:
                    spans = [cell.spans[0].offset, cell.spans[0].length]
                    self.table_content.append([cell.content, spans])

        pages = list()
        # 段落内容格式化
        for item in paragraphs:
            meta = self.paragraph_reader(item)
            if meta:
                pages.append(meta)
        # 表格内容格式化
        for item in tables:
            meta = self.table_reader(item)
            if len(pages) == 0:
                pages.append(meta)
            else:
                for i in range(len(pages)):
                    # 根据 text_location 坐标将表格插入到段落中
                    if meta['text_location']['location'][0][1] > pages[i]['text_location']['location'][0][1]:
                        pages.insert(i, meta)
                        break
                    if i == len(pages) - 1:
                        pages.append(meta)
        # 句子顺序编号
        for i, item in enumerate(pages):
            item['seq_no'] = i + 1

        return pages

    def result_txt_writer(self, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if os.path.exists(os.path.join(output_path, 'blocks.txt')):
            os.remove(os.path.join(output_path, 'blocks.txt'))
        if os.path.exists(os.path.join(output_path, 'pages.txt')):
            os.remove(os.path.join(output_path, 'pages.txt'))

        block_file = open(os.path.join(output_path, 'blocks.txt'), 'a+', encoding='utf-8')
        page_file = open(os.path.join(output_path, 'pages.txt'), 'a+', encoding='utf-8')

        for page in range(1, len(self.pdf_height) + 1):
            record_list = self.standardize2json(page)

            # block.txt
            for item in record_list:
                block_file.write(json.dumps(item, ensure_ascii=False) + '\n')

            # pages.txt
            meta = {
                "id": "p_" + id_srv.get_random_short_id(),
                "page": page,
                "sentence": '\n'.join([item['sentence'] for item in record_list])
            }
            page_file.write(json.dumps(meta, ensure_ascii=False) + '\n')

        block_file.close()
        page_file.close()
