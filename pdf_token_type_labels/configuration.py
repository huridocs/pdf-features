from pathlib import Path
from os.path import join

ROOT_PATH = Path(__file__).parent.parent.absolute()
LABELS_FILE_NAME = "labels.json"
MISTAKES_RELATIVE_PATH = join("labeled_data", "task_mistakes")
STATUS_FILE_NAME = "status.txt"
