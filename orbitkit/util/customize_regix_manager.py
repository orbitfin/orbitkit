# -*- coding: utf-8 -*-
# @Time : 5/31/24 3:12 PM
# @Author : Atem Jetson
# @Email : atem.jetson@gmail.com
# @Project : GeneralTools
# @File : customize_regix_manager.py
from typing import List, Union
import re


class CustomizeRegixManager:
    def __init__(self):
        self.__regs = {}

    @property
    def debug_reg_info(self):
        return self.__regs

    def __set_reg(self, key: str, regix: str):
        """
        Statically add regular expressions
        :param key: regix key
        :param regix: regular expression
        """
        try:
            if key in self.__regs:
                print(f"-[WAR] reg reset: {key}|{regix}")
            else:
                print(f"-[INF] reg add: {key}|{regix}")
            self.__regs[key] = re.compile(regix)
        except BaseException as be:
            print(f"-[ERR] reg set failed: {be}")

    def set_reg_bulk(self, keys: dict, overwrite: bool = False):
        """
        :param keys: {regix_key:regular expression}
        :param overwrite: True: overwrite, False: only add new
        """
        if overwrite:
            for key, val in keys.items():
                self.__set_reg(key, val)
        else:
            for key, val in keys.items():
                if key not in self.__regs:
                    self.__set_reg(key, val)

    def search_reg(self, text: str, key: str, regix: str = None):
        """
        :param text: text to match
        :param key: regix key
        :param regix: regular expression
        """
        if key not in self.__regs and regix:
            self.__set_reg(key, regix)
        return self.__regs[key].findall(text)

    def search_reg_bulk(self, text: str, keys: Union[List, dict] = None) -> dict:
        """
        Dynamically add regular expressions and search for matches
        :param text: text to match
        :param keys: if list, like[re_key1, re_key2]; if dict, like{key1:re_1, key2:re2}
        :param key: string key of reg
        :return: {re_key1: result_1, re_key2: result_2}
        """
        if not keys:
            raise TypeError("search_reg_bulk() missing 1 required positional argument: key(s)")
        result_dict = {}
        if type(keys) is list:
            # list: match with patterns in __regs
            for key in keys:
                try:
                    results = self.__regs[key].findall(text)
                    result_dict[key] = results
                except IndexError as ie:
                    print(f"-[ERR] reg search failed: {ie}")
        elif type(keys) is dict:
            # dict: match with patterns in keys, if new key, add
            for key, val in keys.items():
                if key not in self.__regs:
                    self.__set_reg(key, val)
                results = self.__regs[key].findall(text)
                result_dict[key] = results
        return result_dict
