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


def customize_regix_match(text: str, regix_pairs: dict) -> dict:
    reg_dict = {}
    for key, val in regix_pairs.items():
        if isinstance(val, list):
            reg_dict[key] = []
            for v in val:
                reg_dict[key].append(re.compile(v, re.DOTALL))
        elif isinstance(val, str):
            reg_dict[key] = [re.compile(val, re.DOTALL)]
    result_dict = {}
    for pairs in reg_dict:
        for reg in reg_dict[pairs]:
            result = reg.findall(text, re.S)
            flag = True
            for r in result:
                if isinstance(r, tuple):
                    for i in r:
                        if re.sub(r' ', '', i) != '':
                            flag = False
                elif isinstance(r, str):
                    if re.sub(r' ', '', r) != '':
                        flag = False
            if not flag:
                result_dict[pairs] = result
                break
            else:
                ...
    return result_dict


if __name__ == '__main__':
    #     # test case
    #     text = """
    #     公告序號： 1
    # 公告類型： 非既定之餘額變動
    # 受影響之債券種類：
    # 受影響之債券期別： 111-4  期
    # 受影響之債券代號： F05008
    # 主旨： 公告第一商業銀行股份有限公司111年度第4期無擔保一般順位5年期美元計價可贖回利率連結區間計息型金融債券已於民國113年01月12日~113年01月12日次級市場買回。
    # 事實發生日： 113 年 01 月 12 日 ~ 113 年 01 月 12 日
    # 內容
    # 　 1.發生緣由： 財團法人中華民國證券櫃檯買賣中心連結衍生性金融商品或為結構型債券之外幣計價國際債券管理辦法
    # 　 2.因應措施： （一）依財團法人中華民國證券櫃檯買賣中心連結衍生性金融商品或為結構型債券之外幣計價國際債券
    # 管理辦法，公告第一商業銀行股份有限公司111年度第4期無擔保一般順位5年期美元計價可贖回利率連
    # 結區間計息型金融債券(代碼1：F05008，簡稱1：S22FCB2)。已於民國113年1月12日~113年1月12日
    # 次級市場買回金額50,000元。
    # （二）本次非既定餘額變動前，本期債券現行已流通在外證券餘額19,700,000元
    # 　 3.對債權人之可能影響： 本次餘額變動後，流通在外證券餘額為19700000元
    # 　 4.其他應敘明事項： 無。
    # 申報日期： 113 年 01 月 12 日
    #     """
    #     re_list = {"事實發生日": "事實發生日：(.*?)~", "次級市場買回金額": ["Cannot match", "次級市場買回金額(.*?)元。"],
    #                "流通在外證券餘額": "流通在外證券餘額(.*?)元"}
    #     print(customize_regix_match(text, re_list))

    text = """
    标的证券：本期发行的证券为可交换为发行人所持中国长江电力股份
    有限公司股票（股票代码：600900.SH，股票简称：长江电力）的可交换公司债
    券。
    换股期限：本期可交换公司债券换股期限自可交换公司债券发行结束
    之日满 12 个月后的第一个交易日起至可交换债券到期日止，即 2023 年 6 月 2
    日至 2027 年 6 月 1 日止。
    """
    re_list = {
        '标的证券': ['.*股票代码：(.*)，股票简称.*', '.*自定义规则2.*'],
        '换股期限': ['.*自定义规则3.*', '.*换股期限.*到期日止，即(.*)至(.*)止.*']
    }
    print(customize_regix_match(text, re_list))
