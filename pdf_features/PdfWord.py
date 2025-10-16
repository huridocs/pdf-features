from pydantic import BaseModel
from pdf_features import Rectangle
from lxml.etree import ElementBase


class PdfWord(BaseModel):
    text: str
    bounding_box: Rectangle
    page_number: int

    def __str__(self):
        return f"PdfWord(text={self.text}, bounding_box={self.bounding_box}, page_number={self.page_number})"

    @staticmethod
    def from_etree_element(element: ElementBase, page_number: int):
        text = element.text.strip()
        bounding_box = Rectangle.from_pdf_text_etree_element(element)
        return PdfWord(text=text, bounding_box=bounding_box, page_number=page_number)
