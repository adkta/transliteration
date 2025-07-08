import os
from typing import Generator
import re

def is_space(unicode_point: str) -> bool:
    return unicode_point == 32

def is_comma(unicode_point: str) -> bool:
    return unicode_point == 44

def is_question_mark(unicode_point: str) -> bool:
    return unicode_point == 63

def isEnglish(word: str) -> bool:
  return word.isascii()

def get_matching_files(data_fol: str, file_pattern: str) -> Generator[str, None, None]:
        file_pattern = re.compile(file_pattern)
        for dirpath, dirs, files in os.walk(data_fol):
            for f in files:
                if file_pattern.search(f):
                    yield os.path.join(dirpath, f)