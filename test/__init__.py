import sys
print(sys.path)
from transliterator import TranslitDict
from transliterators import RomanToDevaTransliterator
from json import JSONDecodeError

def create_and_export():
    translit_dict = TranslitDict.create(transcr_src='./test/data/words_2_transliterate.txt', translitrtr=RomanToDevaTransliterator())
    translit_dict.export(dest_path='./test/data/created_translit_dict.json')

def load_from_json(src_path:str) -> None:
    translit_dict = TranslitDict.load(src_path = src_path)
    print_translit_dict(translit_dict, 5)

def print_translit_dict(translit_dict: TranslitDict, num: int = 10) -> None:
    print(f"Word=Transliteration")
    count = 0
    if not translit_dict:
        print("No or empty TranslitDict instance. Nothing to print. Returning")
        return
    for word, transltrn in translit_dict.items():
        print(f"{word}={transltrn}")
        count += 1
        if count == 5:
            break

def load_from_csv(src_path: str, delimiter: str, headers: tuple[str, str]) -> None:
    translit_dict = TranslitDict.load(src_path=src_path, delimiter=delimiter, headers=headers)
    print_translit_dict(translit_dict, 5)

def load_from_empty_json():
    load_from_json(src_path='./test/data/empty_translit_dict.json')

def load_from_empty_csv():
    load_from_csv(src_path='./test/data/empty_translit_dict.csv', delimiter=',', headers=('Word', 'Transliteration'))

def print_title(title: str):
    marker = "".join(['-' for i in range(len(title))])
    print(f"\n\n{marker}\n{title}\n{marker}")

def main():

    print_title("TESTING NON-EMPTY JSON LOAD")
    load_from_json(src_path='./test/data/translit_dict.json')
    print_title(f"TESTING NON-EMPTY SV FILE LOAD")
    load_from_csv(src_path='./test/data/translit_dict.csv', delimiter=',', headers=('Word', 'Transliteration'))

    try:
        print_title(f"TESTING EMPTY JSON LOAD")
        load_from_empty_json()
    except JSONDecodeError as e:
        print("Unable to decode empty json file", e)

    print_title(f"TESTING EMPTY SV FILE LOAD")
    load_from_empty_csv()

if __name__ == "__main__":
    main()
