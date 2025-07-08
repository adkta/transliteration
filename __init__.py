import logging
from pathlib import Path

_log_path = Path("./transliteration/logs/transliteration.log")
if not _log_path.parent.exists():
    _log_path.parent.mkdir()

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
_handler = logging.FileHandler(_log_path, mode = "w")
_handler.setLevel(logging.WARNING)
_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(_handler)