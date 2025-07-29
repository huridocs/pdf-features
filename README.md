
<h3 align="center">PDF Features</h3>
<p align="center">A Python library for extracting and analyzing features from PDF documents using XML parsing and machine learning techniques.</p>



## Features

- **`pdf_features`**: Core PDF feature extraction and analysis
- **`pdf_token_type_labels`**: Token type classification and labeled data handlingfrom_rectangle

### PDF Features Module
- Extract text tokens and their bounding boxes from PDF documents
- Analyze font information and text styling
- Parse XML-based PDF representations
- Handle PDF token styling

### Token Type Labels Module
- **Token Type Classification**: Support for 11 different token types:
  - Formula, Footnote, List item, Table, Picture
  - Title, Text, Page header, Section header, Caption, Page footer
- **Labeled Data Management**: Load and process labeled training data
- **Task Mistakes Tracking**: Track and analyze classification mistakes
- **Table of Contents**: Handle different indentation levels

## Installation

> **System Requirements:**
>
> This project requires [Poppler](https://poppler.freedesktop.org/) to be installed on your system. Poppler provides the tools for PDF rendering and conversion.
>
> **Poppler Installation Recommendation:**
>
> This project uses `pdftohtml`, which comes with Poppler. The recommended way to install Poppler is via your system's package manager. On Ubuntu/Debian, use:
>
> ```bash
> sudo apt-get install poppler-utils
> ```
>
> On macOS, use:
>
> ```bash
> brew install poppler
> ```
>
> **Version 24.02.0 of Poppler is known to work well with this project.** Installing Poppler from source or using other versions (especially newer ones) may cause issues with PDF processing. If you encounter problems, please ensure you are using Poppler 24.02.0 installed via your package manager.

Install the Python package:

```bash
pip install git+https://github.com/huridocs/pdf-features.git
```

## Usage

### Basic PDF Feature Extraction

```python
# Load PDF features from XML representation
pdf_features = PdfFeatures.from_pdf_path("/path/to/pdf.pdf")

# Access pages and tokens
for page in pdf_features.pages:
    print(f"Page: {page}")
    for token in page.tokens:
        print(f"Token: {token}")
```


### Token Type Utilities

```python
from pdf_token_type_labels import TokenType

# Convert from text to token type
token_type = TokenType.from_text("List item")  # Returns TokenType.LIST_ITEM

# Convert from index to token type
token_type = TokenType.from_index(2)  # Returns TokenType.LIST_ITEM

# Get token type index
index = TokenType.TITLE.get_index()  # Returns 5
```

### PDF Label Utilities

You can use `PdfLabels`, `PageLabels`, and `Label` to assign and retrieve token types for specific bounding boxes on PDF pages. This is useful for managing labeled data or for downstream processing that requires token type information.

```python
from pdf_token_type_labels import PdfLabels, PageLabels, Label, TokenType
from pdf_features.Rectangle import Rectangle

# Create a bounding box for a token (left, top, right, bottom)
token_bbox = Rectangle.from_coordinates(100, 200, 200, 220)

# Create a label for this bounding box with a specific token type (e.g., TITLE)
label = Label.from_rectangle(token_bbox, TokenType.TITLE.get_index())

# Create a PageLabels object for page 1 and add the label
page_labels = PageLabels(number=1, labels=[label])

# Create a PdfLabels object with the page labels
pdf_labels = PdfLabels(pages=[page_labels])

# Retrieve the label type for a given bounding box on page 1
label_type_index = pdf_labels.get_label_type(1, token_bbox)
label_type = TokenType.from_index(label_type_index)
print(f"Token type for bounding box: {label_type}")  # Output: TokenType.TITLE
```

### Using Labels with Actual Documents

You can load token type labels from a file and apply them to a PDF document using `PdfFeatures`. This is useful for working with labeled datasets or for evaluating model predictions against ground truth labels.

```python
from pdf_features.PdfFeatures import PdfFeatures
from pdf_token_type_labels.TokenType import TokenType

# Path to your PDF and its corresponding labels file
pdf_path = "/path/to/document.pdf"
labels_path = "/path/to/labels.json"  # This should be a JSON file in the expected format

# Load PDF features from the PDF file
pdf_features = PdfFeatures.from_pdf_path(pdf_path)

# Load labels from the labels file
labels = PdfFeatures.load_labels(labels_path)

# Set the token types in the PDF features using the loaded labels
pdf_features.set_token_types(labels)

# Now you can access the token types for each token
for page in pdf_features.pages:
    for token in page.tokens:
        print(f"Token: {token.content}, Type: {token.token_type}")
        # If you want the string name:
        print(f"Token type name: {TokenType.from_index(token.token_type)}")
```

## Advanced Features

### Text Styling Analysis


_Some of the text stylings requires token types to be set (like, while deciding TitleType). As default, all tokens have the type "Text"._

```python
# Set token styles based on text analysis
pdf_features.set_token_styles()

for page, token in pdf_features.loop_tokens():
    print(f"Script style: {token.token_style.script_style}")
    print(f"Title type: {token.token_style.title_type}")
    print(f"List level: {token.token_style.list_level}")
```




## About

**_The project has been developed and maintained by [HURIDOCS](https://huridocs.org), a global non-profit that builds open-source technology and strategies to make human rights information accessible._**



> **About HURIDOCS**
>
> [HURIDOCS](https://huridocs.org) (Human Rights Information and Documentation Systems) is a non-profit organization that supports human rights defenders by developing tools and strategies to organize, analyze, and make sense of information. We work with hundreds of partners worldwide to improve access to justice and accountability. Learn more about our work and mission at [huridocs.org](https://huridocs.org).




## License

MIT License