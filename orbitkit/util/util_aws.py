import os.path
import re


def s3_split_path(s3_path: str):
    if not s3_path.startswith('s3://'):
        raise Exception("Invalid s3 path format.")

    s3_path_re = re.compile(r"(s3://[a-zA-Z\-_0-9]+)/(.+)")
    path_group = s3_path_re.search(s3_path).groups()
    return {
        'bucket': path_group[0].replace('s3://', ''),
        'store_path': path_group[1],
    }


def s3_concat_path(bucket: str, store_path: str):
    store_path = store_path.lstrip('/')
    return os.path.join('s3://', bucket, store_path)
