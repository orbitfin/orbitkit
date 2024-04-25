import re


def oss_split_path(oss_path):
    if not oss_path.startswith('oss://'):
        raise Exception("Invalid oss path format.")

    oss_path_re = re.compile(r"(oss://[a-zA-Z\-_0-9]+)/(.+)")
    path_group = oss_path_re.search(oss_path).groups()
    return {
        'bucket': path_group[0].replace('oss://', ''),
        'store_path': path_group[1],
    }
