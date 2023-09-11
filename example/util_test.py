from orbitkit import util as outil

extension = outil.get_content_type_v1('pdf')
print(extension)

# date util
print(outil.get_next_day("2022-02-28"))
print(outil.get_next_workday_cn("2022-02-28"))
