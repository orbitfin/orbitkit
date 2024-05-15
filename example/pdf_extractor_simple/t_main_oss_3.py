import json
import os
import logging

logging.basicConfig(level=logging.INFO)

os.environ["OSSAPPID"] = ''
os.environ["OSSPWD"] = ''
os.environ["OSSENDPOINT"] = ''

from orbitkit.pdf_extractor_simple import ExtractPdfSimpleTxtByCloud

if __name__ == "__main__":
    extract_pdf_simple_txt_by_cloud = ExtractPdfSimpleTxtByCloud(skip_ocr_exceed_page=100)

    # 读取环境变量中的OSSAPPID, OSSPWD, OSSENDPOINT
    # cloud_path：远程地址
    # cloud_txt_path：提取完成文件的远程存放地址（可选参数，默认存放地址为cloud_path同级目录）
    # copy_path：提取完成文件本地地址（可选参数）
    # auto_upload：提取完成文件是否上传远程（可选参数，默认为True）
    txt_content = extract_pdf_simple_txt_by_cloud.pdf_extract(cloud_path="oss://edidata/report/cninfo/705001-138796.pdf",
                                                              auto_upload=False)

    # txt_content提取完成数据列表 [{'page_no': '1', 'text': 'zzz'},{'page_no': '2', 'text': 'xxx'}]
    if txt_content:
        for item in txt_content:
            print(json.loads(item))
