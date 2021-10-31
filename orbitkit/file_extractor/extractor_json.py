import json
from orbitkit.file_extractor.extractor import FileExtractor


class FileExtractorJson(FileExtractor):
    def __init__(self):
        super().__init__()

    def extract(self):
        file_obj = self.file_obj

        file_type = file_obj['file_type']
        bucket_name = file_obj['bucket']
        key = file_obj['store_path']
        file_name = file_obj['file_name']

        try:
            _id = file_name.split('.')[1]
            response = self.s3.get_object(Bucket=bucket_name, Key=key)
            contents = response['Body'].read()
            text = str(contents, encoding="utf8")
            data = json.loads(text)
            results = data['results']
            speaker_labels = results['speaker_labels']
            segments = speaker_labels['segments']
            index = 0
            items = results['items']
            text = []

            for segment in segments:
                start_time = segment['start_time']
                end_time = segment['end_time']
                speaker_label = segment['speaker_label']
                length = len(segment['items'])
                while len(items) > (index + length) and items[index + length]['type'] == 'punctuation':
                    length = length + 1
                sentence = items[index:index + length]

                rtn = ' '.join([word['content'] for line in sentence for word in line['alternatives']])
                index = index + length
                record = {
                    'start_time': start_time,
                    'end_time': end_time,
                    'speaker_label': speaker_label,
                    'content': rtn
                }
                text.append(record)

            file_obj['text'] = json.dumps(text)
            file_obj['status'] = 'success'
            file_obj['reason'] = 'Extract json successfully!'
        except Exception as e:
            file_obj['text'] = ''
            file_obj['status'] = 'failed'
            file_obj['reason'] = str(e)

        return file_obj
