import os.path
import re
import boto3
import botocore
from orbitkit.util import get_from_dict_or_env


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


def s3_path_join(*paths):
    """Always connect path with /."""
    if len(paths) <= 0:
        raise ValueError("At least one path needed!")

    paths_clean = [str(path).strip("/") for path in paths if str(path).strip() != ""]
    return "/".join(paths_clean)


class S3Util:
    def __init__(self, *args, **kwargs):
        # Try to get key aws pair
        aws_access_key_id = get_from_dict_or_env(
            kwargs, "aws_access_key_id", "AWS_ACCESS_KEY_ID",
        )

        aws_secret_access_key = get_from_dict_or_env(
            kwargs, "aws_secret_access_key", "AWS_SECRET_ACCESS_KEY",
        )

        self.s3_resource = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    def get_s3_resource(self):
        return self.s3_resource

    def get_s3_client(self):
        return self.s3_client

    def check_file_exist(self, bucket: str, store_path: str):
        try:
            self.s3_resource.Object(bucket, store_path).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                # The object does not exist.
                return False
            else:
                # Something else has gone wrong.
                raise Exception("Check s3 file exist unknown error...")
        else:
            # The object does exist.
            return True
