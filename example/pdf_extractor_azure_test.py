import sys
from os.path import abspath, dirname
import logging

BASE_DIR = dirname(dirname(abspath(__file__)))  # /orbitkit
sys.path.insert(0, BASE_DIR)

from orbitkit.pdf_extractor.pdf_extractor_azure import PdfExtractorAzure

logging.basicConfig(level=logging.INFO)


def extract_pdf_from_s3(s3_path: str):
    pdf_extractor = PdfExtractorAzure(s3_path=s3_path,
                                      txt_vector="",
                                      aws_access_key_id="",
                                      aws_secret_access_key="",
                                      azure_doc_intelligence_endpoint="",
                                      azure_doc_intelligence_key="")

    pdf_extractor.extract()


if __name__ == "__main__":
    extract_list = [
        "s3://orbit-common-resources/pdf-test/202105310903058865590189.pdf",
    ]

    for item in extract_list:
        extract_pdf_from_s3(s3_path=item)
