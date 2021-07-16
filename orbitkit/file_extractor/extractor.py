import boto3
import os


class FileExtractor(object):
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.textract_client = boto3.client('textract')

        self.extract_url = ""
        raise Exception('Not implement exception FIXME')

    def extract(self, file_obj):
        raise Exception('No implement exception!')
