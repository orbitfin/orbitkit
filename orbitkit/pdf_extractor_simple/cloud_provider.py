import os
import logging
import threading
from orbitkit.util import s3_split_path, get_from_dict_or_env, get_content_type_4_filename, oss_split_path
from orbitkit.pdf_extractor_simple.base import CloudObjectProvider

logger = logging.getLogger(__name__)

try:
    import oss2
    import boto3
    import botocore
    import requests
    from botocore.exceptions import ClientError
except ImportError:
    raise ValueError(
        "Please install below packages before using PDF Extractor function.\n"
        "- boto3\n"
        "- oss2\n"
        "- requests\n"
    )


def singleton(cls):
    instances = {}
    lock = threading.Lock()

    def get_instance(*args, **kwargs):
        with lock:
            if cls not in instances:
                instances[cls] = cls(*args, **kwargs)
            return instances[cls]

    return get_instance


@singleton
class AwsCloudObjectProvider(CloudObjectProvider):

    def __init__(self, *args, **kwargs):
        aws_access_key_id = get_from_dict_or_env(
            kwargs, "aws_access_key_id", "AWS_ACCESS_KEY_ID",
        )

        aws_secret_access_key = get_from_dict_or_env(
            kwargs, "aws_secret_access_key", "AWS_SECRET_ACCESS_KEY",
        )

        self.s3_resource = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    def check_file_exist(self, cloud_path: str) -> bool:
        s3_path_obj = s3_split_path(cloud_path)
        try:
            self.s3_resource.Object(s3_path_obj["bucket"], s3_path_obj["store_path"]).load()
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

    def download_file(self, cloud_path: str, local_path: str, filename: str):
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        s3_path_obj = s3_split_path(cloud_path)
        self.s3_resource.Bucket(s3_path_obj["bucket"]).download_file(s3_path_obj["store_path"], os.path.join(local_path, filename))

    def upload_file(self, cloud_path: str, local_path: str):
        if not os.path.exists(local_path):
            raise Exception("Local file doesn't exist!")

        content_type = get_content_type_4_filename(cloud_path, text_with_utf8=True)
        s3_path_obj = s3_split_path(cloud_path)

        self.s3_client.upload_file(local_path,
                                   s3_path_obj["bucket"],
                                   s3_path_obj["store_path"],
                                   ExtraArgs={'ContentType': content_type})


@singleton
class OssCloudObjectProvider(CloudObjectProvider):
    def __init__(self, *args, **kwargs):
        oss_app_id = get_from_dict_or_env(
            kwargs, "ossappid", "OSSAPPID",
        )

        oss_pwd = get_from_dict_or_env(
            kwargs, "osspwd", "OSSPWD",
        )

        self.oss_endpoint = get_from_dict_or_env(
            kwargs, "ossendpoint", "OSSENDPOINT",
        )

        self.auth = oss2.Auth(oss_app_id, oss_pwd)

    def check_file_exist(self, cloud_path: str) -> bool:
        oss_path_obj = oss_split_path(cloud_path)
        oss_bucket = oss2.Bucket(self.auth, self.oss_endpoint, oss_path_obj["bucket"])
        oss_result = oss_bucket.object_exists(oss_path_obj["store_path"])

        return oss_result

    def download_file(self, cloud_path: str, local_path: str, filename: str):
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        oss_path_obj = oss_split_path(cloud_path)
        oss_bucket = oss2.Bucket(self.auth, self.oss_endpoint, oss_path_obj["bucket"])
        file_path = os.path.join(local_path, filename)
        oss_bucket.get_object_to_file(oss_path_obj["store_path"], file_path)

    def upload_file(self, cloud_path: str, local_path: str):
        if not os.path.exists(local_path):
            raise Exception("Local file doesn't exist!")

        oss_path_obj = oss_split_path(cloud_path)
        oss_bucket = oss2.Bucket(self.auth, self.oss_endpoint, oss_path_obj["bucket"])
        content_type = get_content_type_4_filename(cloud_path, text_with_utf8=True)
        oss_bucket.put_object_from_file(oss_path_obj["store_path"], local_path, headers={"Content-Type": content_type})


@singleton
class HttpCloudObjectProvider(CloudObjectProvider):
    def __init__(self, *args, **kwargs):
        pass

    def check_file_exist(self, cloud_path: str) -> bool:
        return False

    def download_file(self, cloud_path: str, local_path: str, filename: str):
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        file_path = os.path.join(local_path, filename)
        response = requests.get(cloud_path)
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type')
            if content_type is None or content_type != 'application/pdf':
                raise Exception(f"File type error! path:{cloud_path} Content-Type:{content_type} ")
            with open(file_path, 'wb') as file:
                file.write(response.content)
        else:
            raise Exception(f"File Download error! path:{cloud_path} status-code:{response.status_code}")

    def upload_file(self, cloud_path: str, local_path: str):
        pass
