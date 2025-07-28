from pathlib import Path
from os.path import join

ROOT_PATH = Path(__file__).parent.parent.absolute()
XML_NAME = "etree.xml"
LABELS_FILE_NAME = "labels.json"
TOKEN_TYPE_RELATIVE_PATH = join("labeled_data", "token_type")
