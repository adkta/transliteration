from transliteration import logger

def get_reduced_devanagari_word(deva_word: str) -> str:
    reduced_word = []
    logger.debug(deva_word)
    for ch in deva_word:
        if ch == 'ई':
            reduced_word.append('इ')
        elif ch == 'ऊ':
            reduced_word.append('उ')
        elif ord(ch) == int('0901', 16): #chandrabindu to bindu
            reduced_word.append(chr(int('0902', 16)))
        elif ord(ch) == int('0940', 16): #dirgha ikaar to hraswa
            reduced_word.append(chr(int('093F', 16)))
        elif ord(ch) == int('0942', 16): #dirgha ukaar to hraswa
            reduced_word.append(chr(int('0941', 16)))
        elif ch in ['श', 'ष']:
            reduced_word.append('स')
        else:
            reduced_word.append(ch)
    return "".join(reduced_word)
