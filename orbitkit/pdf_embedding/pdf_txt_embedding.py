import json
import os
import tempfile
import logging
import time
from orbitkit.util import s3_split_path, S3Util, get_from_dict_or_env, ExtenCons, s3_path_join
from typing import Optional

logger = logging.getLogger(__name__)

"""默认的目录生成规则
文件名称/
- pages.txt
- pages.txt.vector
- blocks.txt
- blocks.txt.vector
- azure-reg.pkl（如果使用 azure 解析的话，则存储一份原生备份）

文件格式：
- {'id': 'l_9Kk4iDUL', 'page': 125, 'seq_no': 31, 'sentence': 'xxx', 'type': 'sentence', 'text_location': {'location': [[752.7609, 423.47514, 774.3009, 416.99514]]}, 'others': 'xxx'}
- {'id': 'p_9Kk4iDUL', 'page': 1, 'sentence': 'xxx', 'others': 'xxx'}
"""


class PdfTxtEmbedding:
    def __init__(self, s3_path: str,
                 embeddings: Optional[any] = None,
                 txt_vector: str = "txt-vector",
                 temp_folder: Optional[str] = None,
                 *args, **kwargs):

        self.s3_path = s3_path
        self.temp_folder = temp_folder

        self.txt_vector = txt_vector
        self.embeddings = embeddings
        self.chunk_size_page = 100
        self.chunk_size_block = 1000
        if self.embeddings is None:
            raise Exception("No embedding module...")

        # Try to get key aws pair
        aws_access_key_id = get_from_dict_or_env(
            kwargs, "aws_access_key_id", "AWS_ACCESS_KEY_ID",
        )

        aws_secret_access_key = get_from_dict_or_env(
            kwargs, "aws_secret_access_key", "AWS_SECRET_ACCESS_KEY",
        )

        self.s3_util = S3Util(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.s3_resource = self.s3_util.get_s3_resource()
        self.s3_client = self.s3_util.get_s3_client()

    def embed(self):
        if self.temp_folder:
            if not os.path.exists(self.temp_folder):
                raise Exception("The temp folder given not exists...")
            self.extract_detail(self.temp_folder)
        else:
            with tempfile.TemporaryDirectory() as tmp_dir:
                input_folder = os.path.join(tmp_dir, "input")
                if not os.path.exists(input_folder):
                    os.makedirs(input_folder)

                self.extract_detail(input_folder)

    def extract_detail(self, input_folder):
        s3_path_obj = s3_split_path(self.s3_path)

        # 开始尝试提取...
        start1 = time.perf_counter()

        # 下载 pages.txt 文件到 input folder
        file_local_path_in = os.path.join(input_folder, "pages.txt")
        self.s3_resource.Bucket(s3_path_obj["bucket"]).download_file(s3_path_join(self.txt_vector, s3_path_obj["store_path"], "pages.txt"), file_local_path_in)
        logger.warning("Download pages.txt successfully...")

        logger.info(f"pages.txt download time: {str((time.perf_counter() - start1) * 1000)}")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  按页面 embedding >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  按页面 embedding >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  按页面 embedding >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        start2 = time.perf_counter()

        with open(
                os.path.join(input_folder, "pages.txt"), "r+", encoding='utf-8'
        ) as f_pages, open(
            os.path.join(input_folder, "pages.txt.vector"), "w+", encoding='utf-8'
        ) as f_pages_vector:
            embedding_cache = []
            for line in f_pages:
                if line.strip() == "":
                    continue
                line_obj = json.loads(line)

                embedding_cache.append(line_obj)
                if len(embedding_cache) >= self.chunk_size_page:
                    txt_arr_embedding = self.embed_query([item["sentence"] for item in embedding_cache], chunk_size=self.chunk_size_page)
                    for item_raw, item_emb in zip(embedding_cache, txt_arr_embedding):
                        f_pages_vector.write(json.dumps({
                            "id": item_raw["id"],
                            "page": item_raw["page"],
                            "sentence": item_raw["sentence"],
                            "sentence_vector": item_emb,
                        }, ensure_ascii=False))
                        f_pages_vector.write("\n")
                    embedding_cache = []  # 清空 embedding_cache
                else:
                    continue
            # 处理剩余的 embedding
            if len(embedding_cache) > 0:
                txt_arr_embedding_left = self.embed_query([item["sentence"] for item in embedding_cache], chunk_size=self.chunk_size_page)
                for item_raw, item_emb in zip(embedding_cache, txt_arr_embedding_left):
                    f_pages_vector.write(json.dumps({
                        "id": item_raw["id"],
                        "page": item_raw["page"],
                        "sentence": item_raw["sentence"],
                        "sentence_vector": item_emb,
                    }, ensure_ascii=False))
                    f_pages_vector.write("\n")
                embedding_cache = []  # 清空 embedding_cache

        pages_txt_vector_key = s3_path_join(self.txt_vector, s3_path_obj["store_path"], "pages.txt.vector")
        self.s3_client.upload_file(
            os.path.join(input_folder, "pages.txt.vector"), s3_path_obj["bucket"], pages_txt_vector_key,
            ExtraArgs={"ContentType": ExtenCons.EXTEN_TEXT_TXT_UTF8.value}
        )
        if self.s3_util.check_file_exist(s3_path_obj["bucket"], pages_txt_vector_key) is False:
            raise Exception("[page] Store page result vector failed...")
        logger.warning("[page] Store page result vector successfully...")

        logger.info(f"pages.txt embedding time: {str((time.perf_counter() - start2) * 1000)}")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 提取 block embedding >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 提取 block embedding >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 提取 block embedding >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        start3 = time.perf_counter()

        # 下载 blocks.txt 文件到 input folder
        file_local_path_in = os.path.join(input_folder, "blocks.txt")
        self.s3_resource.Bucket(s3_path_obj["bucket"]).download_file(s3_path_join(self.txt_vector, s3_path_obj["store_path"], "blocks.txt"), file_local_path_in)
        logger.warning("Download blocks.txt successfully...")

        logger.info(f"blocks.txt download time: {str((time.perf_counter() - start3) * 1000)}")

        start4 = time.perf_counter()

        with open(
                os.path.join(input_folder, "blocks.txt"), "r+", encoding='utf-8'
        ) as f_blocks, open(
            os.path.join(input_folder, "blocks.txt.vector"), "w+", encoding='utf-8'
        ) as f_blocks_vector:
            page_data_cache = []
            for line in f_blocks:
                if line.strip() == "":
                    continue
                line_obj = json.loads(line)

                page_data_cache.append(line_obj)
                if len(page_data_cache) >= self.chunk_size_block:  # 每一批满 1000 则进行处理一批
                    txt_arr_embedding = self.embed_query([item["sentence"] for item in page_data_cache], chunk_size=self.chunk_size_block)
                    for _text_block, _item_embedin in zip(page_data_cache, txt_arr_embedding):
                        text_block_obj = {
                            "id": _text_block["id"],
                            "page": _text_block["page"],
                            "seq_no": _text_block["seq_no"],
                            "sentence": _text_block["sentence"],
                            "type": _text_block["type"],
                            "text_location": _text_block["text_location"],
                            "sentence_vector": _item_embedin,
                        }

                        f_blocks_vector.write(json.dumps(text_block_obj, ensure_ascii=False))
                        f_blocks_vector.write("\n")
                    page_data_cache = []  # 清空 embedding_cache

            if len(page_data_cache) > 0:
                txt_arr_embedding = self.embed_query([item["sentence"] for item in page_data_cache], chunk_size=self.chunk_size_block)
                for _text_block, _item_embedin in zip(page_data_cache, txt_arr_embedding):
                    text_block_obj = {
                        "id": _text_block["id"],
                        "page": _text_block["page"],
                        "seq_no": _text_block["seq_no"],
                        "sentence": _text_block["sentence"],
                        "type": _text_block["type"],
                        "text_location": _text_block["text_location"],
                        "sentence_vector": _item_embedin,
                    }

                    f_blocks_vector.write(json.dumps(text_block_obj, ensure_ascii=False))
                    f_blocks_vector.write("\n")
                page_data_cache = []  # 清空 embedding_cache

        blocks_txt_vector_key = s3_path_join(self.txt_vector, s3_path_obj["store_path"], "blocks.txt.vector")
        self.s3_client.upload_file(
            os.path.join(input_folder, "blocks.txt.vector"), s3_path_obj["bucket"], blocks_txt_vector_key,
            ExtraArgs={"ContentType": ExtenCons.EXTEN_TEXT_TXT_UTF8.value}
        )
        if self.s3_util.check_file_exist(s3_path_obj["bucket"], blocks_txt_vector_key) is False:
            raise Exception("[block] Store block result vector failed...")
        logger.warning("[block] Store block result vector successfully...")

        logger.info(f"blocks.txt embedding time: {str((time.perf_counter() - start4) * 1000)}")

    # @retrying.retry(wait_fixed=100, stop_max_attempt_number=10)
    def embed_query(self, query_list: list, chunk_size: int):
        return self.embeddings.embed_documents(query_list, chunk_size=chunk_size)
