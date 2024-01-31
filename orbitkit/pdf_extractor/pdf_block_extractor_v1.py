import time
from typing import Optional, List
from orbitkit import id_srv
from orbitkit.pdf_extractor.pdf_block_extractor_base import PdfBlockExtractBase
import logging

try:
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer, LTFigure, LTChar
    import pdfplumber
    from Crypto.Cipher import AES
except ImportError:
    raise ValueError(
        "Please install below packages before using PDF Extractor function.\n"
        "- pdfminer.six\n"
        "- pdfplumber >= 0.9.0\n"
        "- pycryptodome >= 3.11.0"
    )

logger = logging.getLogger(__name__)

"""
>>> 注意事项 <<<
pdfminer.six page 索引是从 1 开始的
pdfplumber page 索引是从 0 开始的
本程序的索引是从 1 开始的
"""


class PdfBlockExtractV1(PdfBlockExtractBase):
    def __init__(self, local_path: str, extend_meta: dict, pages: Optional[List[int]] = None):
        self.local_path = local_path
        self.pages = pages
        self.extend_meta = extend_meta
        self.sentence_list = []

    @classmethod
    def from_local_file(cls, local_path: str, extend_meta: dict, pages: Optional[List[int]] = None):
        return cls(local_path, extend_meta, pages)

    def loop_pages(self, page_layout):
        index = 1
        sentence_list_page = []
        for element in page_layout:
            # 如果页面的元素是 LTTextContainer 则直接拿数据
            if isinstance(element, LTTextContainer):
                sentence = element.get_text()
                # Filter sentence
                sentence_obj = self._sentence_filter(sentence)
                if sentence_obj['is_valid_sentence'] is False:
                    continue
                sentence = sentence_obj['sentence']

                _txt_data = {
                    "id": f"l_{id_srv.get_random_short_id()}",
                    "page": str(page_layout.pageid),
                    "seq_no": str(index),
                    "sentence": sentence,
                    "type": "sentence",
                    "text_location": {
                        "location": [[element.x0, element.y1, element.x1, element.y0]]
                    }
                }
                _txt_data.update(self.extend_meta)  # 合并额外信息
                sentence_list_page.append(_txt_data)
                index += 1

            # 如果页面的元素是 LTFigure 则拼接字符拿数据
            if isinstance(element, LTFigure):
                sentence_item = ''
                x0_list = []
                y1_list = []
                x1_list = []
                y0_list = []
                location = []
                for item in element:
                    if isinstance(item, LTChar):
                        sentence_item += item.get_text()
                        x0_list.append(item.x0)
                        y1_list.append(item.y1)
                        x1_list.append(item.x1)
                        y0_list.append(item.y0)

                # PDF 可能有空页情况, 或者某一页没提取出坐标 min max 报错
                if len(x0_list) > 0 and len(y1_list) > 0 and len(x1_list) > 0 and len(y0_list) > 0:
                    location.append(min(x0_list))
                    location.append(max(y1_list))
                    location.append(max(x1_list))
                    location.append(min(y0_list))

                    # Filter sentence
                    sentence_obj = self._sentence_filter(sentence_item)
                    if sentence_obj['is_valid_sentence'] is False:
                        continue
                    sentence = sentence_obj['sentence']

                    _txt_data = {
                        "id": f"l_{id_srv.get_random_short_id()}",
                        "page": str(page_layout.pageid),
                        "seq_no": str(index),
                        "sentence": sentence,
                        "type": "sentence",
                        "text_location": {
                            "location": [location]}
                    }
                    _txt_data.update(self.extend_meta)  # 合并额外信息
                    sentence_list_page.append(_txt_data)
                    index += 1

            # 如果两个 if 都匹配不上则说明此 element 没有数据
            pass

        # 最后返回当页的提取结果
        return sentence_list_page

    def extract(self):
        """入口方法
        可以根据 specific_page 选择是提取单独一页的数据还是全部解析
        """
        start_extract_time = time.perf_counter()
        logger.warning('Start extract pdf...')

        page_layouts = extract_pages(self.local_path)
        # 解析单独一页数据
        if self.pages:
            for page_layout in page_layouts:
                if page_layout.pageid in self.pages:
                    ordered_sentence_list_page = self.loop_pages(page_layout)
                    # 合并入到总的列表中
                    self.sentence_list.extend(ordered_sentence_list_page)
        else:
            # 解析所有页面
            for page_layout in page_layouts:
                ordered_sentence_list_page = self.loop_pages(page_layout)
                # 合并入到总的列表中
                self.sentence_list.extend(ordered_sentence_list_page)

        end_extract_time = time.perf_counter() - start_extract_time
        logger.warning(f'End extract pdf with cost time {str(end_extract_time * 1000)}')

        return self.sentence_list

    def extract_iter(self):
        """入口方法
        可以根据 specific_page 选择是提取单独一页的数据还是全部解析
        """
        start_extract_time = time.perf_counter()
        logger.warning('Start extract pdf...')

        page_layouts = extract_pages(self.local_path)
        # 解析单独一页数据
        if self.pages:
            for page_layout in page_layouts:
                if page_layout.pageid in self.pages:
                    yield self.loop_pages(page_layout)
        else:
            # 解析所有页面
            for page_layout in page_layouts:
                yield self.loop_pages(page_layout)

        end_extract_time = time.perf_counter() - start_extract_time
        logger.warning(f'End extract pdf with cost time {str(end_extract_time * 1000)}')
