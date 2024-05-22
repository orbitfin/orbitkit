import logging
import json
from orbitkit.pdf_extractor_simple.base import PdfExtractor
from orbitkit.pdf_extractor_simple.utils import is_no_mess_code

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

try:
    import pypdf
    from pdf2image import convert_from_path
    from pytesseract import pytesseract
except ImportError:
    raise ValueError(
        "Please install below packages before using PDF Extractor function.\n"
        "- pypdf\n"
        "- pdf2image\n"
        "- pytesseract\n"
    )


class PyPdfPdfExtractor(PdfExtractor):
    def __init__(self, mess_code_per: int = 90, low_length_per: int = 95):
        super().__init__()
        self.mess_code_per = mess_code_per
        self.low_length_per = low_length_per

    def extract(self, local_path_pdf: str):
        self.local_path_pdf_txt = local_path_pdf + ".txt"
        try:
            with open(local_path_pdf, 'rb') as pdf_file, open(self.local_path_pdf_txt, "w+", encoding="utf-8") as pdf_file_txt:
                pdf_reader = pypdf.PdfReader(pdf_file)

                for index, page_obj in enumerate(pdf_reader.pages, start=1):
                    logger.info(f"Start to extract page: {str(index)}")

                    full_text = page_obj.extract_text()
                    try:
                        # 特殊字符无法使用utf-8编码写入文本, 引发UnicodeEncodeError 测试用例 oss://edidata/report/china_money/705007-2489084.pdf
                        pdf_file_txt.write(json.dumps({"page_no": str(index), "text": full_text}, ensure_ascii=False))
                        pdf_file_txt.write('\n')
                    except UnicodeEncodeError as e:
                        full_text = full_text.encode('utf-8', 'replace').decode('utf-8').strip()
                        pdf_file_txt.write(json.dumps({"page_no": str(index), "text": full_text}, ensure_ascii=False))
                        pdf_file_txt.write('\n')
                        logger.warning(f"{str(index)} -->  {e}")
        except Exception as e:
            self.exception_exist = True
            logger.error(e, exc_info=True)

    def do_continue(self) -> bool:
        # If there is exception
        if self.exception_exist:
            return True

        total_page = 0
        judge_mess_code_wrong = 0
        judge_length_wrong = 0

        with open(self.local_path_pdf_txt, "r", encoding="utf-8") as f:
            for line in f.readlines():
                line_json = json.loads(line)
                if len(line_json["text"]) > 10:
                    pass
                else:
                    judge_length_wrong += 1

                if is_no_mess_code(line_json["text"]):
                    pass
                else:
                    judge_mess_code_wrong += 1

                total_page += 1

        # Final judge
        judge_mess_code_per = ((total_page - judge_mess_code_wrong) / total_page) * 100
        judge_length_per = ((total_page - judge_length_wrong) / total_page) * 100

        logger.info(f"Total page: {str(total_page)}, Mess code page: {str(judge_mess_code_wrong)}, Low length page: {str(judge_length_wrong)}")

        if judge_mess_code_per > self.mess_code_per and judge_length_per > self.low_length_per:
            return False
        return True


