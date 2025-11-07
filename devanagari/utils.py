import transliteration.utils as translitutils
from transliteration import logger

def is_devanagari(unicode_point: int) -> bool:
    if (unicode_point >= 2304 and unicode_point <= 2431):
        return True 
    return False

def allowed_codepoint(unicode_point: int) -> bool:
    if translitutils.is_space(unicode_point):
        return True
    if translitutils.is_comma(unicode_point):
        return True
    if translitutils.is_question_mark(unicode_point):
        return True
    if translitutils.is_percentage(unicode_point):
        return True
    if translitutils.is_ZWNJ(unicode_point):
        return True
    if translitutils.is_ZWJ(unicode_point):
        return True
    if translitutils.is_LRM(unicode_point):
        return True
    if is_devanagari(unicode_point):
        return True
    if translitutils.is_Devanagari_period(unicode_point):
        return True
    return False


def is_devanagari_token(word: str) -> bool:
    for character in word:
        unicode_point = ord(character)
        if not allowed_codepoint(unicode_point):
            logger.debug(f"{character} with unicode {unicode_point} not allowed in Devanagari")
            return False
    return True