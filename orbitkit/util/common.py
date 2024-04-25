import datetime
import re
import os
import uuid
from typing import Any, Dict, Optional
from deprecated.sphinx import deprecated


def gen_ot_uuid_random():
    """
    :return:
    """
    return str(uuid.uuid4())


def gen_ot_uuid_by_key(word, prefix=''):
    """
    :param word:
    :param prefix:
    :return:
    """
    if str(prefix).strip() != '':
        prefix = prefix + '_'

    return prefix + str(uuid.uuid3(uuid.NAMESPACE_DNS, str(word)))


def get_orbit_uuid_v1(word):
    """
    :param word:
    :return:
    """
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, str(word)))


@deprecated(version="v1", reason="remove_all_tags_v1 is deprecated.")
def remove_all_tags_v1(tag_str, substitution=''):
    """
    :param tag_str:
    :param substitution:
    :return:
    """
    return str(re.sub(r'<.*?>', substitution, tag_str))


def get_from_dict_or_env(
        data: Dict[str, Any], key: str, env_key: str, default: Optional[str] = None
) -> str:
    """Get a value from a dictionary or an environment variable."""
    if key in data and data[key]:
        return data[key]
    else:
        return get_from_env(key, env_key, default=default)


def get_from_env(key: str, env_key: str, default: Optional[str] = None) -> str:
    """Get a value from a dictionary or an environment variable."""
    if env_key in os.environ and os.environ[env_key]:
        return os.environ[env_key]
    elif default is not None:
        return default
    else:
        raise ValueError(
            f"Did not find {key}, please add an environment variable"
            f" `{env_key}` which contains it, or pass"
            f"  `{key}` as a named parameter."
        )


def date_2_path(date_str: str) -> str:
    """
    2023-09-08T09:08 -> 2023/09/08
    :param date_str:
    :return:
    """
    if len(date_str) < 10:
        raise Exception("The length of Date str is not enough.")

    date_pre10_str = date_str[0:10]
    try:
        date_obj = datetime.datetime.strptime(date_pre10_str, '%Y-%m-%d')
    except:
        raise Exception("Wrong date format, should be in %Y-%m-%d format.")

    return date_obj.strftime("%Y/%m/%d")
