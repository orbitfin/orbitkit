from pdf_extractor.pdf_block_extractor_v2 import PdfBlockExtractV2
import tracemalloc

'''
new-SkyWestESGReport2022.pdf
8A88035B38A6655EBCD68F608A59A27D.pdf
'''

# tracemalloc.start()

pdf_block_extract = PdfBlockExtractV2(local_path='new-SkyWestESGReport2022.pdf', extend_meta={})
text_block_arr = pdf_block_extract.extract()
pdf_block_extract = None

for item in text_block_arr:
    print(item)

# pdf_block_extract = PdfBlockExtractV2(local_path='8A88035B38A6655EBCD68F608A59A27D.pdf', extend_meta={})
# pdf_block_extract_gen = pdf_block_extract.extract_iter()
# while True:
#     try:
#         page_data = next(pdf_block_extract_gen)
#
#         current, peak = tracemalloc.get_traced_memory()
#         print(f"Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB.")
#
#         # for item in page_data:
#         #     print(item)
#     except StopIteration as e:
#         print('End fetching docs')
#         break

# current, peak = tracemalloc.get_traced_memory()
# print(f"Current memory usage is {current / 10 ** 6}MB, Peak was {peak / 10 ** 6}MB.")
#
# tracemalloc.stop()

if __name__ == '__main__':
    pass
    # pages = PdfBlockExtractV2.get_pdf_pages('8A88035B38A6655EBCD68F608A59A27D.pdf')
    # print(pages)

    # for ind in range(1, 97):
    #     print(f"Start calc [{str(ind)}] info...")
    #     calc_memory(ind)
