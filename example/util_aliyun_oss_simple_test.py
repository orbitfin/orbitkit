from orbitkit.util import util_aliyun_oss_simple

bucket = util_aliyun_oss_simple.get_oss_bucket("edidata")

result = util_aliyun_oss_simple.down_oss(bucket, local_path="./123.txt", oos_path="report_tmp/705007-012481424.pdf.txt")
result = util_aliyun_oss_simple.push_oss(bucket, local_path="./123.txt", oos_path="report_tmp/123.pdf.txt")
