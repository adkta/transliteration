def is_space(unicode_point: str) -> bool:
    return unicode_point == 32

def is_comma(unicode_point: str) -> bool:
    return unicode_point == 44

def is_question_mark(unicode_point: str) -> bool:
    return unicode_point == 63

def isEnglish(word: str) -> bool:
  return word.isascii()