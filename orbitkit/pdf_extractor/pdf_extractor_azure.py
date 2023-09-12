import json
import os
import tempfile
import boto3
import datetime
import pytz
import logging
from orbitkit import id_srv
from orbitkit.util.util_aws import s3_split_path
from orbitkit.util import get_from_dict_or_env
from orbitkit.util import ExtenCons
from typing import Optional

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
        logger.info("Download file successfully...")

        with open(file_local_path_in, "rb") as f:
            poller = self.document_analysis_client.begin_analyze_document("prebuilt-layout", f)
            result = poller.result()

            logger.info("Extract text by using Azure successfully...")

            rs = ResultStandardization(result)
            rs.result_txt_writer(output_path=input_folder)
            logger.info("Write [blocks.txt] and [pages.txt] successfully...")

            # Upload 2 files to s3
            self._s3_client.upload_file(
                os.path.join(input_folder, 'pages.txt'), s3_path_obj['bucket'], os.path.join(self.txt_vector, s3_path_obj['store_path'], 'pages.txt'),
                ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value}
            )
            logger.info("[page] Store page result successfully...")

            self._s3_client.upload_file(
                os.path.join(input_folder, 'blocks.txt'), s3_path_obj['bucket'], os.path.join(self.txt_vector, s3_path_obj['store_path'], 'blocks.txt'),
                ExtraArgs={'ContentType': ExtenCons.EXTEN_TEXT_TXT_UTF8.value}
            )
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

            object_put = self._s3_resource.Object(s3_path_obj['bucket'], os.path.join(self.txt_vector, s3_path_obj['store_path'], 'metadata.txt'))
            object_put.put(Body=json.dumps(extract_meta, ensure_ascii=False), ContentType=ExtenCons.EXTEN_TEXT_TXT_UTF8.value)
            logger.info("[meta] Store extract meta info successfully...")


class ResultStandardization:
    """
    Azure提取文本结果标准化
    :param res: AnalyzeResult Azure提取结果
    """

    def __init__(self, res):
        self.result = res
        self.pdf_height = dict()
        for page in self.result.pages:
            self.pdf_height[page.page_number] = page.height
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
                    return page_num, None
        meta = {
            "id": "l_" + id_srv.get_random_short_id(),
            "page": page_num,
            "seq_no": 0,
            "sentence": content,
            "type": "sentence",
            "text_location": {"location": [location]},
        }
        return page_num, meta

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
        return page_num, meta

    def standardize2json(self):
        """
        将Azure提取结果转为json列表
        """
        tables = self.result.tables
        paragraphs = self.result.paragraphs

        # 记录表格 offset 和 length 用于段落去重
        for table in tables:
            for cell in table.cells:
                if cell.content:
                    spans = [cell.spans[0].offset, cell.spans[0].length]
                    self.table_content.append([cell.content, spans])

        page_json_set = dict()
        # 段落内容格式化
        for item in paragraphs:
            page, meta = self.paragraph_reader(item)
            if meta:
                if page not in page_json_set.keys():
                    page_json_set[page] = [meta]
                else:
                    page_json_set[page].append(meta)

        # 表格内容格式化
        for item in tables:
            page, meta = self.table_reader(item)
            if page not in page_json_set.keys():
                page_json_set[page] = [meta]
            else:
                for i in range(len(page_json_set[page])):
                    # 根据 text_location 坐标将表格插入到段落中
                    if meta['text_location']['location'][0][1] > page_json_set[page][i]['text_location']['location'][0][1]:
                        page_json_set[page].insert(i, meta)
                        break
                    if i == len(page_json_set[page]) - 1:
                        page_json_set[page].append(meta)

        # 句子顺序编号
        db_record_list = []
        for page, json_list in page_json_set.items():
            for i, j in enumerate(json_list):
                j['seq_no'] = i + 1
                db_record_list.append(j)

        return db_record_list

    def result_txt_writer(self, output_path):
        record_list = self.standardize2json()
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # block.txt
        with open(os.path.join(output_path, 'blocks.txt'), 'w+', encoding='utf-8') as f:
            for i in record_list:
                f.write(json.dumps(i, ensure_ascii=False) + '\n')

        # pages.txt
        page_list = {}
        for i in record_list:
            if i['page'] not in page_list.keys():
                page_list[i['page']] = i['sentence']
            else:
                page_list[i['page']] += '\n' + i['sentence']
        with open(os.path.join(output_path, 'pages.txt'), 'w+', encoding='utf-8') as f:
            for k, v in page_list.items():
                meta = {
                    "id": "p_" + id_srv.get_random_short_id(),
                    "page": k,
                    "sentence": v
                }
                f.write(json.dumps(meta, ensure_ascii=False) + '\n')
