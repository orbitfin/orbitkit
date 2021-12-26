from orbitkit import id_srv

print(id_srv.get_random_uuid())
print(id_srv.get_fix_uuid(long_id="xxx"))
print(id_srv.get_random_short_id())

id_obj = id_srv.get_fix_short_id(long_id='123')
print(id_obj['short_id'], id_obj['ver'])
id_obj_1 = id_srv.get_fix_short_id(long_id=id_obj['short_id'], ver=id_obj['ver'] + 1)
print(id_obj_1)
