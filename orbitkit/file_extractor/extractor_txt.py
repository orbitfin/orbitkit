from orbitkit.file_extractor.extractor import FileExtractor


class FileExtractorTxt(FileExtractor):
    def __init__(self):
        super().__init__()

    def extract(self, file_obj):
        file_type = file_obj['file_type']
        bucket_name = file_obj['bucket']
        key = file_obj['store_path']
        file_name = file_obj['file_name']

        try:
            response = self.s3.get_object(Bucket=bucket_name, Key=key)
            contents = response['Body'].read()
            text = str(contents, encoding="utf8")

            file_obj['text'] = text
            file_obj['status'] = 'success'
            file_obj['reason'] = 'Extract text successfully!'
        except Exception as e:
            file_obj['text'] = ''
            file_obj['status'] = 'failed'
            file_obj['reason'] = str(e)

        return file_obj