class MixedPdfPdfExtractor(PdfExtractor):
    def __init__(self, issue_page_per: int = 95, skip_ocr_exceed_page: int = 0):
        super().__init__()
        self.issue_page_per = issue_page_per
        self.total_page = 0
        self.judge_length_wrong = 0
        self.skip_ocr_exceed_page = skip_ocr_exceed_page

    def _extract_by_ocr(self, index, local_path_pdf):
        images = convert_from_path(local_path_pdf)
        image = images[index - 1]
        image = image.convert('L')
        full_text_ocr = pytesseract.image_to_string(image, lang='chi_sim')
        return str(full_text_ocr).strip()

    def extract(self, local_path_pdf: str):
        self.local_path_pdf_txt = local_path_pdf + ".txt"
        try:
            with open(local_path_pdf, 'rb') as pdf_file, open(self.local_path_pdf_txt, "w+", encoding="utf-8") as pdf_file_txt:
                pdf_reader = pypdf.PdfReader(pdf_file)
                for index, page_obj in enumerate(pdf_reader.pages, start=1):
                    logger.warning(f">>> page: {str(index)} is processing <<<")
                    logger.debug(f"page: {str(index)} --------------------------------------------------------------------------------------")

                    try:
                        full_text = page_obj.extract_text().strip()
                    except Exception as e:
                        if 0 < self.skip_ocr_exceed_page < index:  # skip_ocr_excess_page > 0 超出最大页面，不继续解析
                            logger.warning(f"Page {str(index)} is OCR needed, but exceed hard stop condition!")
                            break

                        logger.warning("Normal pypdf can't handle: " + str(e))
                        full_text = self._extract_by_ocr(index, local_path_pdf)

                    if len(full_text) < 10:
                        if 0 < self.skip_ocr_exceed_page < index:  # skip_ocr_excess_page > 0 超出最大页面，不继续解析
                            logger.warning(f"Page {str(index)} is OCR needed, but exceed hard stop condition!")
                            break

                        logger.warning("1) Low to 10 char length by pypdf extract lib...")
                        full_text_ocr = self._extract_by_ocr(index, local_path_pdf)
                        if len(full_text_ocr) < 10:
                            logger.warning("1.1) Try by OCR extract failed with char length >>>>>>>>>>>>>>>")
                            logger.debug(full_text_ocr + "\n<<<<<<<<<<<<<<<<<<<<<<<<<")
                            self.judge_length_wrong += 1
                        else:
                            logger.warning("1.2) Try by OCR extract success >>>>>>>>>>>>>>>")
                            logger.debug(full_text_ocr + "\n<<<<<<<<<<<<<<<<<<<<<<<<<")
                            # OCR 提取的文本 > 10，不需要判断乱码问题
                            pdf_file_txt.write(json.dumps({"page_no": str(index), "text": full_text_ocr}, ensure_ascii=False))
                            pdf_file_txt.write('\n')
                    else:
                        logger.debug("2) Good, larger than 10 char length...")
                        if is_no_mess_code(full_text):
                            logger.debug("2.1) No mess code >>>>>>>>>>>>>>>>>>>>>>>>>")
                            logger.debug(full_text + "\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                            # >10 没有乱码，则直接写入
                            try:
                                pdf_file_txt.write(
                                    json.dumps({"page_no": str(index), "text": full_text}, ensure_ascii=False))
                                pdf_file_txt.write('\n')
                            except UnicodeEncodeError as e:
                                full_text = full_text.encode('utf-8', 'replace').decode('utf-8').strip()
                                pdf_file_txt.write(
                                    json.dumps({"page_no": str(index), "text": full_text}, ensure_ascii=False))
                                pdf_file_txt.write('\n')
                                logger.warning(f"{str(index)} -->  {e}")
                        else:
                            if 0 < self.skip_ocr_exceed_page < index:  # skip_ocr_excess_page > 0 超出最大页面，不继续解析
                                logger.warning(f"Page {str(index)} is OCR needed, but exceed hard stop condition!")
                                break

                            logger.warning("2.2) with mess code so go OCR >>>>>>>>>>>>>>>>")
                            logger.debug(full_text + "\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                            full_text_ocr = self._extract_by_ocr(index, local_path_pdf)
                            logger.debug(">>>>>>>>>>>>>>>>\n" + full_text_ocr + "\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                            if len(full_text_ocr) < 10:
                                logger.debug("2.2.1) err")
                                self.judge_length_wrong += 1
                            else:
                                logger.debug("2.2.2) success")
                                # OCR 提取的文本 > 10，不需要判断乱码问题
                                pdf_file_txt.write(json.dumps({"page_no": str(index), "text": full_text_ocr}, ensure_ascii=False))
                                pdf_file_txt.write('\n')

                    logger.debug(f"page: {str(index)} --------------------------------------------------------------------------------------")
                    self.total_page += 1
        except Exception as e:
            self.exception_exist = True
            logger.error(e, exc_info=True)

    def do_continue(self) -> bool:
        if self.exception_exist:
            return True

        logger.info(f"Total page: {str(self.total_page)}, Issue page: {str(self.judge_length_wrong)}")
        if ((self.total_page - self.judge_length_wrong) / self.total_page) * 100 > self.issue_page_per:
            return False

        return True
