import abc


class CloudObjectProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def check_file_exist(self, cloud_path: str) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def download_file(self, cloud_path: str, local_path: str, filename: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def upload_file(self, cloud_path: str, local_path: str):
        raise NotImplementedError()


class PdfExtractor(metaclass=abc.ABCMeta):
    def __init__(self):
        self.local_path_pdf_txt = ""
        self.exception_exist = False

    @abc.abstractmethod
    def extract(self, local_path_pdf: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def do_continue(self) -> bool:
        raise NotImplementedError()
