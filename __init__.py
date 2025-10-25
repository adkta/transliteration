import logging
from pathlib import Path
from importlib.resources import files

# _log_path = Path("./transliteration/logs/transliteration.log")
_log_path = files("transliteration.logs").joinpath("transliteration.log")
if not _log_path.parent.exists():
    _log_path.parent.mkdir()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_handler = logging.FileHandler(_log_path, mode = "w")
_handler.setLevel(logging.INFO)
_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(_handler)