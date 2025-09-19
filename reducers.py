from typing import Optional

from transliteration.transliterators import RomanToDevaTransliterator

class DevanagariReducer(RomanToDevaTransliterator):
    def for_transliteration(self, word: str) -> bool:
        return True if word else False

    def translit_using_rules(self, word: str) -> Optional[str]:
        translit_word = super().translit_using_rules(word)
        if not translit_word:
            translit_word = word
        reduced_word = self.get_reduced_devanagari_word(translit_word)
        if reduced_word == word:
            return None
        return reduced_word

    def get_reduced_devanagari_word(self, deva_word: str) -> str:
        reduced_word = []
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
