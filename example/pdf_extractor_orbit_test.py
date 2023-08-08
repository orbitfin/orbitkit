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
        try:
            pdf_extractor = PdfExtractor(s3_path=s3_path,
                                         txt_vector="")

            pdf_extractor.extract()
        except TooManyPagesException as e:
            print(e.detail)
        except CidEncryptionException as e:
            print(e.detail)
        except OcrBrokenException as e:
            print(e.detail)
        except Exception as e:
            print(e)


def extract_pdf_from_s3(s3_path: str):
    pdf_extractor = PdfExtractor(s3_path=s3_path,
                                 txt_vector="",
                                 aws_access_key_id="",
                                 aws_secret_access_key="")

    pdf_extractor.extract()


if __name__ == "__main__":
    # extract_pdf_from_s3(s3_path="example.pdf")
    pass
