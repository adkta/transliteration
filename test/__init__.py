import sys
print(sys.path)
from transliterator import TranslitDict
from transliterators import RomanToDevaTransliterator

def create_and_export():
    translit_dict = TranslitDict.create(transcr_src='./test/data/words_2_transliterate.txt', translitrtr=RomanToDevaTransliterator())
    translit_dict.export(dest_path='./test/data/translit_dict.json')

def load():
    translit_dict = TranslitDict.load(src_path='./test/data/translit_dict.json')
    print(f"Word=Transliteration")
    for word, transltrn in translit_dict.items():
        print(f"{word}={transltrn}")

if __name__ == "__main__":
    load()
