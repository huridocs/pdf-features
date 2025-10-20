from os.path import join
from unittest import TestCase

from pdf_features.configuration import ROOT_PATH
from pdf_features.PdfTextPosition import PdfTextPosition
from pdf_features.Rectangle import Rectangle


class TestPdfTextPosition(TestCase):
    def setUp(self):
        pdf_path = join(ROOT_PATH, "test_pdfs", "cejil2.pdf")
        self.pdf_text_position = PdfTextPosition.from_pdf_path(pdf_path)

    def test_get_pdf_words(self):
        self.assertIsNotNone(self.pdf_text_position.pdf_words)
        self.assertGreater(len(self.pdf_text_position.pdf_words), 0)

    def test_pdf_words_have_correct_structure(self):
        first_word = self.pdf_text_position.pdf_words[0]
        self.assertIsNotNone(first_word.text)
        self.assertIsNotNone(first_word.bounding_box)
        self.assertIsNotNone(first_word.page_number)
        self.assertGreater(first_word.page_number, 0)

    def test_get_bounding_boxes_exact_match(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("REPORT No. 146/18", search_box, 1)

        self.assertGreater(len(results), 0)
        self.assertIn("REPORT", results[0].text)
        self.assertEqual(results[0].page_number, 1)

    def test_get_bounding_boxes_case_sensitive(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("report no. 146/18", search_box, 1)

        self.assertEqual(len(results), 0)

    def test_get_bounding_boxes_merges_adjacent_words(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("JOSÉ DELFÍN ACOSTA MARTINEZ", search_box, 1)

        self.assertGreater(len(results), 0)
        self.assertIn("JOSÉ", results[0].text)
        self.assertIn("DELFÍN", results[0].text)
        self.assertIn("ACOSTA", results[0].text)

    def test_get_bounding_boxes_multiple_instances(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("José Delfín Acosta", search_box, 2)

        self.assertGreater(len(results), 0)
        for result in results:
            self.assertEqual(result.page_number, 2)

    def test_get_bounding_boxes_partial_match(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("petitioners stated that", search_box, 2)

        self.assertGreater(len(results), 0)
        self.assertIn("petitioners", results[0].text.lower())

    def test_get_bounding_boxes_with_special_characters(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("Martínez", search_box, 2)

        self.assertGreater(len(results), 0)

    def test_get_bounding_boxes_filtered_by_page(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results_page_1 = self.pdf_text_position.get_bounding_boxes("REPORT", search_box, 1)
        results_page_2 = self.pdf_text_position.get_bounding_boxes("REPORT", search_box, 2)

        self.assertGreater(len(results_page_1), 0)
        for result in results_page_1:
            self.assertEqual(result.page_number, 1)

        self.assertEqual(len(results_page_2), 0)

    def test_get_bounding_boxes_filtered_by_bounding_box(self):
        top_half_box = Rectangle.from_coordinates(0, 0, 612, 400)
        bottom_half_box = Rectangle.from_coordinates(0, 400, 612, 792)

        results_top = self.pdf_text_position.get_bounding_boxes("REPORT", top_half_box, 1)
        results_bottom = self.pdf_text_position.get_bounding_boxes("REPORT", bottom_half_box, 1)

        self.assertGreater(len(results_top), 0)
        self.assertEqual(len(results_bottom), 0)

    def test_get_bounding_boxes_long_phrase(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("detained when he was talking to a Brazilian", search_box, 2)

        self.assertGreater(len(results), 0)
        self.assertIn("detained", results[0].text.lower())
        self.assertIn("brazilian", results[0].text.lower())

    def test_get_bounding_boxes_no_match(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("this text does not exist in the document", search_box, 1)

        self.assertEqual(len(results), 0)

    def test_get_bounding_boxes_empty_search(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("", search_box, 1)

        self.assertEqual(len(results), 0)

    def test_get_bounding_boxes_date_format(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("DECEMBER 7, 2018", search_box, 1)

        self.assertGreater(len(results), 0)
        self.assertIn("DECEMBER", results[0].text)

    def test_get_bounding_boxes_with_numbers(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("April 5, 1996", search_box, 2)

        self.assertGreater(len(results), 0)
        self.assertIn("April", results[0].text)
        self.assertIn("1996", results[0].text)

    def test_bounding_box_coordinates_are_valid(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("REPORT", search_box, 1)

        self.assertGreater(len(results), 0)
        bbox = results[0].bounding_box
        self.assertGreater(bbox.right, bbox.left)
        self.assertGreater(bbox.bottom, bbox.top)
        self.assertGreaterEqual(bbox.left, 0)
        self.assertGreaterEqual(bbox.top, 0)

    def test_get_bounding_boxes_fuzzy_matching(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("Argentine Federal Police", search_box, 2)

        self.assertGreater(len(results), 0)
        self.assertIn("Argentine", results[0].text)
        self.assertIn("Police", results[0].text)

    def test_get_bounding_boxes_all_instances_on_page(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("the", search_box, 2)

        self.assertGreater(len(results), 5)
        for result in results:
            self.assertEqual(result.page_number, 2)
            self.assertIn("the", result.text.lower())

    def test_get_bounding_boxes_preserves_original_text(self):
        search_box = Rectangle.from_coordinates(0, 0, 612, 792)
        results = self.pdf_text_position.get_bounding_boxes("José Delfín", search_box, 2)

        self.assertGreater(len(results), 0)
        self.assertIn("José", results[0].text)
