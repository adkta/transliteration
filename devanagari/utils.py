from nepali_arabic_num_to_word.nepali_arabic_num_to_word import numeral_type, get_word_from_numeral, DEV_NUM, EN_NUM

import transliteration.utils as translitutils
from transliteration import logger


ENG_WORD = 'eng'
NEP_WORD = 'nep'
NEP_NUM = DEV_NUM #'dev'
ENG_NUM = EN_NUM #'en'


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


def base_word(word: str) -> str:
    """
    Determines the type of base_word based on the script. 
    The type maybe Devanagari numeral ('ne')
    or Roman numeral ('en')
    or Nepali alpha word ('nep') 
    or English alpha word ('eng')
    """
    num_type = numeral_type(word)
    if num_type:
        return num_type #'dev' or 'en'
    if translitutils.isEnglish(word):
        return ENG_WORD
    return NEP_WORD


def handle_plural_case_markers(word:str, sep_deva: bool = False) -> tuple[str, str]:
    """
    Separates case markers or plurals attached to word. Expective text from Nepali-English code-mixed corpus or Nepali corpus
    :param word: str Word to check for case markers
    :param sep_deva: bool if True, separates case markers/plurals suffix from devanagari prefix also. If False, only separates from English, numerals
    :return: tuple[str, int] Returns a tuple of original word and empty string if no case markers. If there are case markers,
                             returns a tuple of space separated word and base word type: eng, nep for words and en, dev for numeral
    """
    idx = find_plural_case_marker(word)
    return split_plural_case_markers(word, idx, sep_deva)


def get_plural() -> str:
    return 'हरु'


def get_case_markers() -> list[str]:
    return ['को', 'लाई', 'बाट', 'मा', 'ले']


def find_plural_case_marker(word: str) -> int:
    plur = get_plural()
    case_markers = get_case_markers()
    idx =  word.find(plur)
    if idx in (0, -1):
        for suff in case_markers:
            if word.endswith(suff):
                idx =  word.rfind(suff)
                if idx != -1:
                    break
    return idx

def split_plural_case_markers(word: str, idx: int, sep_deva: bool = False) -> tuple[str, str]:
    sub_1 = ''
    sub_2 = ''
    base_wrd = ''

    if idx not in  (0,-1):
        sub_1 = word[:idx]
        sub_2 = word[idx:]
        base_wrd = base_word(sub_1)
        if sep_deva or base_wrd != NEP_WORD: #separates if sep_deva is True . If false, separates all cases except for devanagari base word
            word = f"{sub_1} {sub_2}"
    return (word, base_wrd)

