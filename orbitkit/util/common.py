# -*- coding: utf-8 -*-
import re
import uuid


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


if __name__ == '__main__':
    res = gen_ot_uuid_by_key('x', prefix='oil')
    # res = gen_ot_uuid_random()
    print(res)
