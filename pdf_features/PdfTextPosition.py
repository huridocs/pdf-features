import tempfile
import subprocess
from pathlib import Path
from lxml import etree
from lxml.etree import ElementBase

from pdf_features import Rectangle
from pdf_features.PdfWord import PdfWord


class PdfTextPosition:
    def __init__(self, pdf_words: list[PdfWord]):
        self.pdf_words = pdf_words

    @staticmethod
    def from_pdf_path(pdf_path: Path | str) -> "PdfTextPosition":
        pdf_words = PdfTextPosition.get_pdf_words(pdf_path)
        return PdfTextPosition(pdf_words=pdf_words)

    @staticmethod
    def get_pdf_words(pdf_path: Path | str) -> list[PdfWord]:
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

    def get_all_pdf_words(self) -> list[PdfWord]:
        return self.pdf_words

    def get_bounding_boxes(self, text: str, search_bounding_box: Rectangle, page_number: int) -> list[PdfWord]:
        filtered_words = [
            word
            for word in self.pdf_words
            if word.page_number == page_number and search_bounding_box.get_intersection_percentage(word.bounding_box) > 0
        ]

        if not filtered_words:
            return []

        search_text = text.strip()
        search_words = search_text.split()

        if not search_words:
            return []

        matches = []

        for start_idx in range(len(filtered_words)):
            match_result = self._find_match_from_position(filtered_words, start_idx, search_words)

            if match_result:
                matched_words, score = match_result
                matches.append((matched_words, score, start_idx))

        if not matches:
            return []

        sorted_matches = sorted(matches, key=lambda x: x[1], reverse=True)

        unique_matches = []
        used_indices = set()

        for matched_words, score, start_idx in sorted_matches:
            word_indices = set(range(start_idx, start_idx + len(matched_words)))

            if not word_indices.intersection(used_indices):
                unique_matches.append(matched_words)
                used_indices.update(word_indices)

        result = []
        for matched_words in unique_matches:
            lines = self._split_words_by_line(matched_words)
            for line_words in lines:
                merged_word = self._merge_adjacent_words(line_words)
                result.append(merged_word)

        return result

    @staticmethod
    def _split_words_by_line(words: list[PdfWord]) -> list[list[PdfWord]]:
        if not words:
            return []

        if len(words) == 1:
            return [words]

        lines = []
        current_line = [words[0]]

        for i in range(1, len(words)):
            current_word = words[i]
            previous_word = words[i - 1]

            prev_top = previous_word.bounding_box.top
            prev_bottom = previous_word.bounding_box.bottom
            prev_height = previous_word.bounding_box.height

            curr_top = current_word.bounding_box.top
            curr_bottom = current_word.bounding_box.bottom

            tolerance = prev_height * 0.3

            top_diff = abs(curr_top - prev_top)
            bottom_diff = abs(curr_bottom - prev_bottom)

            if top_diff <= tolerance and bottom_diff <= tolerance:
                current_line.append(current_word)
            else:
                lines.append(current_line)
                current_line = [current_word]

        if current_line:
            lines.append(current_line)

        return lines

    def _find_match_from_position(
        self, words: list[PdfWord], start_idx: int, search_words: list[str]
    ) -> tuple[list[PdfWord], float] | None:
        if start_idx >= len(words):
            return None

        best_match = None
        best_score = 0

        max_search_length = min(len(search_words) * 3, len(words) - start_idx)

        for end_idx in range(start_idx + 1, start_idx + max_search_length + 1):
            candidate_words = words[start_idx:end_idx]
            candidate_text = " ".join(word.text for word in candidate_words)

            score = self._calculate_match_score(candidate_text, search_words)

            if score > best_score:
                best_score = score
                best_match = candidate_words

        if best_score > 0.6:
            return best_match, best_score

        return None

    @staticmethod
    def _calculate_match_score(candidate_text: str, search_words: list[str]) -> float:
        search_text = " ".join(search_words)

        if candidate_text == search_text:
            return 1.0

        if search_text in candidate_text:
            length_penalty = len(search_text) / max(len(candidate_text), 1)
            return 0.95 * length_penalty

        candidate_words = candidate_text.split()

        if len(candidate_words) == 0:
            return 0.0

        matched_words = 0
        search_idx = 0

        for candidate_word in candidate_words:
            if search_idx >= len(search_words):
                break

            if candidate_word == search_words[search_idx]:
                matched_words += 1
                search_idx += 1

        word_match_ratio = matched_words / len(search_words)

        length_ratio = min(len(candidate_words), len(search_words)) / max(len(candidate_words), len(search_words))

        score = word_match_ratio * 0.7 + length_ratio * 0.3

        return score

    @staticmethod
    def _merge_adjacent_words(words: list[PdfWord]) -> PdfWord:
        if not words:
            raise ValueError("Cannot merge empty list of words")

        if len(words) == 1:
            return words[0]

        merged_text = " ".join(word.text for word in words)
        merged_bbox = Rectangle.merge_rectangles([word.bounding_box for word in words])

        return PdfWord(text=merged_text, bounding_box=merged_bbox, page_number=words[0].page_number)
