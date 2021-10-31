from orbitkit.file_extractor.extractor import FileExtractor
import json
import requests


class FileExtractorOffice(FileExtractor):
    def __init__(self):
        super().__init__()

    def extract(self):
        file_obj = self.file_obj

        file_type = file_obj['file_type']
        bucket_name = file_obj['bucket']
        key = file_obj['store_path']
        file_name = file_obj['file_name']

        headers = {'Content-Type': 'application/json'}
        pay_load = json.dumps({'bucket': bucket_name, 'key': key})
        res = requests.post(url=self.extract_url, headers=headers, data=pay_load)
        if res.status_code == 200:
            data = res.json()
            text = data['body']

            file_obj['text'] = text
            file_obj['status'] = 'success'
            file_obj['reason'] = 'Extract office type file successfully!'
        else:
            file_obj['text'] = ''
            file_obj['status'] = 'failed'
            file_obj['reason'] = str(res)

        return file_obj
