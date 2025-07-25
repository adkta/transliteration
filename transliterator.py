from typing import Union, Optional
from pathlib import Path
import json
import re
from transliteration import logger
from transliteration.utils import get_matching_files


class TranslitDict(dict[str, str]):

    _FILE_ENCODING = 'utf-8'
    PUNCT_SPACE_REGEX = r"[\s\.\?\|!\",]+"
    DEFAULT_HEADERS = ("Word","Transliteration")
    DEFAULT_DELIMITER = ","

    @classmethod
    def load(cls, src_path: str, delimiter: str = DEFAULT_DELIMITER, headers: tuple[str] = DEFAULT_HEADERS, encoding: str = _FILE_ENCODING) -> "TranslitDict":
        """
        :param src_path: str transcript file location. Works with json files or delimeter separated files
        :param delimiter: str delimiter used in file (not required if json file source)
        :param headers: tuple[str] headers to be used as keys, values (in order) (not required if json file source)
        :param encoding: str encoding used to convert text to bytes
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
            
    @classmethod
    def from_json_file(cls, src_path:str, encoding:str = _FILE_ENCODING) -> "TranslitDict":
        translit_dict = TranslitDict()
        with open(file = src_path, encoding=encoding) as translit_src_path:
            try:
                translit_dict.update(json.load(fp = translit_src_path))
                return translit_dict
            except json.decoder.JSONDecodeError as e:
                raise json.decoder.JSONDecodeError(f"Could not load transliteration dictionary (TranslitDict object). Reason: BAD JSON FILE: {e.msg}.", doc = e.doc, pos = e.pos)

    @classmethod
    def from_sv_file(cls, src_path: str, delimiter:str = DEFAULT_DELIMITER, headers: tuple[str, str] = DEFAULT_HEADERS, encoding:str = _FILE_ENCODING) -> "TranslitDict":
        if len(headers) != 2:
            raise ValueError("Can only have 2 headers corresponding to word to transliterate and its transliteration")
 
        translit_dict = TranslitDict()
        word_hdr, translitn_hdr = headers
        with open(file = src_path, encoding=encoding) as translit_dict_file:
            first_line_fields:list[str] = translit_dict_file.readline().strip().split(delimiter)
            word_idx:int = 0
            translitn_idx: int = 0

            field_count = len(first_line_fields)
            
            if field_count < 2:
                raise ValueError(f"{len(first_line_fields)} fields present in line 1. Each line must have at least 2 fields!")
            
            if (word_hdr not in first_line_fields) or (translitn_hdr not in first_line_fields):
                if field_count > 2:
                    raise ValueError(f'Provided headers are not present in file {src_path}. Please supply correct headers or check the file.')
                word_idx = 0
                translitn_idx = 1
                translit_dict[first_line_fields[word_idx]] = first_line_fields[translitn_idx]
            else:
                word_idx = first_line_fields.index(word_hdr)
                translitn_idx = first_line_fields.index(translitn_hdr)

            for line in translit_dict_file:
                fields = line.strip().split(delimiter)
                translit_dict[fields[word_idx]] = fields[translitn_idx]
        return translit_dict

    @classmethod
    def create(cls, transcr_src: str, translitr: "Transliterator", encoding:str = _FILE_ENCODING, transcr_name_pattern: str = r"transcript.txt$") -> "TranslitDict":
        """
        Create a transliteration dictionary for given words
        :param transcr_src: str path to the file or folder containing list of words or a corpus. If a folder is provided, one can specify transcr_name_pattern argument. Chooses words using Transliterator.for_transliteration. 
        :param translitrtr: Transliterator Transliterator object with a technique to transliterate
        :param encoding: str File encoding standard used
        :param transcr_name_pattern: str File name pattern (use regex format) to allow choosing file if transcr_src is a directory and not a file
        :return: TranslitDict returns a TranslitDict object
        """
        
        transcr_src_path = Path(transcr_src)
        punct_space = cls.PUNCT_SPACE_REGEX
        tknzr_pattern = re.compile(punct_space)
        if not transcr_src_path.exists():
            raise FileNotFoundError(f"Path {transcr_src_path.absolute()} does not exist!")
        if transcr_src_path.is_file():
            return cls._create_from_file(transcr_src, translitr, tknzr_pattern, encoding)
        if transcr_src_path.is_dir():
            transcr_paths = get_matching_files(data_fol = transcr_src_path, file_pattern = transcr_name_pattern)
            translit_dict = TranslitDict()
            for transcr_path in transcr_paths:
                translit_dict.update(cls._create_from_file(transcr_path, translitr, tknzr_pattern, encoding))
            return translit_dict

    @classmethod
    def _create_from_file(cls, transcr_src: str, translitr: "Transliterator", tknzr_pattern: re.Pattern, encoding:str = _FILE_ENCODING) -> "TranslitDict":
        logger.info(f"Extracting dictionary from file: {transcr_src}...")
        translit_dict = TranslitDict()
        with open(transcr_src, encoding = encoding) as lines:
            for line in lines:
                translit_dict.update(cls._create_from_line(line, translitr, tknzr_pattern))
        return translit_dict
    
    @classmethod
    def _create_from_line(cls, line: str, translitr: "Transliterator", tknzr_pattern: Union[str, re.Pattern]) -> "TranslitDict":
        line.strip()
        if not line:
            return None
        translit_dict = TranslitDict()
        tokens = tknzr_pattern.split(line)
        logger.debug(f"Split into: {tokens}")
        for token in tokens:
            logger.debug(f"Attempting transliteration of {token}...")
            if translitr.for_transliteration(word=token):
                translit_dict[token] = translitr.translit(token)
            logger.debug(f"Transliterated {token} and saved to dictionary")
        return translit_dict

    def export(self, dest_path: str, delimiter: str = DEFAULT_DELIMITER, headers:tuple[str] = DEFAULT_HEADERS, exp_mode:str = 'w', encoding:str = _FILE_ENCODING) -> None:
        """
        Save TranslitDict instance as json or delimiter separated value file based on the extension of destination path
        :param dest_path: str destination path to save the transliteration dictionary in
        :param delimiter: str column separator. Required for non-json files. 
        :param exp_mode: str Either 'w' or 'a'. w for new file or overwriting existing file. 'a' or appending to existing file.
        :return: None 
        """
        translit_dest_path = Path(dest_path)

        if exp_mode not in ['w', 'a']:
            raise ValueError(f"Allowed export/write modes are w for write and a for append. But {exp_mode=} was passed")
        
        if not translit_dest_path.parent.exists():
            translit_dest_path.parent.mkdir(parents=True)
        
        if translit_dest_path.suffix == '.json':
            self.export_to_json(dest_path, exp_mode, encoding)
        else:
            self.export_to_sv(dest_path, delimiter, headers, exp_mode, encoding)
        
    def export_to_json(self, dest_path:str,  exp_mode:str = 'w', encoding:str = _FILE_ENCODING) -> None:
        """
        Save TranslitDict instance as json file based on the extension of destination path
        :param dest_path: str destination path to save the transliteration dictionary in
        :param exp_mode: str Either 'w' or 'a'. w for new file or overwriting existing file. 'a' or appending to existing file.
        :param encoding: str File encoding
        :return: None 
        """
        if exp_mode == 'a':
            self.update(TranslitDict.from_json_file(src_path=dest_path))
        with open(dest_path, mode = 'w', encoding=encoding) as translit_dict_file:
            json.dump(obj=self, fp=translit_dict_file, ensure_ascii=False)

    def export_to_sv(self, dest_path: str, delimiter: str = DEFAULT_DELIMITER, headers:tuple[str] = DEFAULT_HEADERS, exp_mode:str = 'w', encoding:str = _FILE_ENCODING) -> None:
        """
        Save TranslitDict instance as delimiter separated file based on the extension of destination path
        :param dest_path: str destination path to save the transliteration dictionary in
        :param delimiter: str column separator. Required for non-json files. 
        :param exp_mode: str Either 'w' or 'a'. w for new file or overwriting existing file. 'a' or appending to existing file.
        :param encoding: str File encoding
        :return: None 
        """
        word_hdr, translitn_hdr = headers
        if exp_mode == 'a':
            self.update(TranslitDict.from_sv_file(src_path=dest_path, delimiter=delimiter, encoding=encoding))
        with open(dest_path, mode='w', encoding=encoding) as out_translit_dict_file:
            out_translit_dict_file.write(f"{word_hdr}{delimiter}{translitn_hdr}\n")
            for word, translitn in self.items():
                out_translit_dict_file.write(f"{word}{delimiter}{translitn}\n")


class Transliterator():
    """
    The objects of this class can perform transliteration either based on dictionary or rules.
    Provision of a dictionary doesn't need this class to be inherited/extended.
    If rule based transliteration is required, it must be defined in the child class as rules are different for each type 
    of transliteration.
    """

    def __init__(self, *, translit_dict:Union[str, TranslitDict] = None, delimiter:Optional[str] = None, headers: Optional[tuple[str,str]] = None) -> None:
        """
        :param translit_dic: Union[str, TranslitDict] Either a TranslitDict instance or
        filepath to transliteration dictionary.
        When a filepath is provided, column headers corresponding to word and its
        transliteration should also be provided.
        """
        logger.debug("Inside Transliterator init")
        if not translit_dict:
            self.translit_dict = None
        elif (isinstance(translit_dict, str)):
            self.translit_dict = TranslitDict.load(src_path = translit_dict, delimiter=delimiter, headers=headers)
        elif (isinstance(translit_dict, TranslitDict)):
            self.translit_dict = translit_dict

    def for_transliteration(self, word: str) -> bool:
        """
        Check if word is eligible for transliteration. Must be provided in child class. A possible check could be if the word adheres to a given script.
        :param word: str Word to be transliterated
        :return: str Transliteration of the supplied word
        """
        return True if word else False

    def translit(self, word: str) -> Optional[str]:
        """
        Transliterate a word. 
        Performs the following in order: 
            1) Checks if the word is eligible for transliteration (to be implemented in child class)
            2) Try transliterating using dictionary lookup if provided during instantiation.
            3) If couldn't transliterate using dictionary look up, try transliterating using rules which will be provided in the child class. 
        :param word: str Word to be transliterated
        :return: str Transliteration of supplied word
        """
        word = word.strip()
        logger.debug(f"Transliterating {word}...")
        out = self.translit_using_dict(word)
        if not out:
            out = self.translit_using_rules(word)
        if not out:
            logger.info(f"Transliteration failed for {word=}. The word to transliterate wasn't sent in the source script or it isn't present in cmudict.")
        return out

    def translit_using_rules(self, word: str) -> Optional[str]:
        """
        Transliterate a word using rules
        This needs to be implemented in the child class.
        :param word: str Word to be transliterated
        :return: str Transliteration of supplied word
        """
        return None

    def translit_using_dict(self, word: str) -> Optional[str]:
        """
        Transliterate a word using dictionary lookup. 
        If one wants to use a dictionary, dictionary filepath or TranslitDict instance must be supplied during instantiation
        :param word: str Word to be transliterated
        :return: str Transliteration of supplied word
        """
        return self.translit_dict.get(word) if self.translit_dict else None