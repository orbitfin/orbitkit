import hashlib


def get_md5_by_file(file_path: str, use_lower: bool = False):
    """
    Get file md5 code.
    :param file_path:
    :param use_lower:
    :return:
    """
    with open(file_path, 'rb+') as f:
        m = hashlib.md5()
        m.update(f.read())
        md5_hash = m.hexdigest()
        if use_lower:
            return str(md5_hash).lower()
        return str(md5_hash).upper()


def get_md5_by_str(target_str: str, use_lower: bool = False):
    """
    Get string md5 code.
    :param target_str:
    :param use_lower:
    :return:
    """
    m = hashlib.md5()
    m.update(target_str.encode(encoding='utf-8'))
    md5_hash = m.hexdigest()
    if use_lower:
        return str(md5_hash).lower()
    return str(md5_hash).upper()
