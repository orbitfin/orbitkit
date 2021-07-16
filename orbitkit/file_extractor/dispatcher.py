import time
import signal
import copy
import os
from file_extractor.exception import ParamsInvalidException, FileExtractorTimeoutException
from file_extractor.extractor import FileExtractor
from file_extractor.extractor_txt import FileExtractorTxt
from file_extractor.extractor_pdf import FileExtractorPdf
from file_extractor.extractor_office import FileExtractorOffice
from file_extractor.extractor_json import FileExtractorJson
from file_extractor.util import timeout_handler


class FileDispatcher(object):
    file_extractor: FileExtractor = None
    file_obj = None

    def __init__(self, file_obj):
        self.validate_params()

        self.file_obj = file_obj
        self.file_type = file_obj['file_type']

        if self.file_type in ['txt']:
            self.file_extractor = FileExtractorTxt()
        if self.file_type in ['pdf']:
            self.file_extractor = FileExtractorPdf()
        if self.file_type in ['doc', 'docx', 'xls', 'xlsx']:
            self.file_extractor = FileExtractorOffice()
        if self.file_type in ['json']:
            self.file_extractor = FileExtractorJson()

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

    def to_extract(self):
        print('Start to extract file')

        return self.file_extractor.extract(self.file_obj)

    def to_extract_timeout(self, timeout=60 * 10):
        print('Start to extract file with timeout')

        store_data_copy = copy.deepcopy(self.file_obj)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

            store_data_copy = self.file_extractor.extract(self.file_obj)

            signal.alarm(0)
        except FileExtractorTimeoutException as ret:
            store_data_copy['status'] = 'failed'
            store_data_copy['reason'] = str(ret)
        except Exception as ret:
            store_data_copy['status'] = 'failed'
            store_data_copy['reason'] = str(ret)

        print('End to extract file with timeout')

        return store_data_copy

    def validate_params(self):
        pass
        # try:
        #     os.environ['extract_url']
        # except Exception as e:
        #     raise ParamsInvalidException('Params invalid exception')
