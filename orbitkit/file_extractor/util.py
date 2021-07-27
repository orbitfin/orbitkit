from orbitkit.file_extractor.exception import FileExtractorTimeoutException


def create_uri(bucket_name, file_name):
    return "s3://" + bucket_name + "/" + file_name


def timeout_handler(signum, frame):
    raise FileExtractorTimeoutException("File extractor timeout err")
