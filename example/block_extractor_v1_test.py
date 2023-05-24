from pdfminer.high_level import extract_pages
from pdf_extractor.pdf_block_extractor_v1 import PdfBlockExtractV1
import tracemalloc

'''
new-SkyWestESGReport2022.pdf
8A88035B38A6655EBCD68F608A59A27D.pdf
'''

tracemalloc.start()

page_layouts = extract_pages('8A88035B38A6655EBCD68F608A59A27D.pdf')

pdf_block_extract = PdfBlockExtractV1(local_path='8A88035B38A6655EBCD68F608A59A27D.pdf', extend_meta={})
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


def calc_memory(page):
    # tracemalloc.start()

    pdf_block_extract = PdfBlockExtractV1(local_path='8A88035B38A6655EBCD68F608A59A27D.pdf', extend_meta={}, pages=[page])
    text_block_arr = pdf_block_extract.extract()
    pdf_block_extract = None

    for item in text_block_arr:
        print(item)

    # pdf_block_extract = PdfBlockExtractV1(local_path='8A88035B38A6655EBCD68F608A59A27D.pdf', extend_meta={}, pages=[page])
    # text_block_arr = pdf_block_extract.extract()
    #
    # for item in text_block_arr:
    #     print(item)

    # current, peak = tracemalloc.get_traced_memory()
    # print(f"Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB.")
    #
    # tracemalloc.stop()


if __name__ == '__main__':
    pass
    # pages = PdfBlockExtractV1.get_pdf_pages('8A88035B38A6655EBCD68F608A59A27D.pdf')
    # print(pages)

    # for ind in range(1, 97):
    #     print(f"Start calc [{str(ind)}] info...")
    #     calc_memory(ind)
