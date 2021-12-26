import uuid

printable_char = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"
]


def get_random_short_id():
    id = str(uuid.uuid4()).replace("-", '')  # 注意这里需要用uuid4
    buffer = []
    # 循环 8 次，每次取出 4 个
    for i in range(0, 8):
        start = i * 4
        end = i * 4 + 4
        # 将 16 进制的 uuid 转换成 10 进制的数字
        val = int(id[start:end], 16)
        buffer.append(printable_char[val % 62])
    return "".join(buffer)


def get_fix_short_id(long_id, ver=1):
    id = str(uuid.uuid3(uuid.NAMESPACE_DNS, long_id)).replace("-", '')
    buffer = []
    for i in range(0, 8):
        start = i * 4
        end = i * 4 + 4
        val = int(id[start:end], 16)
        buffer.append(printable_char[val % 62])
    short_id = "".join(buffer)
    if ver > 1:
        short_id += '_' + str(ver)
    return {'short_id': short_id, 'ver': ver}


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
