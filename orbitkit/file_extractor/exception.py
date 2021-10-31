class FileExtractorTimeoutException(Exception):
    pass


class ParamsInvalidException(Exception):
    pass


class NoProperExtractorFindException(Exception):
    def __init__(self):
        super().__init__('NoProperExtractorFind Exception')
