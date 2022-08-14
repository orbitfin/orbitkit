from orbitkit import FileDispatcher

if __name__ == '__main__':
    # Init extractor
    file_dispatcher = FileDispatcher(extractor_config={
        "extract_url": "",
        "aws_access_key_id": "",
        "aws_secret_access_key": ""
    })

    # Configure file info
    file_obj = FileDispatcher.get_params_template()
    file_obj.update({
        'bucket': 'filing-reports',
        'store_path': 'reports-data/stock_xtse/2022/05/03/seder_00000131_5196199.pdf',
        'file_name': '',
        'file_type': 'pdf',
    })

    # Init specific extractor
    extractor = file_dispatcher.init_extractor(file_obj)

    # Start extracting
    # res = extractor.extract()
    res = extractor.extract_timeout()
    print(res)
    print(res['text'])
