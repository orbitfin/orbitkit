import uuid

from orbitkit import id_srv

"""Test random short ID version1
"""
# print(id_srv.get_random_uuid())
# print(id_srv.get_fix_uuid(long_id="xxx"))
# print(id_srv.get_random_short_id())

# id_obj = id_srv.get_fix_short_id(long_id='123')
# print(id_obj['short_id'], id_obj['ver'])
# id_obj_1 = id_srv.get_fix_short_id(long_id=id_obj['short_id'], ver=id_obj['ver'] + 1)
# print(id_obj_1)

"""Test shortuuid
https://github.com/skorokithakis/shortuuid/tree/master
"""
# import shortuuid
# print(shortuuid.uuid())

"""Test short ID version2
"""

for _ in range(10000):
    sid = id_srv.get_random_short_id_v2(padding=22)
    print(sid, len(sid))

print(id_srv.get_fix_short_id_v2(long_id="hello/world"))

"""
ffffffffffffffffffffffffffffffff

hello/world
935287a8-17af-369d-95aa-fc0f9a5bf1a8
935287a817af369d95aafc0f9a5bf1a8(32)
aVCdIwEAZLwGumlxtBNX5C
"""

"""Test xxx.hex & xxx.int
"""
xxx = uuid.uuid3(uuid.NAMESPACE_DNS, "xxx")
print(xxx)
yyy = str(xxx).replace("-", '')
print(yyy)
print(int(yyy, 16))
print(xxx.hex)
print(xxx.int)
