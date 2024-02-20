import logging
import boto3
from orbitkit.util import get_from_dict_or_env, s3_split_path
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
        Check a file does it exist in s3
        :param s3_path: s3 path
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

    def copy_file(self, source_path, target_path):
        """
        Move file from one path to another
        :param source_path: Source s3 path location
        :param target_path: Target s3 path location
        :return:
        """
        source_path_obj = s3_split_path(source_path)
        target_path_obj = s3_split_path(target_path)

        self.s3_resource.Object(target_path_obj["bucket"], target_path_obj["store_path"]).copy_from(
            CopySource=source_path_obj["bucket"] + '/' + source_path_obj["store_path"],
        )

    def delete_file(self, s3_path):
        """
        Delete a file from s3
        :param s3_path: Target s3 path
        :return:
        """
        s3_path_obj = s3_split_path(s3_path)
        self.s3_resource.Object(s3_path_obj["bucket"], s3_path_obj["store_path"]).delete()
