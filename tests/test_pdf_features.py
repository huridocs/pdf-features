from os.path import join
from unittest import TestCase

from pdf_features.configuration import ROOT_PATH
from pdf_features.PdfFeatures import PdfFeatures


class TestPdfFeatures(TestCase):
    def test_wrong_pdf(self):
        not_a_pdf_path = join(ROOT_PATH, "test_pdfs", "not_a_pdf.pdf")
        print(not_a_pdf_path)
        pdf_features = PdfFeatures.from_pdf_path(not_a_pdf_path)
        self.assertIsNone(pdf_features)

    def test_blank_xml(self):
        pdf_features_empty = PdfFeatures.from_poppler_etree_content("", "")
        pdf_features_empty_list = PdfFeatures.from_poppler_etree_content("", "[]")
        self.assertNotEqual(pdf_features_empty, None)
        self.assertNotEqual(pdf_features_empty_list, None)

    def test_ocr_pdf(self):
        pdf_features = PdfFeatures.from_pdf_path(join(ROOT_PATH, "test_pdfs", "ocr_pdf.pdf"))
        self.assertGreater(len(pdf_features.pages[0].tokens), 0)

    def test_from_poppler_etree_string(self):
        xml_path = join(ROOT_PATH, "test_pdfs", "cejil2.xml")
        with open(xml_path, "r") as f:
            xml_content = f.read()
        pdf_features = PdfFeatures.from_poppler_etree_string(xml_content, "cejil2.xml", "test_dataset")
        self.assertIsNotNone(pdf_features)
        self.assertEqual(pdf_features.file_name, "cejil2.xml")
        self.assertEqual(pdf_features.file_type, "test_dataset")
        self.assertEqual(len(pdf_features.pages), 23)
