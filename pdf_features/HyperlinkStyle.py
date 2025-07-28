from enum import StrEnum
from lxml.etree import ElementBase
from pydantic import BaseModel


class HyperlinkType(StrEnum):
    WEB_URL = "Web url"
    DOCUMENT_REFERENCE = "Document reference"
    NO_LINK = "No link"


class HyperlinkStyle(BaseModel):
    link_text: str = ""
    link: str = ""
    type: HyperlinkType = HyperlinkType.NO_LINK

    @staticmethod
    def from_xml_tag(xml_tag: ElementBase, content: str) -> "HyperlinkStyle":
        links = xml_tag.findall(".//a")
        if not links:
            return HyperlinkStyle(link_text="", link="", type=HyperlinkType.NO_LINK)

        link_element = links[0]
        link = link_element.attrib.get("href", "")
        if not link:
            return HyperlinkStyle(link="", type=HyperlinkType.NO_LINK)

        link_text = "".join(link_element.itertext()).strip()
        if link.startswith("http"):
            # if link_text == content:
            if link_text and link_text in content:
                return HyperlinkStyle(link_text=link_text, link=link, type=HyperlinkType.WEB_URL)
            else:
                return HyperlinkStyle(link_text="", link="", type=HyperlinkType.NO_LINK)
        else:
            return HyperlinkStyle(link_text=link_text, link=link, type=HyperlinkType.DOCUMENT_REFERENCE)

    def get_styled_content_markdown(self, content: str) -> str:
        if self.type != HyperlinkType.WEB_URL:
            return content
        return f"{content.replace(self.link_text, f'[{self.link_text}]')}({self.link})"

    def get_styled_content_html(self, content: str) -> str:
        if self.type != HyperlinkType.WEB_URL:
            return content
        return content.replace(self.link_text, f'<a href="{self.link}">{self.link_text}</a>')
