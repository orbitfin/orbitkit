import sys
from os.path import abspath, dirname
import logging
from typing import List

BASE_DIR = dirname(dirname(abspath(__file__)))  # /orbitkit
sys.path.insert(0, BASE_DIR)

from orbitkit.pdf_extractor.pdf_extractor_orbit import PdfExtractor
from orbitkit.pdf_extractor.exceptions import TooManyPagesException, CidEncryptionException, OcrBrokenException

logging.basicConfig(level=logging.INFO)


def extract_pdf_list_example(s3_list: List):
    for s3_path in s3_list:
        extract_pdf_one_example(s3_path=s3_path)


def extract_pdf_one_example(s3_path: str):
    try:
        pdf_extractor = PdfExtractor(s3_path=s3_path,
                                     txt_vector="",
                                     page_and_block="both",
                                     aws_access_key_id="",
                                     aws_secret_access_key="")

        pdf_extractor.extract()
    except TooManyPagesException as e:
        print(e.detail)
    except CidEncryptionException as e:
        print(e.detail)
    except OcrBrokenException as e:
        print(e.detail)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    # Test list
    s3_path_list = []
    extract_pdf_list_example(s3_list=s3_path_list)

    # Test one
    # extract_pdf_one_example(s3_path="s3://orbit-common-resources/pdf-test/202105310903058865590189.pdf")

    pass
