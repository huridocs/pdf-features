from pathlib import Path
import fitz
from pdf_features.PdfTextPosition import PdfTextPosition
from pdf_features.Rectangle import Rectangle


def check_pdf_text_position():
    pdf_path = Path("test_pdfs/resolution.pdf")

    print(f"Loading PDF: {pdf_path}")
    pdf_text_position = PdfTextPosition.from_pdf_path(pdf_path)

    search_text = "affirming the\ninadmissibility"
    page_number = 1
    search_bbox = Rectangle.from_coordinates(0, 0, 700, 700)

    print(f"Searching for text: {repr(search_text)}")
    print(f"Page: {page_number}")
    print(f"Search bounding box: {search_bbox}")

    results = pdf_text_position.get_bounding_boxes(search_text, search_bbox, page_number)

    print(f"\nFound {len(results)} match(es):")
    for i, word in enumerate(results):
        print(f"  Match {i + 1}: '{word.text}'")
        print(f"    Bounding box: {word.bounding_box}")

    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]

    for word in results:
        bbox = word.bounding_box
        rect = fitz.Rect(bbox.left, bbox.top, bbox.right, bbox.bottom)
        page.draw_rect(rect, color=(1, 0, 0), width=2)

    output_path = Path("data/output_with_bounding_boxes.pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    doc.close()

    print(f"\nOutput saved to: {output_path}")


if __name__ == "__main__":
    check_pdf_text_position()
