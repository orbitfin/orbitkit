import logging
import os.path
from typing import Optional
import boto3
from orbitkit.util import get_from_dict_or_env, s3_split_path, get_content_type_4_filename
import botocore
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AwsS3Wrapper:
    """Encapsulates Amazon s3 actions for Orbitfin"""

    def __init__(self, s3_resource, s3_client):
        """
        :param s3_resource: boto3.resource('s3')
        :param s3_client: boto3.client('s3')
        """
        self.s3_resource = s3_resource
        self.s3_client = s3_client

    @classmethod
    def from_s3(cls, *args, **kwargs):
        # Try to get key aws pair
        aws_access_key_id = get_from_dict_or_env(
            kwargs, "aws_access_key_id", "AWS_ACCESS_KEY_ID",
        )

        aws_secret_access_key = get_from_dict_or_env(
            kwargs, "aws_secret_access_key", "AWS_SECRET_ACCESS_KEY",
        )

        s3_resource = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

        return cls(s3_resource, s3_client)

    def get_s3_resource(self):
        return self.s3_resource

    def get_s3_client(self):
        return self.s3_client

    def check_file_exist(self, s3_path: str) -> bool:
        """
        :param s3_path: Target store path for s3.
        :return:
        """

        s3_path_obj = s3_split_path(s3_path)
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

    def copy_file(self, source_path: str, target_path: str):
        """
        :param source_path: Source s3 path location
        :param target_path: Target s3 path location
        :return:
        """
        source_path_obj = s3_split_path(source_path)
        target_path_obj = s3_split_path(target_path)

        self.s3_resource.Object(target_path_obj["bucket"], target_path_obj["store_path"]).copy_from(
            CopySource=source_path_obj["bucket"] + '/' + source_path_obj["store_path"],
        )

    def delete_file(self, s3_path: str):
        """
        :param s3_path: Target store path for s3.
        :return:
        """
        s3_path_obj = s3_split_path(s3_path)
        self.s3_resource.Object(s3_path_obj["bucket"], s3_path_obj["store_path"]).delete()

    def download_file(self, s3_path: str, local_path: str, filename: str):
        """
        :param s3_path: Target store path for s3.
        :param local_path: Local path
        :param filename: File name
        :return:
        """
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        s3_path_obj = s3_split_path(s3_path)
        self.s3_resource.Bucket(s3_path_obj["bucket"]).download_file(s3_path_obj["store_path"], os.path.join(local_path, filename))

    def upload_by_local_path(self, s3_path: str, local_path: str, text_with_utf8: bool = True):
        """
        :param s3_path: Target store path for s3.
        :param local_path: Local file path.
        :param text_with_utf8: If content-type start with "text/" then put ;charset=utf-8 after.
        :return:
        """
        if not os.path.exists(local_path):
            raise Exception("Local file doesn't exist!")

        content_type = get_content_type_4_filename(s3_path, text_with_utf8)
        s3_path_obj = s3_split_path(s3_path)

        self.s3_client.upload_file(local_path,
                                   s3_path_obj["bucket"],
                                   s3_path_obj["store_path"],
                                   ExtraArgs={'ContentType': content_type})

    def upload_file(self, s3_path: str, content: bytes, metadata: Optional[dict] = None, text_with_utf8: bool = True):
        """
        :param s3_path: Target store path for s3.
        :param content: The content of file, if text-like use content.encode("utf-8"), if binary then put directly.
        :param metadata: Custom metadata for file.
        :param text_with_utf8: If content-type start with "text/" then put ;charset=utf-8 after.
        :return:
        """
        s3_path_obj = s3_split_path(s3_path)
        content_type = get_content_type_4_filename(s3_path, text_with_utf8)

        object_put = self.s3_resource.Object(s3_path_obj["bucket"], s3_path_obj["store_path"])
        if metadata:
            object_put.put(Body=content, ContentType=content_type, Metadata=metadata)
        else:
            object_put.put(Body=content, ContentType=content_type)

    def get_file_meta_info(self, s3_path: str) -> dict:
        """
        :param s3_path: Target store path for s3.
        :return:
        """
        s3_path_obj = s3_split_path(s3_path)
        response = self.s3_client.head_object(Bucket=s3_path_obj["bucket"], Key=s3_path_obj["store_path"])
        return {
            "content_type": response['ContentType'],
            "metadata": response['Metadata'],
        }

    def read_text_like_file(self, s3_path: str, decoding: str = "utf-8") -> str:
        """
        :param s3_path: Target store path for s3.
        :param decoding: decoding, default is "utf-8".
        :return:
        """
        s3_path_obj = s3_split_path(s3_path)
        obj = self.s3_client.get_object(Bucket=s3_path_obj["bucket"], Key=s3_path_obj["store_path"])
        return obj['Body'].read().decode(decoding)
