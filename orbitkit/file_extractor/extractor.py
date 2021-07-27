import boto3


class FileExtractor(object):
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.textract_client = boto3.client('textract')
        self.extract_url = None

    def extract(self, file_obj):
        raise Exception('No implement exception!')

    def set_extract_url(self, extract_url):
        self.extract_url = extract_url
