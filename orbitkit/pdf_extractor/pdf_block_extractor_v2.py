import time
from typing import Optional, List, Union
import logging
from orbitkit import id_srv
from prettytable import PrettyTable
from orbitkit.pdf_extractor.pdf_block_extractor_base import PdfBlockExtractBase

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

"""方法说明：
>>> 安装包 <<<
pip install pdfplumber # pdfplumber 是基于 pdfminer.six 的，安装这个包的同时也会安装 pdfminer.six
pip install pycryptodome # 有些 pdf 是加密的，可以通过这个包进行有效的解密

>>> 思路说明 <<<
通过 pdfplumber 和 pdfminer.six 同时提取文字，如果在一个 page 上如果有表格信息，
则在将 pdfminer.six 提取的 block 信息去表格中找，如果存在表格中，则去掉这条信息。

>>> 注意事项 <<<
pdfminer.six page 索引是从 1 开始的
pdfplumber page 索引是从 0 开始的
本程序的索引是从 1 开始的
"""


class PdfBlockExtractV2(PdfBlockExtractBase):
    def __init__(self, local_path: str, extend_meta: dict, pages: Optional[List[int]] = None):
        # 最终的句子列表（带有坐标）
        self.sentence_list = []
        self.local_path = local_path
        self.pages = pages
        self.extend_meta = extend_meta
        self.pdf_plumber = pdfplumber.open(self.local_path)
        self.pdf_plumber_pages = self.pdf_plumber.pages

    @classmethod
    def from_local_file(cls, local_path: str, extend_meta: dict, pages: Optional[List[int]] = None):
        return cls(local_path, extend_meta, pages)

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

        logger.warning(f'End extract pdf with cost time {str((time.perf_counter() - start_extract_time) * 1000)}')

    def loop_pages(self, page_layout):
        """处理单独一页的数据
        1. 通过 pdfplumber 提取表格信息
        2. 通过 pdfminer 提取文本 block 信息
        """
        logger.info(f"Start inspect page {str(page_layout.pageid)}...")

        sentence_list_page = []
        # 尝试得到每一页的表格
        pdf_plumber_page = self.pdf_plumber_pages[page_layout.pageid - 1]
        '''
        https://github.com/jsvine/pdfplumber/issues/193
        Memory issues on very large PDFs
        
        I found that after extracting text, the lru_cache was somehow not being cleared causing the memory to keep filling up and eventually run out of it. After some playing around I found the following code helped me. In the code below, I am clearing the page cache and the lru cache.
        with pdfplumber.open("path-to-pdf/my.pdf") as pdf:
            for page in pdf.pages:
            text = page.extract_text(layout=True)
            page.flush_cache()
        
           # This was the fn where cache is implemented
           page.get_text_layout.cache_clear()     `
        PS: I am currently using pdfplumber version 0.71. I hope this helps someone.
        '''
        tables = pdf_plumber_page.extract_tables()
        pdf_plumber_page.flush_cache()

        # 过滤无用表格，并构建表格扩展对象
        tables_obj = self._filter_extend_tables(tables)

        # 遍历页面所有的元素开始解析
        index = 1
        for element in page_layout:
            # 如果页面的元素是 LTTextContainer 则直接拿数据
            if isinstance(element, LTTextContainer):
                sentence = element.get_text()

                # 如果 sentence 为空字符串，则本条数据没有意义
                if sentence.strip() == '':
                    continue

                # If element in table，则统一处理本页的 table
                if len(tables_obj) > 0:
                    is_exist_in_table = self._element_in_table(element, index, tables_obj)
                    if is_exist_in_table:
                        index += 1
                        continue

                # Filter sentence
                sentence_obj = self._sentence_filter(sentence)
                if sentence_obj['is_valid_sentence'] is False:
                    index += 1
                    continue
                sentence = sentence_obj['sentence']

                # 开始组装信息
                _txt_data = {
                    "id": f"l_{id_srv.get_random_short_id()}",
                    "page": page_layout.pageid,
                    "seq_no": index,
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
            # 一般出现在 LTFigure 的数据没有表格信息
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
                        index += 1
                        continue
                    sentence = sentence_obj['sentence']

                    # 开始组装信息
                    _txt_data = {
                        "id": f"l_{id_srv.get_random_short_id()}",
                        "page": page_layout.pageid,
                        "seq_no": index,
                        "sentence": sentence,
                        "type": "sentence",
                        "text_location": {
                            "location": [location]
                        }
                    }
                    _txt_data.update(self.extend_meta)  # 合并额外信息
                    sentence_list_page.append(_txt_data)
                    index += 1

            # 如果两个 if 都匹配不上则说明此 element 没有数据
            pass

        # 所有元素解析完毕后，开始解析 table
        # - sentence_list_page 当前页面所有过滤后的文本 block（table 过滤，其他过滤）
        # - tables_obj 当前页所有 table 信息
        for item_table in tables_obj:
            if len(item_table['x0_list']) <= 0 \
                    or len(item_table['y1_list']) <= 0 \
                    or len(item_table['x1_list']) <= 0 \
                    or len(item_table['y0_list']) <= 0:
                continue
            item_table['location'].append(min(item_table['x0_list']))
            item_table['location'].append(max(item_table['y1_list']))
            item_table['location'].append(max(item_table['x1_list']))
            item_table['location'].append(min(item_table['y0_list']))

            # 合并进入 sentence_list_page
            _txt_data = {
                "id": f"l_{id_srv.get_random_short_id()}",
                "page": page_layout.pageid,
                "seq_no": min(item_table['index_set']),
                "sentence": self._get_html_table_format(item_table['table']),
                "type": "table",
                "text_location": {
                    "location": [item_table['location']]
                }
            }
            _txt_data.update(self.extend_meta)  # 合并额外信息
            sentence_list_page.append(_txt_data)

        # 最后对新的 sentence_list_page 进行排序
        ordered_sentence_list_page = sorted(sentence_list_page, key=lambda item_sen: item_sen['seq_no'])
        # 重新设置顺序信息
        for ind, item in enumerate(ordered_sentence_list_page):
            item['seq_no'] = ind + 1

        # 合并入到总的列表中
        return ordered_sentence_list_page

    def _element_in_table(self, element: Union[LTTextContainer], index: int, tables_obj):
        is_exist_in_table = False
        for table_info in tables_obj:
            if element.get_text().strip() in table_info['values_set']:
                is_exist_in_table = True
                table_info['index_set'].append(index)
                table_info['x0_list'].append(element.x0)
                table_info['y1_list'].append(element.y1)
                table_info['x1_list'].append(element.x1)
                table_info['y0_list'].append(element.y0)
                # break
        return is_exist_in_table

    def _filter_extend_tables(self, tables: List[List[List[Optional[str]]]]):
        """对 table 信息进行扩展
        table_info = {
            'x0_list': [],
            'y1_list': [],
            'x1_list': [],
            'y0_list': [],
            'table': [], # 得到去掉 None 信息后的 table
            'values_set': {}, # 得到 table 数据的去重集合（没有 "" 数据）
            'index_set': [], # 如果某条数据在 table 中，则将本条数据的 index 也设置进来，最小的 index 则是当前 table 的 index
            'location': [], # 预留，最后计算 table 的 location 信息
        }
        """
        if len(tables) <= 0:
            return []

        tables_obj = []
        for table in tables:
            # 处理每一个 table 的信息
            table_info = {
                'x0_list': [],
                'y1_list': [],
                'x1_list': [],
                'y0_list': [],
                'table': [],
                'index_set': [],
                'values_set': {},
                'location': [],
            }
            # 遍历一个表格，将 None 都转换成 ''
            table_converted = []
            for ind, row in enumerate(table):
                table_converted.append(['' if cell is None else cell for cell in row])
            table_info['table'] = table_converted

            # 打平 table 并得到关键词列表
            values_set = set()
            for ind, row in enumerate(table_converted):
                for cell in row:
                    if cell.strip() != '':
                        values_set.add(cell.strip())
            table_info['values_set'] = values_set

            # 判断 table 中是否有有效数据
            # values_set_copy = copy.deepcopy(values_set)
            # valid_table_flag = False
            # for item in values_set_copy:
            #     if item.strip() != '':
            #         valid_table_flag = True
            #         break
            #
            # if valid_table_flag:
            #     tables_obj.append(table_info)

            # 判断 table 中是否有有效数据
            if len(values_set) > 0:
                tables_obj.append(table_info)

        return tables_obj

    def _get_html_table_format(self, table):
        tb = PrettyTable()
        for row in table:
            tb.add_row(row)

        return tb.get_html_string(header=False)
