class PdfExtractionException(Exception):
    default_detail = "PDF Extraction Exception."
    code = "exe_pdf_exception"

    def __init__(self, detail=None):
        if detail is None:
            self.detail = self.default_detail
        else:
            self.detail = detail

    def __str__(self):
        return str(self.detail)


class TooManyPagesException(PdfExtractionException):
    """ Too many pages. """

    default_detail = "Too many pages Exception."
    code = "exe_too_many_pages"


class CidEncryptionException(PdfExtractionException):
    """ (cid:00) encryption pdf file. """

    default_detail = "(cid:00) encryption pdf file Exception."
    code = "exe_cid_encryption"


class OcrBrokenException(PdfExtractionException):
    """ Empty content, OCR or broken pdf file. """

    default_detail = "Empty content, OCR or broken pdf file Exception."
    code = "exe_ocr_broken"
