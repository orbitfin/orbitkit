# -*- coding: utf-8 -*-
import re
import uuid


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
