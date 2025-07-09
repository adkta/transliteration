from transliteration.transliterator import TranslitDict
from transliteration.transliterators import RomanToDevaTransliterator
from transliteration.test import print_title
from importlib.resources import files

PROJECT_DIR = files("transliteration").joinpath("").as_posix()

def create() -> TranslitDict:
    print_title("CREATING DICTIONARY")
    translit_dict = TranslitDict.create(transcr_src = f"{PROJECT_DIR}/test/data/transcript_test/", translitr = RomanToDevaTransliterator())
    print(f"Type={type(translit_dict)}\nLen={len(translit_dict)}")
    return translit_dict

def export_various_modes(translit_dict: TranslitDict) -> None:
    print_title("EXPORTING UNDER WRITE MODE")
    translit_dict.export(f"{PROJECT_DIR}/test/data/transcript_test_out/json_transcript.json")
    translit_dict.export(f"{PROJECT_DIR}/test/data/transcript_test_out/csv_transcript.csv")
    print_title("EXPORTING THE SAME DICTIONARY TO THE SAME FIELS UNDER APPEND MODE")
    translit_dict.export(f"{PROJECT_DIR}/test/data/transcript_test_out/json_transcript.json", exp_mode='a')
    translit_dict.export(f"{PROJECT_DIR}/test/data/transcript_test_out/csv_transcript.csv", exp_mode = 'a')

def load_from_exported_files(translit_dict: TranslitDict) -> None:
    print_title("LOAD FROM CSV")
    translit_dict = TranslitDict.load(f"{PROJECT_DIR}/test/data/transcript_test_out/csv_transcript.csv")
    print(f"Type={type(translit_dict)}\nLen={len(translit_dict)}")
    print_title("LOAD FROM JSON")
    translit_dict = TranslitDict.load(f"{PROJECT_DIR}/test/data/transcript_test_out/json_transcript.json")
    print(f"Type={type(translit_dict)}\nLen={len(translit_dict)}")


if __name__ == "__main__":    
    translit_dict = create()
    export_various_modes(translit_dict)
    load_from_exported_files(translit_dict)

