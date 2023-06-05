from orbitkit.util import ExtenCons, get_content_type_4_filename

print(ExtenCons.EXTEN_APPLI_DOCX.value)
print(ExtenCons.EXTEN_APPLI_PDF.value)
print(ExtenCons.EXTEN_TEXT_HTML_UTF8.value)

print(get_content_type_4_filename('xxxxx.txt'))
print(get_content_type_4_filename('xxxxx.txt', True))
print(get_content_type_4_filename('xxxxx.htm', False))
