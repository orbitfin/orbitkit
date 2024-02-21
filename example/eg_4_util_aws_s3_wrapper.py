from util import AwsS3Wrapper
import boto3

aws_s3_wrapper = AwsS3Wrapper(boto3.resource('s3'), boto3.client('s3'))


def test_check_file_exist():
    res = aws_s3_wrapper.check_file_exist(s3_path="s3://orbit-common-resources/test111/test22/tesst.md")
    print(res)


def test_copy_file():
    aws_s3_wrapper.copy_file(source_path="s3://orbit-common-resources/leg_pdf_demo/table_20240207_085919.xlsx",
                             target_path="s3://orbit-common-resources/leg_pdf_demo/table_20240207_085919_copy.xlsx")


def test_delete_file():
    aws_s3_wrapper.delete_file(s3_path="s3://orbit-common-resources/leg_pdf_demo/table_20240207_085919_copy.xlsx")


def test_get_file_meta_info():
    meta_info = aws_s3_wrapper.get_file_meta_info(s3_path="s3://orbit-common-resources/leg_pdf_demo/table_20240207_085919.xlsx")
    print(meta_info)


def test_read_text_like_file():
    res = aws_s3_wrapper.read_text_like_file(s3_path="s3://orbit-common-resources/leg_pdf_demo/oqa_result.csv")
    print(res)


def test_download_file():
    aws_s3_wrapper.download_file(s3_path="s3://orbit-common-resources/leg_pdf_demo/table_20240207_085919.xlsx",
                                 local_path="/Users/crown/Projects/orbitkit/xxx/yyy",
                                 filename="table_20240207_085919.xlsx")


def test_upload_file():
    # with open("/Users/crown/Desktop/embedding_id_20240101_20240218.txt", "r+", encoding="utf-8") as f:
    #     content = f.read()
    #     aws_s3_wrapper.upload_file(s3_path="s3://orbit-common-resources/lilu/embedding_id_20240101_20240218_copy.txt",
    #                                content=content.encode("utf-8"),
    #                                metadata={"x": "a"})

    with open("/Users/crown/Desktop/screenshot-20230628-223157.png", "rb") as f:
        content = f.read()
        aws_s3_wrapper.upload_file(s3_path="s3://orbit-common-resources/lilu/screenshot-20230628-223157.png",
                                   content=content,
                                   metadata={"x": "a"})


def test_upload_by_local_path():
    aws_s3_wrapper.upload_by_local_path(s3_path="s3://orbit-common-resources/lilu/embedding_id_20240101_20240218.txt",
                                        local_path="/Users/crown/Desktop/embedding_id_20240101_20240218.txt")


if __name__ == "__main__":
    test_download_file()
