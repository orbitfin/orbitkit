import os
import shutil
import tempfile
from typing import List, Optional
from orbitkit.pdf_extractor_simple.base import CloudObjectProvider, PdfExtractor
from orbitkit.pdf_extractor_simple.cloud_provider import AwsCloudObjectProvider, OssCloudObjectProvider, HttpCloudObjectProvider


class CorePdfExtract:
    cloud_object_provider: CloudObjectProvider = None
    pdf_extractor_list: List[PdfExtractor] = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def _setup_cloud_object_provider(self, cloud_path: str):
        # FIXME: Specific cloud provider could be new() delayed.
        if cloud_path.startswith("s3://"):
            self.cloud_object_provider = AwsCloudObjectProvider(*self.args, **self.kwargs)
            return
        if cloud_path.startswith("oss://"):
            self.cloud_object_provider = OssCloudObjectProvider(*self.args, **self.kwargs)
            return
        if cloud_path.startswith("http://") or cloud_path.startswith("https://"):
            self.cloud_object_provider = HttpCloudObjectProvider(*self.args, **self.kwargs)
            return
        raise Exception("No specific CloudObjectProvider err!")

    def add_pdf_extractor(self, pdf_extractor: PdfExtractor):
        self.pdf_extractor_list.append(pdf_extractor)

    def pdf_extract(self, cloud_path: str,
                    cloud_txt_path: Optional[str] = None,
                    copy_path: Optional[str] = None,
                    auto_upload: bool = True,
                    return_txt_list: bool = False,
                    force_txt_overwrite: bool = False) -> Optional[list]:

        # Supply cloud_path & cloud_txt_path
        self.cloud_path = cloud_path
        if cloud_txt_path is None:
            self.cloud_txt_path = cloud_path + ".txt"
        else:
            self.cloud_txt_path = cloud_txt_path

        # Select CloudObjectProvider by protocol
        self._setup_cloud_object_provider(cloud_path)

        # Create a tmp folder
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Check if the target .txt file exist in cloud
            if force_txt_overwrite is False and self.cloud_object_provider.check_file_exist(self.cloud_txt_path):
                # Exist then download directly: local_path = tmp_dir + '/' + self.cloud_txt_path.split("/")[-1]
                self.cloud_object_provider.download_file(cloud_path=self.cloud_txt_path,
                                                         local_path=tmp_dir,
                                                         filename=self.cloud_txt_path.split("/")[-1])
                final_txt_path = os.path.join(tmp_dir, self.cloud_txt_path.split("/")[-1])
            else:
                # Download pdf itself firstly
                self.cloud_object_provider.download_file(cloud_path=self.cloud_path,
                                                         local_path=tmp_dir,
                                                         filename=self.cloud_path.split("/")[-1])
                # Start to process
                is_extract_success = False
                for pdf_extractor in self.pdf_extractor_list:
                    pdf_extractor.extract(local_path_pdf=os.path.join(tmp_dir, self.cloud_path.split("/")[-1]))
                    if pdf_extractor.do_continue() is False:
                        # 1)mark at least one extractor success & 2)return final txt path & 3)upload txt file
                        is_extract_success = True
                        final_txt_path = pdf_extractor.local_path_pdf_txt
                        if auto_upload:
                            self.cloud_object_provider.upload_file(self.cloud_txt_path, final_txt_path)
                        break
                if is_extract_success is False:
                    raise Exception("Failed to extract pdf with given pdf extractor!")

            # export copy path
            if copy_path:
                shutil.copy(final_txt_path, copy_path)

            # Return list
            txt_content_list = None
            if return_txt_list:
                txt_content_list = []
                with open(final_txt_path, encoding="utf-8") as ft:
                    for line in ft.readlines():
                        txt_content_list.append(line)
                    return txt_content_list
            return txt_content_list
