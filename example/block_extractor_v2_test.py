import sys
from os.path import abspath, dirname

BASE_DIR = dirname(dirname(abspath(__file__)))  # /orbitkit
sys.path.insert(0, BASE_DIR)

from orbitkit.pdf_extractor.pdf_block_extractor_v2 import PdfBlockExtractV2


def extract_pdf(path: str):
    """
    直接提取 PDF 的 block，适合比较小的 PDF
    """

    pdf_block_extract = PdfBlockExtractV2(local_path=path, extend_meta={})
    text_block_arr = pdf_block_extract.extract()
    pdf_block_extract = None

    for item in text_block_arr:
        print(item)


def extract_pdf_extract_iter(path: str):
    """
    通过迭代器提取 PDF 的 block，适合比较大的 PDF，
    代码中有内存监控，可能速度会稍慢
    """

    import tracemalloc

    tracemalloc.start()

    pdf_block_extract = PdfBlockExtractV2(local_path=path, extend_meta={})
    pdf_block_extract_gen = pdf_block_extract.extract_iter()
    while True:
        try:
            page_data = next(pdf_block_extract_gen)

            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB.")

            for item in page_data:
                print(item)
        except StopIteration as e:
            print('End fetching docs')
            break

    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB.")

    tracemalloc.stop()


if __name__ == '__main__':
    # extract_pdf(path='example.pdf')
    # extract_pdf_extract_iter(path='example.pdf')
    pass
