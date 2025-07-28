from enum import StrEnum
from pdf_features.Rectangle import Rectangle
from pdf_token_type_labels.TokenType import TokenType


class ScriptType(StrEnum):
    REGULAR = "Regular"
    SUPERSCRIPT = "Superscript"
    SUBSCRIPT = "Subscript"

    @staticmethod
    def _get_same_line_boxes(token_box: Rectangle, page_boxes: list[Rectangle]) -> list[Rectangle]:
        left, top, bottom = token_box.left, token_box.top, token_box.bottom
        page_boxes.remove(token_box)
        height_threshold = max(3, (bottom - top) / 2)
        left_threshold = left * 0.7
        same_line_boxes = [
            each_box
            for each_box in page_boxes
            if not (each_box.bottom < top + height_threshold or bottom - height_threshold < each_box.top)
            and each_box.right > left_threshold
        ]
        return same_line_boxes

    @classmethod
    def from_text_height(
        cls, common_text_height: int, content: str, token_box: Rectangle, page_boxes: list[Rectangle], token_type: TokenType
    ):
        if not content.isdigit():
            return cls.REGULAR
        if token_box.height >= 0.8 * common_text_height:
            return cls.REGULAR
        if token_type in {TokenType.TABLE, TokenType.FORMULA, TokenType.PICTURE}:
            return cls.REGULAR

        same_line_boxes = cls._get_same_line_boxes(token_box, page_boxes)

        if not same_line_boxes:
            return cls.REGULAR

        other_boxes_rectangle = Rectangle.merge_rectangles(same_line_boxes)

        if other_boxes_rectangle.height * 0.8 < token_box.height:
            return cls.REGULAR

        same_line_boxes.append(token_box)
        line_rectangle = Rectangle.merge_rectangles(same_line_boxes)
        middle_of_the_line = line_rectangle.top + line_rectangle.height / 2

        top_distance_to_center = abs(token_box.top - middle_of_the_line)
        bottom_distance_to_center = abs(token_box.bottom - middle_of_the_line)

        if token_box.top >= middle_of_the_line:
            return cls.SUBSCRIPT
        elif token_box.bottom <= middle_of_the_line:
            return cls.SUPERSCRIPT

        if top_distance_to_center >= bottom_distance_to_center:
            return cls.SUPERSCRIPT
        else:
            return cls.SUBSCRIPT

    def get_styled_content(self, content: str) -> str:
        if self == ScriptType.SUPERSCRIPT:
            return f"<sup>{content}</sup>"
        if self == ScriptType.SUBSCRIPT:
            return f"<sub>{content}</sub>"
        return content
