from pathlib import Path
from unittest import TestCase

from configuration import ROOT_PATH
from pdf_features.PdfFeatures import PdfFeatures
from pdf_features.ScriptType import ScriptType
from pdf_features.TitleType import TitleType
from pdf_features.ListLevel import ListLevel
from pdf_features.HyperlinkStyle import HyperlinkType
from pdf_token_type_labels.TokenType import TokenType


class TestPdfFeatures(TestCase):
    def _get_pdf(self, filename):
        return PdfFeatures.from_pdf_path(Path(ROOT_PATH) / "test_pdfs" / filename)

    def test_only_bold_text(self):
        test_cases = [
            ("deeplearning_paper38.pdf", 204, "1. Introduction", "10.91%"),
            ("ihrda_4.pdf", 75, "ACTS", "2009"),
            ("cejil2.pdf", 71, "REPORT No. 146/18", "ARGENTINA:"),
            ("cyrilla_26.pdf", 23, "COMMUNICATIONS COMMISSION OF KENYA", "11"),
        ]
        for filename, expected_count, first_content, last_content in test_cases:
            with self.subTest(pdf=filename):
                pdf = self._get_pdf(filename)
                bold_tokens = [t for _, t in pdf.loop_tokens() if t.token_style.font.bold and not t.token_style.font.italics]
                self.assertEqual(
                    len(bold_tokens),
                    expected_count,
                    f"Expected {expected_count} bold tokens in {filename}, got {len(bold_tokens)}",
                )
                self.assertEqual(
                    bold_tokens[0].content,
                    first_content,
                    f"First bold token in {filename} should be '{first_content}', got '{bold_tokens[0].content}'",
                )
                self.assertEqual(
                    bold_tokens[-1].content,
                    last_content,
                    f"Last bold token in {filename} should be '{last_content}', got '{bold_tokens[-1].content}'",
                )

    def test_only_italic_text(self):
        test_cases = [
            ("deeplearning_paper41.pdf", 422, "Abstract", "shops"),
            ("ihrda_2.pdf", 56, "Introduction", "Order"),
            ("cejil5.pdf", 228, "ad-hoc", "ad hoc"),
            ("cyrilla_13.pdf", 89, "Fair Hous. Council v. Roommates.com, LLC,", "see also"),
        ]
        for filename, expected_count, first_content, last_content in test_cases:
            with self.subTest(pdf=filename):
                pdf = self._get_pdf(filename)
                italic_tokens = [
                    t for _, t in pdf.loop_tokens() if t.token_style.font.italics and not t.token_style.font.bold
                ]
                self.assertEqual(
                    len(italic_tokens),
                    expected_count,
                    f"Expected {expected_count} italic tokens in {filename}, got {len(italic_tokens)}",
                )
                self.assertEqual(
                    italic_tokens[0].content,
                    first_content,
                    f"First italic token in {filename} should be '{first_content}', got '{italic_tokens[0].content}'",
                )
                self.assertEqual(
                    italic_tokens[-1].content,
                    last_content,
                    f"Last italic token in {filename} should be '{last_content}', got '{italic_tokens[-1].content}'",
                )

    def test_bold_italic_text(self):
        test_cases = [
            ("deeplearning_paper38.pdf", 13, "3.1.1. Data Settings", "Comparison on Test set:"),
            ("cejil2.pdf", 2, "145", "146"),
            ("cejil5.pdf", 29, "et al.", "into  the  facts"),
        ]
        for filename, expected_count, first_content, last_content in test_cases:
            with self.subTest(pdf=filename):
                pdf = self._get_pdf(filename)
                bold_italic_tokens = [
                    t for _, t in pdf.loop_tokens() if t.token_style.font.bold and t.token_style.font.italics
                ]
                self.assertEqual(
                    len(bold_italic_tokens),
                    expected_count,
                    f"Expected {expected_count} bold+italic tokens in {filename}, got {len(bold_italic_tokens)}",
                )
                self.assertEqual(
                    bold_italic_tokens[0].content,
                    first_content,
                    f"First bold+italic token in {filename} should be '{first_content}', got '{bold_italic_tokens[0].content}'",
                )
                self.assertEqual(
                    bold_italic_tokens[-1].content,
                    last_content,
                    f"Last bold+italic token in {filename} should be '{last_content}', got '{bold_italic_tokens[-1].content}'",
                )

    def test_script_type(self):
        test_cases = [
            ("cejil2.pdf", 307, 0, "1", "154"),
            ("cejil_staging14.pdf", 130, 0, "1", "65"),
        ]
        for filename, expected_supers, expected_subs, first_content, last_content in test_cases:
            with self.subTest(pdf=filename):
                pdf = self._get_pdf(filename)
                pdf.set_token_styles()
                superscript_tokens = [t for _, t in pdf.loop_tokens() if t.token_style.script_type == ScriptType.SUPERSCRIPT]
                subscript_tokens = [t for _, t in pdf.loop_tokens() if t.token_style.script_type == ScriptType.SUBSCRIPT]
                self.assertEqual(
                    len(superscript_tokens),
                    expected_supers,
                    f"Expected {expected_supers} superscript tokens in {filename}, got {len(superscript_tokens)}",
                )
                self.assertEqual(
                    len(subscript_tokens),
                    expected_subs,
                    f"Expected {expected_subs} subscript tokens in {filename}, got {len(subscript_tokens)}",
                )
                if superscript_tokens:
                    self.assertEqual(
                        superscript_tokens[0].content,
                        first_content,
                        f"First superscript token in {filename} should be '{first_content}', got '{superscript_tokens[0].content}'",
                    )
                    self.assertEqual(
                        superscript_tokens[-1].content,
                        last_content,
                        f"Last superscript token in {filename} should be '{last_content}', got '{superscript_tokens[-1].content}'",
                    )

    def test_title_type(self):
        test_cases = [
            (
                "deeplearning_paper36.pdf",
                [(1, 2), (1, 3), (1, 4), (13, 54), (13, 55)],
                {
                    (1, 2): TitleType.H1,
                    (1, 3): TitleType.H1,
                    (1, 4): TitleType.H1,
                    (13, 54): TitleType.H4,
                    (13, 55): TitleType.H4,
                },
            ),
            (
                "deeplearning_paper34.pdf",
                [(1, 0), (1, 1), (4, 171), (5, 0)],
                {(1, 0): TitleType.H2, (1, 1): TitleType.H2, (4, 171): TitleType.H3, (5, 0): TitleType.H3},
            ),
            (
                "cyrilla_32.pdf",
                [(1, 3), (1, 5), (3, 3), (10, 19), (10, 22), (10, 23)],
                {
                    (1, 3): TitleType.H2,
                    (1, 5): TitleType.H2,
                    (3, 3): TitleType.H3,
                    (10, 19): TitleType.H4,
                    (10, 22): TitleType.H4,
                    (10, 23): TitleType.H4,
                },
            ),
        ]
        for filename, page_token_index_pairs, expected_types in test_cases:
            with self.subTest(pdf=filename):
                pdf = self._get_pdf(filename)
                for page, token in pdf.loop_tokens():
                    idx = (page.page_number, page.tokens.index(token))
                    if idx in page_token_index_pairs:
                        token.token_type = TokenType.SECTION_HEADER
                pdf.set_token_styles()
                for page, token in pdf.loop_tokens():
                    idx = (page.page_number, page.tokens.index(token))
                    if idx in expected_types:
                        self.assertEqual(
                            token.token_style.title_type,
                            expected_types[idx],
                            f"Token at {idx} in {filename} should be {expected_types[idx]}, got {token.token_style.title_type}",
                        )

    def test_list_level(self):
        contents = [
            " Pulmonary congestion and bleeding. Food intake (aspiración alimenticia). Birefringent crystals polarizing light in airways (bronchi) and air sacs (alveoli).",
            " Subcutaneous bleeding in the lumbar region",
            "• Sub item 1",
            "• Sub item 2",
            "• Sub item 3",
            " Renal passive congestion. Medullary fibroid.",
            "• Sub item 4",
            "• Sub item 5",
            "• Sub item 6",
            " Congestion and diffuse brain edema.",
            "• Sub item 7",
            "⦾ Sub item 8",
            "• Sub item 9",
            "⦾ Sub item 10",
            "⦾ Sub item 11",
        ]
        expected_levels = [
            ListLevel.LEVEL_0,
            ListLevel.LEVEL_0,
            ListLevel.LEVEL_1,
            ListLevel.LEVEL_1,
            ListLevel.LEVEL_1,
            ListLevel.LEVEL_0,
            ListLevel.LEVEL_1,
            ListLevel.LEVEL_1,
            ListLevel.LEVEL_1,
            ListLevel.LEVEL_0,
            ListLevel.LEVEL_1,
            ListLevel.LEVEL_2,
            ListLevel.LEVEL_1,
            ListLevel.LEVEL_2,
            ListLevel.LEVEL_2,
        ]
        list_levels = ListLevel.from_list_contents(contents)
        self.assertEqual(
            list_levels, expected_levels, f"List levels do not match expected: {list_levels} vs {expected_levels}"
        )

    def test_hyperlink_style(self):
        pdf_features = self._get_pdf("cyrilla_13.pdf")
        pdf_features.set_token_styles()
        tokens = [t for _, t in pdf_features.loop_tokens() if t.token_style.hyperlink_style.type == HyperlinkType.WEB_URL]
        link_1 = "https://scholar.google.com/scholar?scidkt=14466714832946854672+12009610805931716007+6361409173314449918&as_sdt=2&hl=en"
        link_2 = (
            "https://scholar.google.com/scholar_case?case=17822437944046994144&q=666+F.3d+1216+&hl=en&as_sdt=2006&scilh=0"
        )
        self.assertEqual(len(tokens), 162, f"Expected 162 hyperlink tokens, got {len(tokens)}")
        self.assertEqual(
            tokens[0].content,
            "Nos. 09-55272, 09-55875, 09-55969.",
            f"First hyperlink token content mismatch: {tokens[0].content}",
        )
        self.assertEqual(
            tokens[0].token_style.hyperlink_style.link,
            link_1,
            f"First hyperlink token link mismatch: {tokens[0].token_style.hyperlink_style.link}",
        )
        self.assertEqual(
            tokens[-1].content,
            "42 Cal.4th 254, 64 Cal.Rptr.3d 390, 165 P.3d 118, 128 (2007);",
            f"Last hyperlink token content mismatch: {tokens[-1].content}",
        )
        self.assertEqual(
            tokens[-1].token_style.hyperlink_style.link,
            link_2,
            f"Last hyperlink token link mismatch: {tokens[-1].token_style.hyperlink_style.link}",
        )
