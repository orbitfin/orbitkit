from typing import Optional
from orbitkit.pdf_extractor_simple.base import CloudObjectProvider, PdfExtractor
from orbitkit.pdf_extractor_simple.cloud_provider import AwsCloudObjectProvider, OssCloudObjectProvider
from orbitkit.pdf_extractor_simple.core import CorePdfExtract
from orbitkit.pdf_extractor_simple.extractors import PyPdfPdfExtractor, MixedPdfPdfExtractor
from func_timeout import func_timeout, FunctionTimedOut


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
                    auto_upload: bool = True,
                    force_txt_overwrite: bool = False,
                    time_in_sec: int = 60 * 60 * 24):  # Default 24 hrs to timeout

        try:
            return func_timeout(time_in_sec, self.core_pdf_extract.pdf_extract, kwargs={
                "cloud_path": cloud_path,
                "cloud_txt_path": cloud_txt_path,
                "copy_path": copy_path,
                "auto_upload": auto_upload,
                "force_txt_overwrite": force_txt_overwrite,
                "return_txt_list": True,
            })
        except FunctionTimedOut:
            raise Exception(f"Failed to extract pdf with timeout[{str(time_in_sec)}]!")

        # return self.core_pdf_extract.pdf_extract(cloud_path=cloud_path,
        #                                          cloud_txt_path=cloud_txt_path,
        #                                          copy_path=copy_path,
        #                                          auto_upload=auto_upload,
        #                                          force_txt_overwrite=force_txt_overwrite,
        #                                          return_txt_list=True)
