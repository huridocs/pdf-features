from lxml.etree import ElementBase
from pydantic import BaseModel

from pdf_features.PdfFont import PdfFont
from pdf_features.PdfTokenStyle import PdfTokenStyle
from pdf_features.PdfTokenContext import PdfTokenContext
from pdf_features.Rectangle import Rectangle
from pdf_token_type_labels.Label import Label
from pdf_token_type_labels.TokenType import TokenType


class PdfToken(BaseModel):
    page_number: int
    id: str
    content: str
    font: PdfFont
    reading_order_no: int
    bounding_box: Rectangle
    token_type: TokenType
    token_style: PdfTokenStyle
    pdf_token_context: PdfTokenContext = PdfTokenContext()
    prediction: int = 0

    def __str__(self):
        return f"PdfToken(page_number={self.page_number}, content={self.content}, bounding_box={self.bounding_box}, token_type={self.token_type}"

    def same_line(self, token: "PdfToken"):
        if self.bounding_box.bottom < token.bounding_box.top:
            return False

        if token.bounding_box.bottom < self.bounding_box.top:
            return False

        return True

    @staticmethod
    def from_poppler_etree(page_number: int, xml_tag: ElementBase, pdf_font: PdfFont):
        if "id" in xml_tag.attrib:
            tag_id = xml_tag.attrib["id"]
        else:
            tag_id = "tag"

        reading_order_no = int(xml_tag.attrib["reading_order_no"]) if "reading_order_no" in xml_tag.attrib else -1
        bounding_box = Rectangle.from_poppler_tag_etree(xml_tag)
        token_type = TokenType.TEXT

        content = "".join(xml_tag.itertext()).strip()
        token_style = PdfTokenStyle.from_xml_tag(xml_tag=xml_tag, content=content, pdf_font=pdf_font)

        return PdfToken(
            page_number=page_number,
            id=tag_id,
            content=content,
            font=pdf_font,
            reading_order_no=reading_order_no,
            bounding_box=bounding_box,
            token_type=token_type,
            token_style=token_style,
        )

    @property
    def content_markdown(self) -> str:
        markdown_content = self.content
        markdown_content = self.token_style.get_styled_content_markdown(markdown_content)
        markdown_content = self.token_style.title_type.get_styled_content_markdown(markdown_content)
        markdown_content = self.token_style.script_type.get_styled_content(markdown_content)
        markdown_content = self.token_style.list_level.get_styled_content_markdown(markdown_content)
        markdown_content = self.token_style.hyperlink_style.get_styled_content_markdown(markdown_content)
        return markdown_content

    @property
    def content_html(self) -> str:
        html_content = self.content
        html_content = self.token_style.get_styled_content_html(html_content)
        html_content = self.token_style.title_type.get_styled_content_html(html_content)
        html_content = self.token_style.script_type.get_styled_content(html_content)
        html_content = self.token_style.list_level.get_styled_content_html(html_content)
        html_content = self.token_style.hyperlink_style.get_styled_content_html(html_content)
        return html_content

    def get_label_intersection_percentage(self, label: Label):
        label_bounding_box = Rectangle.from_width_height(
            left=label.left, top=label.top, width=label.width, height=label.height
        )

        return self.bounding_box.get_intersection_percentage(label_bounding_box)

    def get_same_line_tokens(self, page_tokens: list["PdfToken"]):
        top, height = self.bounding_box.top, self.bounding_box.height

        same_line_tokens = [
            each_token
            for each_token in page_tokens
            if top <= each_token.bounding_box.top < (top + height) or top < each_token.bounding_box.bottom <= (top + height)
        ]

        return same_line_tokens

    def get_context(self, page_tokens: list["PdfToken"]):
        left, right = self.bounding_box.left, self.bounding_box.right

        self.pdf_token_context.left_of_token_on_the_left = left

        same_line_tokens = self.get_same_line_tokens(page_tokens)

        on_the_left = [each_token for each_token in same_line_tokens if each_token.bounding_box.right < right]
        on_the_right = [each_token for each_token in same_line_tokens if left < each_token.bounding_box.left]

        if on_the_left:
            self.pdf_token_context.right_of_token_on_the_left = max([x.bounding_box.right for x in on_the_left])
            self.pdf_token_context.left_of_token_on_the_left = min([x.bounding_box.left for x in on_the_left])

        if on_the_right:
            self.pdf_token_context.left_of_token_on_the_right = min([x.bounding_box.left for x in on_the_right])
            self.pdf_token_context.right_of_token_on_the_right = max([x.bounding_box.right for x in on_the_right])
