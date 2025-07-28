from enum import IntEnum
from pdf_token_type_labels.TokenType import TokenType

LIST_INDICATORS = {"-", "•", "", "‣", "⁃", "⁌", "⁍", "◘", "◦", "⦾", "⦿"}


class ListLevel(IntEnum):
    NO_LEVEL = -1
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3

    @staticmethod
    def from_list_contents(contents: list[str]) -> list["ListLevel"]:
        list_levels: list[ListLevel] = []
        seen_list_indicators: list[str] = []

        for content in contents:
            stripped = content.lstrip()
            if not stripped:
                list_levels.append(ListLevel.NO_LEVEL)
                continue

            first_character = stripped[0]
            if first_character not in LIST_INDICATORS:
                list_levels.append(ListLevel.NO_LEVEL)
                continue

            if first_character not in seen_list_indicators:
                seen_list_indicators.append(first_character)

            level_index = min(seen_list_indicators.index(first_character), 3)
            list_levels.append(ListLevel(level_index))

        return list_levels

    def get_styled_content_markdown(self, content: str) -> str:
        if self == ListLevel.NO_LEVEL:
            return content
        indentation = "  " * self
        return f"{indentation}- {content[1:]}"

    def get_styled_content_html(self, content: str) -> str:
        if self == ListLevel.NO_LEVEL:
            return content
        html = content
        for _ in range(self):
            html = f"<ul><li>{html}</li></ul>"
        return html
