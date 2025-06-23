import utils as translitutils
def is_devanagari(unicode_point: int) -> bool:
    return True if (unicode_point >= 2304 and unicode_point <= 2431) else False

def allowed_codepoint(unicode_point: int) -> bool:
    return is_devanagari(unicode_point) or translitutils.is_space(unicode_point) or translitutils.is_comma(unicode_point) or translitutils.is_question_mark(unicode_point)

def is_devanagari_token(word: str) -> bool:
    for character in word:
        unicode_point = ord(character)
        if not allowed_codepoint(unicode_point):
            return False
    return True