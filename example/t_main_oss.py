import os
import time

os.environ["OSSAPPID"] = ''
os.environ["OSSPWD"] = ''
os.environ["OSSENDPOINT"] = ''

from pdf_extractor_simple import ExtractPdfSimpleTxtByCloud
from pdf_extractor_simple.extractors import PyPdfPdfExtractor, MixedPdfPdfExtractor

if __name__ == "__main__":
    with open('./oss_path_file.txt', 'r') as file:
        oss_path_list = [line.strip() for line in file]

    start_time = time.time()
    for index, path in enumerate(oss_path_list, start=1):
        print(f"-------- {index} --------")
        cloud_path = path
        copy_path = './test_pdf/test_txt_folder/' + path.split('/')[-1] + '.txt'
        print(cloud_path)
        if os.path.exists(copy_path):
            print(f"{copy_path} 文件已经存在")
            continue
        extract_pdf_simple_txt_by_cloud = ExtractPdfSimpleTxtByCloud(cloud_path=path)
        extract_pdf_simple_txt_by_cloud.add_pdf_extractor(PyPdfPdfExtractor())
        extract_pdf_simple_txt_by_cloud.add_pdf_extractor(MixedPdfPdfExtractor(issue_page_per=95))
        extract_pdf_simple_txt_by_cloud.pdf_extract(copy_path=copy_path, auto_upload=False)
    print(f"--- {time.time() - start_time} seconds ---")
