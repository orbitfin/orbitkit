import re


def is_no_mess_code(text):
    # If more than 5 char, no mess code
    """
    常用汉字：\u4e00 到 \u9fff
    扩展汉字：\u3400 到 \u4dbf
    部首补充：\u2e80 到 \u2eff
    符号和标点：\u3000 到 \u303f
    汉字笔画：\u31c0 到 \u31ef
    汉字结构描述字符：\u2ff0 到 \u2fff
    中日韩汉字共同使用的汉字：\u2e00 到 \u2e7f:
    """
    # 如果连着有 10 个中文字符，则没有乱码
    pattern_cn = re.compile('[\u4e00-\u9fa5]{10}')
    if pattern_cn.search(text):
        return True

    # 去掉空格后，如果连着有 10 个中文字符，则没有乱码
    text_without_spaces = re.sub(r"\s+", "", text)
    pattern_cn = re.compile('[\u4e00-\u9fa5]{10}')
    if pattern_cn.search(text_without_spaces):
        return True

    # If more than 5 English word, no mess code
    pattern_en = re.compile('[a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+ [a-zA-Z]+')
    if pattern_en.search(text):
        return True
    return False
