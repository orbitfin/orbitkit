import re
from orbitkit.file_extractor.extractor import FileExtractor


class FileExtractorHtml(FileExtractor):
    def __init__(self):
        super().__init__()

    def remove_all_tags(self, with_tag):
        """
        :param with_tag:
        :return:
        """
        return str(re.sub(r'<.*?>', ' ', with_tag))

    def extract(self):
        file_obj = self.file_obj

        file_type = file_obj['file_type']
        bucket_name = file_obj['bucket']
        key = file_obj['store_path']
        file_name = file_obj['file_name']

        try:
            response = self.s3.get_object(Bucket=bucket_name, Key=key)
            contents_byte = response['Body'].read()
            try:
                contents = contents_byte.decode('utf-8')
            except:
                contents = contents_byte.decode('latin-1')

            text = self.remove_all_tags(str(contents).strip())

            file_obj['text'] = text
            file_obj['status'] = 'success'
            file_obj['reason'] = 'Extract text successfully!'
        except Exception as e:
            file_obj['text'] = ''
            file_obj['status'] = 'failed'
            file_obj['reason'] = str(e)

        return file_obj
