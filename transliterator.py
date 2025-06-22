from typing import Union, Optional
from pathlib import Path
import json

class TranslitDict(dict[str, str]):
    _FILE_ENCODING = 'utf-8'
    @staticmethod
    def load(src_path: str, delimiter: Optional[str] = None, headers: Optional[tuple[str]] = None, encoding: str = _FILE_ENCODING) -> "TranslitDict":
        """
        :param src_path: str transcript file location. Only works with delimeter separated files
        :param delimiter: str delimiter used in file
        :param headers: tuple[str] headers to be used as keys, values (in order)
        :return: "TranslitDict" a transliteration dictionary as an instance of this class

        TO-DO: Add support for empty files
        """
        
        translit_src_path = Path(src_path)

        if not translit_src_path.exists() or not translit_src_path.is_file():
            raise FileNotFoundError(f"Path {src_path} doesn't exist")
        
        if translit_src_path.suffix == '.json':
            return TranslitDict.from_json_file(src_path, encoding)
        else:
            return TranslitDict.from_sv_file(src_path, delimiter, headers, encoding)
            
    @staticmethod
    def from_json_file(src_path:str, encoding:str = _FILE_ENCODING) -> "TranslitDict":
        with open(file = src_path, encoding=encoding) as translit_src_path:
            return json.load(fp = translit_src_path)


    @staticmethod
    def from_sv_file(src_path: str, delimiter:str, headers: tuple[str, str], encoding:str = _FILE_ENCODING) -> "TranslitDict":
        if not delimiter or not headers:
            raise ValueError("No delimiter or header provided")
        
        if len(headers) != 2:
            raise ValueError("Can only have 2 headers corresponding to word to transliterate and its transliteration")
 
        translit_dict = TranslitDict()
        word, translitn = headers
        with open(file = src_path, encoding=encoding) as translit_dict_file:
            hdr_fields:list[str] = translit_dict_file.readline().split(delimiter)
            word_idx:int = hdr_fields.index[word]
            translitn_idx:int = hdr_fields.index[translitn]
            for line in translit_dict_file:
                fields = line.split(delimiter)
                translit_dict[fields[word_idx]] = fields[translitn_idx]
        return translit_dict


    @staticmethod
    def create(transcr_src: str, translitrtr: "Transliterator", encoding:str = _FILE_ENCODING) -> "TranslitDict":
        """
        Create a transliteration dictionary for given words
        :param transcr_src: str path to the file containing list of words to be transliterated (supports one word per line)
        :param translitrtr: Transliterator Transliterator object with a technique to transliterate
        :return: TranslitDict returns a TranslitDict object
        """
        translit_dict = TranslitDict()
        with open(transcr_src, encoding=encoding) as words_to_translit:
            for word in words_to_translit:
                word = word.strip()
                translit_dict[word] = translitrtr.translit(word)
        return translit_dict

    def export(self, dest_path: str, delimiter:str = ',', exp_mode:str = 'w', encoding:str = _FILE_ENCODING) -> None:
        """
        TO-DO - Write append mode for JSON
        """
        translit_dest_path = Path(dest_path)

        if exp_mode not in ['w', 'a']:
            raise ValueError("Allowed export/write modes are w for write and a for append. But {exp_mode=} was passed")
        
        if translit_dest_path.suffix == '.json':
            self.export_to_json(dest_path, exp_mode, encoding)
        else:
            self.export_to_sv(dest_path, delimiter, exp_mode, encoding)
        
    def export_to_json(self, dest_path, exp_mode, encoding:str = _FILE_ENCODING):
        if exp_mode == 'a':
            self = TranslitDict.from_json_file(src_path=dest_path).update(self)
        with open(dest_path, mode = 'w', encoding=encoding) as translit_dest_path:
            json.dump(obj=self, fp=translit_dest_path, ensure_ascii=False)

    def export_to_sv(self, dest_path, delimiter, exp_mode, encoding:str = _FILE_ENCODING):
        with open(dest_path, mode=exp_mode, encoding=encoding) as out_translit_dict_file:
            out_translit_dict_file.write(f"Word{delimiter}Transliteration\n")
            for word, translitn in self.items():
                out_translit_dict_file.write(f"{word}{delimiter}{translitn}\n")




class Transliterator():

    def __init__(self, *, translit_dict:Union[str, TranslitDict] = None, delimiter:Optional[str] = None, headers: Optional[tuple[str,str]] = None) -> None:
        """
        :param translit_dic: Union[str, TranslitDict] Either a TranslitDict instance or
        filepath to transliteration dictionary.
        When a filepath is provided, column headers corresponding to word and its
        transliteration should also be provided.
        """
        print("Inside Transliterator init")
        if not translit_dict:
            self.translit_dict = None
        elif (isinstance(translit_dict, str)):
            self.translit_dict = TranslitDict.load(src_path = translit_dict, delimiter=delimiter, headers=headers)
        elif (isinstance(translit_dict, TranslitDict)):
            self.translit_dict = translit_dict


    def for_transliteration(self, word: str) -> bool:
        return True

    def translit(self, word: str) -> str:
        word = word.strip()
        print(f"Transliterating {word}...")
        if not self.for_transliteration(word):
            return word
        out = self.translit_using_dict(word)
        if not out:
            out = self.translit_using_rules(word)
        if not out:
            out = f"Transliteration failed for {word=}"
        return out

    def translit_using_rules(self, word: str) -> str:
        """
        Transliterate a word using rules
        This needs to be implemented in the child class.
        """
        return None

    def translit_using_dict(self, word: str) -> str:
        """
        Transliterate a word using dictionary lookup.
        """
        return self.translit_dict.get(word) if self.translit_dict else None