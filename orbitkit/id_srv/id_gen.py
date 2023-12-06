import uuid
from typing import Optional

printable_char = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
]

# 0 as a padding number
printable_char_no_0_1 = [
    "2", "3", "4", "5", "6", "7", "8", "9",
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
]

"""版本2，生成最多 22 位的 ID
参考链接：# https://github.com/skorokithakis/shortuuid/tree/master
生成思路：根据 UUID3 或者 UUID4 得到的 32 位 16 进制数，转换成 62 进制的数
"""


def get_random_short_id_v2(padding: Optional[int] = 22):
    _tmp_id = get_random_uuid(with_dash=True)
    return _convert_10_2_60(_tmp_id, padding)


def get_fix_short_id_v2(long_id: str, padding: Optional[int] = 22):
    _tmp_id = get_fix_uuid(long_id=long_id, with_dash=True)
    return _convert_10_2_60(_tmp_id, padding)


def _convert_10_2_60(id_16: str, padding: Optional[int]):
    _tmp_id_10 = int(id_16, 16)

    output = ""
    while _tmp_id_10:
        _tmp_id_10, digit = divmod(_tmp_id_10, 60)
        output += printable_char_no_0_1[digit]
    if padding:
        remainder = max(padding - len(output), 0)
        output = output + "0" * remainder

    return output[::-1]


"""版本1，生成 8 位数的短 ID
参考链接：https://www.cnblogs.com/shouke/archive/2020/08/02/13423073.html
生成思路：根据 UUID3 或者 UUID4 得到的 32 位 16 进制数进行分组，每组 4 个，一共 8 组。对每一组的数字对 62 取余。
"""


def get_random_short_id():
    _tmp_id = get_random_uuid(with_dash=True)
    _buffer = []
    # 循环 8 次，每次取出 4 个
    for i in range(0, 8):
        start = i * 4
        end = i * 4 + 4
        # 将 16 进制的 uuid 转换成 10 进制的数字
        val = int(_tmp_id[start:end], 16)
        _buffer.append(printable_char[val % 62])
    return "".join(_buffer)


def get_fix_short_id(long_id, ver=1):
    _tmp_id = get_fix_uuid(long_id=long_id, with_dash=True)
    _buffer = []
    for i in range(0, 8):
        start = i * 4
        end = i * 4 + 4
        val = int(_tmp_id[start:end], 16)
        _buffer.append(printable_char[val % 62])
    short_id = "".join(_buffer)
    if ver > 1:
        short_id += '_' + str(ver)
    return {'short_id': short_id, 'ver': ver}


"""使用 UUID3 和 UUID4 分别得到固定的和随机的 UUID
Python 的 UUID3 生成的 ID 是 128 位的十进制数，可以表示为 32 位的十六进制数位。
Python 的 UUID3 生成的 ID 在给定相同的命名空间和名称的情况下是唯一的，它是通过将命名空间和名称作为输入，应用 MD5 哈希算法生成的。
由于 MD5 算法的特性，即使输入的命名空间和名称有微小的变化，生成的 ID 也会有很大的差异，从而保证了唯一性。
"""


def get_random_uuid(with_dash=False):
    if with_dash:
        return str(uuid.uuid4()).replace("-", '')
    else:
        return str(uuid.uuid4())


def get_fix_uuid(long_id, with_dash=False):
    if with_dash:
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, long_id)).replace("-", '')
    else:
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, long_id))
