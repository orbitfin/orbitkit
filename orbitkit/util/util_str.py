# -*- coding: utf-8 -*-

EMPTY_STR = ""


def is_empty(word):
    return bool(word == EMPTY_STR)


def is_empty_strip(word):
    return bool(str(word).strip() == EMPTY_STR)
