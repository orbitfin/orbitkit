import re
import os
import uuid
from typing import Any, Dict, Optional


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


if __name__ == '__main__':
    res = gen_ot_uuid_by_key('x', prefix='oil')
    # res = gen_ot_uuid_random()
    print(res)
