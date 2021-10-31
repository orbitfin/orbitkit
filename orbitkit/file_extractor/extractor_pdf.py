import json
import requests
from orbitkit.file_extractor.extractor import FileExtractor


class FileExtractorPdf(FileExtractor):
    def __init__(self):
        super().__init__()

    def extract(self):
        file_obj = self.file_obj

        file_type = file_obj['file_type']
        bucket_name = file_obj['bucket']
        key = file_obj['store_path']
        file_name = file_obj['file_name']

        # Start to calc
        text = ''
        pdf_ex = 'pdf no content err!'
        headers = {'Content-Type': 'application/json'}
        pay_load = json.dumps({'bucket': bucket_name, 'key': key})
        res = requests.post(url=self.extract_url, headers=headers, data=pay_load)
        if res.status_code == 200:
            data = res.json()
            text = data['body']

        if not text or not text.strip() or res.status_code != 200:
            # process using S3 object
            response = self.textract_client.start_document_text_detection(
                DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': key}}
            )

            # Get the text blocks
            job_id = response['JobId']
            try:
                text = self.get_detected_text(job_id)
            except Exception as ex:
                pdf_ex = str(ex)
                text = ''

        if text.strip() == '':
            file_obj['text'] = ''
            file_obj['status'] = 'failed'
            file_obj['reason'] = pdf_ex
        else:
            file_obj['text'] = text
            file_obj['status'] = 'success'
            file_obj['reason'] = 'Extract pdf successfully!'

        return file_obj

    def get_detected_text(self, job_id: str, keep_newlines: bool = False) -> str:
        """
        Giving job_id, return plain text extracted from input document.
        :param job_id: Textract DetectDocumentText job Id
        :param keep_newlines: if True, output will have same lines structure as the input document
        :return: plain text as extracted by Textract
        """
        max_results = 1000
        pagination_token = None
        finished = False
        text = ''

        while not finished:
            if pagination_token is None:
                response = self.textract_client.get_document_text_detection(JobId=job_id, MaxResults=max_results)
            else:
                response = self.textract_client.get_document_text_detection(JobId=job_id, MaxResults=max_results, NextToken=pagination_token)

            sep = ' ' if not keep_newlines else '\n'
            status = response['JobStatus']
            if status == 'IN_PROGRESS':
                continue
            else:
                text += sep.join([x['Text'] for x in response['Blocks'] if x['BlockType'] == 'LINE'])

                if 'NextToken' in response:
                    pagination_token = response['NextToken']
                else:
                    finished = True

        return text
