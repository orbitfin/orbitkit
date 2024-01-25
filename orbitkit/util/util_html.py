import re


def remove_all_tags(tag_str, substitution=""):
    """
    :param tag_str:
    :param substitution:
    :return:
    """
    return str(re.sub(r"<.*?>", substitution, tag_str))
