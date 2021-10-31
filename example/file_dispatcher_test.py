from orbitkit import FileDispatcher

if __name__ == '__main__':
    # Init extractor
    file_dispatcher = FileDispatcher(extractor_config={
        "extract_url": "",
        "aws_access_key_id": "",
        "aws_secret_access_key": ""
    })

    # 设置文件信息
    file_obj = FileDispatcher.get_params_template()
    file_obj.update({
        'bucket': 'filing-reports',
        'store_path': 'reports-data/test_extract/Prospekt Inv. BankInvest - 2020.09.21 clean.pdf',
        'file_name': '',
        'file_type': 'pdf',
    })

    # 实例化文件提取器
    extractor = file_dispatcher.init_extractor(file_obj)

    # 开始提取
    # res = extractor.extract()
    res = extractor.extract_timeout()
    print(res)
    print(res['text'])
