import time
from orbitkit.file_extractor.exception import ParamsInvalidException, NoProperExtractorFindException
from orbitkit.file_extractor.extractor import FileExtractor
from orbitkit.file_extractor.extractor_txt import FileExtractorTxt
from orbitkit.file_extractor.extractor_pdf import FileExtractorPdf
from orbitkit.file_extractor.extractor_office import FileExtractorOffice
# from orbitkit.file_extractor.extractor_json import FileExtractorJson
from orbitkit.file_extractor.extractor_html import FileExtractorHtml


class FileDispatcher:
    def __init__(self, extractor_config=None):
        self.validate_params(extractor_config=extractor_config)
        self.extractor_config = extractor_config

    def init_extractor(self, file_obj):
        file_extractor = None
        file_type = str(file_obj['file_type']).lower()

        # 根据类型初始化文件提取器
        if file_type in ['txt']:
            file_extractor = FileExtractorTxt()
        if file_type in ['pdf']:
            file_extractor = FileExtractorPdf()
        if file_type in ['doc', 'docx', 'xls', 'xlsx']:
            file_extractor = FileExtractorOffice()
        # if file_type in ['json']:
        #     file_extractor = FileExtractorJson()
        if file_type in ['html', 'htm']:
            file_extractor = FileExtractorHtml()

        # extractor should not be None
        if file_extractor is None:
            raise NoProperExtractorFindException()

        # Configure extractor
        file_extractor.config_extractor(extractor_config=self.extractor_config, file_obj=file_obj)
        return file_extractor

    @staticmethod
    def get_params_template():
        return {
            'published': time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
            'text': '',
            'store_path': '',
            'file_name': '',
            'file_type': '',
            'bucket': '',
            'status': 'pending',
            'reason': 'Pending to process.'
        }

    def validate_params(self, extractor_config):
        if extractor_config is None:
            raise ParamsInvalidException()
