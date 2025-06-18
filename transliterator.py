from typing import NamedTuple, Callable, Union, Optional
from abc import ABC, abstractmethod

class TranslitDict(dict[str, str]):
    
    @staticmethod
    def load (src_path: str, delimiter: str, headers: tuple[str]) -> "TranslitDict":
        ...

    @staticmethod
    def create(self, transcr_src: str, transliterator: "Transliterator") -> "TranslitDict":
        ...
        return self

    def export(self, dest_path: str) -> None:
        ...


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


    def translit(self, word: str) -> str:
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