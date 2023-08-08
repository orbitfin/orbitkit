from pdfminer.high_level import extract_pages
from pdf_extractor.pdf_block_extractor_v1 import PdfBlockExtractV1
import tracemalloc


def extract_pdf_extract_iter():
    tracemalloc.start()

    pdf_block_extract = PdfBlockExtractV1(local_path='example.pdf', extend_meta={})
    pdf_block_extract_gen = pdf_block_extract.extract_iter()
    while True:
        try:
            page_data = next(pdf_block_extract_gen)

            current, peak = tracemalloc.get_traced_memory()
            print(f"Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB.")

            # for item in page_data:
            #     print(item)
        except StopIteration as e:
            print('End fetching docs')
            break

    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB.")

    tracemalloc.stop()


def extract_pdf(page):
    tracemalloc.start()

    pdf_block_extract = PdfBlockExtractV1(local_path='example.pdf', extend_meta={}, pages=[page])
    text_block_arr = pdf_block_extract.extract()
    pdf_block_extract = None

    for item in text_block_arr:
        print(item)

    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB.")

    tracemalloc.stop()


if __name__ == '__main__':
    # extract_pdf()
    # extract_pdf_extract_iter()
    pass
