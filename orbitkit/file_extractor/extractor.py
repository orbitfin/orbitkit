import signal
import copy
import boto3
import abc
from orbitkit.file_extractor.exception import FileExtractorTimeoutException
from orbitkit.file_extractor.util import timeout_handler


class FileExtractor(metaclass=abc.ABCMeta):
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.textract_client = boto3.client('textract')
        self.extract_url = None
        self.file_obj = None

    @abc.abstractmethod
    def extract(self):
        raise NotImplementedError("No implement exception!")

    def extract_timeout(self, timeout=60 * 10):
        file_obj = self.file_obj

        print('Start to extract file with timeout')

        store_data_copy = copy.deepcopy(file_obj)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)

            store_data_copy = self.extract()

            signal.alarm(0)
        except FileExtractorTimeoutException as ret:
            store_data_copy['status'] = 'failed'
            store_data_copy['reason'] = str(ret)
        except Exception as ret:
            store_data_copy['status'] = 'failed'
            store_data_copy['reason'] = str(ret)

        print('End to extract file with timeout')

        return store_data_copy

    def config_extractor(self, extractor_config, file_obj):
        self.extract_url = extractor_config['extract_url']
        self.s3 = boto3.client('s3',
                               aws_access_key_id=extractor_config['aws_access_key_id'],
                               aws_secret_access_key=extractor_config['aws_secret_access_key'])
        self.textract_client = boto3.client('textract',
                                            aws_access_key_id=extractor_config['aws_access_key_id'],
                                            aws_secret_access_key=extractor_config['aws_secret_access_key'])
        # Set file info
        self.file_obj = file_obj
