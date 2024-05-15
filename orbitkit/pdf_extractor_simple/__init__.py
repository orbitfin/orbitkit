from typing import Optional
from orbitkit.pdf_extractor_simple.base import CloudObjectProvider, PdfExtractor
from orbitkit.pdf_extractor_simple.cloud_provider import AwsCloudObjectProvider, OssCloudObjectProvider
from orbitkit.pdf_extractor_simple.core import CorePdfExtract
from orbitkit.pdf_extractor_simple.extractors import PyPdfPdfExtractor, MixedPdfPdfExtractor


class ExtractPdfSimpleTxtByCloud:
    def __init__(self, skip_ocr_exceed_page=0, *args, **kwargs):
        self.core_pdf_extract = CorePdfExtract(*args, **kwargs)
        # Add extractor
        self.core_pdf_extract.add_pdf_extractor(MixedPdfPdfExtractor(issue_page_per=95,
                                                                     skip_ocr_exceed_page=skip_ocr_exceed_page))

    def pdf_extract(self,
                    cloud_path: str,
                    cloud_txt_path: Optional[str] = None,
                    copy_path: Optional[str] = None,
                    auto_upload: bool = True):
        return self.core_pdf_extract.pdf_extract(cloud_path=cloud_path,
                                                 cloud_txt_path=cloud_txt_path,
                                                 copy_path=copy_path,
                                                 auto_upload=auto_upload, return_txt_list=True)
