import json
import os
import time

os.environ["OSSAPPID"] = ''
os.environ["OSSPWD"] = ''
os.environ["OSSENDPOINT"] = ''

from orbitkit.pdf_extractor_simple import ExtractPdfSimpleTxtByCloud

if __name__ == "__main__":
    with open('oss_path_file.txt', 'r') as file:
        oss_path_list = [line.strip() for line in file]

    extract_pdf_simple_txt_by_cloud = ExtractPdfSimpleTxtByCloud()

    start_time = time.time()
    for index, path in enumerate(oss_path_list, start=1):
        print(f"-------- {index} --------")
        cloud_path = path
        copy_path = './test_txt_folder/' + path.split('/')[-1] + '.txt'
        print(cloud_path)
        if os.path.exists(copy_path):
            print(f"{copy_path} 文件已经存在")
            continue

        txt_content = extract_pdf_simple_txt_by_cloud.pdf_extract(cloud_path=path, auto_upload=False)

        if txt_content:
            for item in txt_content:
                print(json.loads(item))

    print(f"--- {time.time() - start_time} seconds ---")
