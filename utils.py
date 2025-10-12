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

def get_reverse_dict(dictionary: dict[str, str]) -> dict[str, list[str]]:
    """
    :param dictionary: dict[str, str]
    :return: dict[str, list[str]] Returns a reverse dictionary with values being list to account for many-to-one key-value relationships in original dictionary
    """
    reverse_dict = dict()
    for k,v in dictionary.items():
        if v in reverse_dict:
            reverse_dict[v].append(k)
        else:
            reverse_dict[v] = [k]
    return reverse_dict
