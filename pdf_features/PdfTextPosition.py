import tempfile
import subprocess
from pathlib import Path
from lxml import etree
from lxml.etree import ElementBase

from pdf_features import Rectangle
from pdf_features.PdfWord import PdfWord


class PdfTextPosition:
    def __init__(self, pdf_path: Path | str):
        self.pdf_path = pdf_path
        self.pdf_words = self.from_pdf_path(pdf_path)

    @staticmethod
    def from_pdf_path(pdf_path: str | Path) -> list[PdfWord]:
        xml_path = Path(tempfile.gettempdir(), "pdf_text_positions.xml")
        subprocess.run(["pdftotext", "-bbox-layout", pdf_path, xml_path])
        file_content: str = open(xml_path, errors="ignore").read()
        file_bytes: bytes = file_content.encode("utf-8")
        parser = etree.XMLParser(recover=True, encoding="utf-8")
        root: ElementBase = etree.fromstring(file_bytes, parser=parser)
        page_number = 0
        pdf_words: list[PdfWord] = []
        for element in root.iter():
            if "page" in element.tag:
                page_number += 1
            elif "word" in element.tag and element.text and element.text.strip():
                pdf_words.append(PdfWord.from_etree_element(element, page_number))

        return pdf_words

    def get_pdf_words_within_bounding_box(self, text: str, bounding_box: Rectangle, page_number: int) -> list[PdfWord]:
        return [
            word for word in self.pdf_words if word.bounding_box.intersects(bounding_box) and word.page_number == page_number
        ]
