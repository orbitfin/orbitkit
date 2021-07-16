from orbitkit import FileDispatcher

if __name__ == '__main__':
    file_obj = FileDispatcher.get_params_template()
    file_obj['bucket'] = 'vision-filemgt-dev'
    file_obj['store_path'] = 'user-2/a14983bc-0779-471a-89e2-7a83d8cfc92b.docx'
    file_obj['file_name'] = 'a14983bc-0779-471a-89e2-7a83d8cfc92b'
    file_obj['file_type'] = 'docx'
    file_dispatcher = FileDispatcher(file_obj)

    # res = file_dispatcher.to_extract()
    res = file_dispatcher.to_extract_timeout()

    print(res)
