from transliteration.transliterator import TranslitDict
from transliteration.transliterators import RomanToDevaTransliterator
from importlib.resources import files

PROJECT_DIR = files("transliteration").joinpath("").as_posix()
if __name__ == "__main__":
    
    translit_dict = TranslitDict.create(transcr_src = f"{PROJECT_DIR}/test/data/transcript_test/", translitr = RomanToDevaTransliterator())
    translit_dict.export(f"{PROJECT_DIR}/test/data/transcript_test_out/json_transcript.json")
    translit_dict.export(f"{PROJECT_DIR}/test/data/transcript_test_out/csv_transcript.csv")