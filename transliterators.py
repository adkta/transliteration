from nltk.downloader import Downloader
import pandas as pd
from string import digits
import traceback
from typing import Any, Optional
from g2p_en import G2p
from transliteration.transliterator import Transliterator
from transliteration.devanagari.utils import is_devanagari_token
from pathlib import Path
from datetime import datetime
from importlib.resources import files


class RomanToDevaTransliterator(Transliterator):
  """
  Transliteration takes place using
  1)English-ARPABET mapping (http://www.speech.cs.cmu.edu/cgi-bin/cmudict via g2p_en package),
  2)ARPABET-IPA mapping (https://docs.soapboxlabs.com/resources/linguistics/arpabet-to-ipa/ via a file) and
  3)IPA-Devanagari mapping (https://www.scriptsource.org/cms/scripts/page.php?item_id=grapheme_detail&uid=a2ys6pbp2u via an
  updated version of it in a file)
  and additional rule
  """

  _IPA_ARPA_MAP_PATH: str = files("transliteration.mappings").joinpath("IPA_ARPABET_mapping.txt").as_posix()
  _IPA_DEVA_MAP_PATH: str = files("transliteration.mappings").joinpath("IPA_Devanagari_mapping_Adapted_to_Arpabet.txt").as_posix()

  def __init__(self, *, ipa_arpa_path: Optional[str] = None, ipa_deva_path: Optional[str] = None ,**kwargs: Any) -> None:
    super().__init__(**kwargs)
    self._ipa_arpa_path = ipa_arpa_path if ipa_arpa_path else RomanToDevaTransliterator._IPA_ARPA_MAP_PATH
    self._ipa_deva_path = ipa_deva_path if ipa_deva_path else RomanToDevaTransliterator._IPA_DEVA_MAP_PATH
    self._initialize_mappings()

  def for_transliteration(self, word):
    return not is_devanagari_token(word)

  #DEVANAGARI
  @staticmethod
  def isSvara(devanagari_char):
    #Is the character independent Vowel?
    unicode_int = ord(devanagari_char)
    return True if unicode_int >= int('0905', 16) and unicode_int <= int('0914', 16) else False

  @staticmethod
  def isMatra(devanagari_char):
    #Is the character dependent vowel?
    unicode_int = ord(devanagari_char)
    return True if unicode_int >= int('093A', 16) and unicode_int <= int('094C', 16) else False

  @staticmethod
  def isVyanjan(devanagari_char):
    #Is the character dependent vowel?
    unicode_int = ord(devanagari_char)
    return True if unicode_int >= int('0915', 16) and unicode_int <= int('0939', 16) else False

  @staticmethod
  def isNaVariant(devanagari_char):
    #ञ and ण sound very similar to न in a Nepali word. Therefore we remove the disambiguity through logic
    #unicode_int = ord(devanagari_char)
    #return True if unicode_int in [int('091E',16), int('0923',16)] else False
    return True if devanagari_char in ['ञ', 'ण'] else False

  #ARPABET
  #All consonant sounds end and start with consonants
  #All vowel sounds start with a vowel
  #All vowel sounds end with a vowel except of ER (eg bird) (we will say composite vowel)

  @staticmethod
  def isERSound(arpabet_notation, current):
    return True if arpabet_notation[current] == 'ER' else False

  @staticmethod
  def isSoundFullyVowel(arpabet_notation, current):
    #needs arpabet phonemes (list of arpabet codes for the word) and the current position
    #ER sound isn't completely vowel
    if RomanToDevaTransliterator.isERSound(arpabet_notation, current):
      return False
    return RomanToDevaTransliterator.isSoundVowel(arpabet_notation, current)

  @staticmethod
  def isSoundVowel(arpabet_notation, current):
    vowels = ('A','E','I','O','U')
    return True if arpabet_notation[current].capitalize().startswith(vowels) else False

  @staticmethod
  def isSoundConsonant(arpabet_notation, current):
    return not RomanToDevaTransliterator.isSoundVowel(arpabet_notation, current)

  @staticmethod
  def soundStartsWithVowel(arpabet_notation, current):
    return RomanToDevaTransliterator.isSoundVowel(arpabet_notation, current)

  @staticmethod
  def soundEndsWithVowel(arpabet_notation, current):
    return RomanToDevaTransliterator.isSoundFullyVowel(arpabet_notation, current)

  @staticmethod
  def soundStartsWithConsonant(arpabet_notation, current):
    return RomanToDevaTransliterator.isSoundConsonant(arpabet_notation, current)

  @staticmethod
  def soundEndsWithConsonant(arpabet_notation, current):
    return RomanToDevaTransliterator.isERSound(arpabet_notation, current) or RomanToDevaTransliterator.isSoundConsonant(arpabet_notation, current)

  @staticmethod
  def isNextSoundConsonant(arpabet_notation, current):
    if current == len(arpabet_notation) -1:
      return False
    return RomanToDevaTransliterator.soundStartsWithConsonant(arpabet_notation, current+1)

  @staticmethod
  def isPreviousSoundConsonant(arpabet_notation, current):
    if current == 0:
      return False
    return RomanToDevaTransliterator.soundEndsWithConsonant(arpabet_notation, current-1)

  @staticmethod
  def isNextSoundVowel(arpabet_notation, current):
    if current == len(arpabet_notation) -1:
      return False
    return RomanToDevaTransliterator.soundStartsWithVowel(arpabet_notation, current)

  @staticmethod
  def isPreviousSoundVowel(arpabet_notation, current):
    if current == 0:
      return False
    return RomanToDevaTransliterator.soundEndsWithVowel(arpabet_notation, current-1)
  
  def days_since_modification(self, nltk_resource_path: Path):
      modified_datetime = datetime.fromtimestamp(nltk_resource_path.stat().st_mtime)
      current_datetime = datetime.now()
      time_difference = current_datetime - modified_datetime
      return time_difference.days

  def _update_nltk_resources_using_status(self, resource_names: list[str]) -> None:
      dldr = Downloader()
      for resource_name in resource_names:
          if dldr.status(info_or_id=resource_name) == Downloader.INSTALLED:
              continue
          dldr.download(resource_name)
  
  def _update_nltk_resources(self, resource_names: list[str]) -> None:
      dldr = Downloader()
      nltk_resource_dir = Path(dldr.download_dir)
      for resource_name in resource_names:
          if self.days_since_modification(next(nltk_resource_dir.rglob(resource_name))) < 30:
              continue
          dldr.download(resource_name)


  def _load_ipa_arpa_map(self) -> None:
    #IPA_ARPA, Phoneme Unicode List
    self._ipa_arpa_map_df = pd.read_csv(self._ipa_arpa_path, sep='\t', header = 0, comment = '#')
    phoneme_unicodes: list[str] = []
    for phoneme in self._ipa_arpa_map_df['IPA']:
      phoneme_unicode = [hex(ord(chars)) for chars in phoneme]
      phoneme_unicodes.append(phoneme_unicode)
    self._ipa_arpa_map_df['IPA_Unicode'] = phoneme_unicodes

  def _load_ipa_deva_map(self) -> None:
    #IPA_DEVA, Phoneme Unicode List
    self._ipa_deva_map_df = pd.read_csv(self._ipa_deva_path,sep='\t', header = 0, comment='#')
    phoneme_unicodes = []
    phonemes_without_slash: list[str] = []
    for phoneme in self._ipa_deva_map_df["Phonemes"]:
      phoneme = phoneme.strip('/')
      phonemes_without_slash.append(phoneme)
      phoneme_unicode=[hex(ord(chars)) for chars in phoneme]
      phoneme_unicodes.append(phoneme_unicode)
    self._ipa_deva_map_df['IPA_Phoneme'] = phonemes_without_slash
    self._ipa_deva_map_df['IPA_Unicode'] = phoneme_unicodes

  def _assert_complete_mapping(self):
    for phoneme in self._ipa_arpa_map_df["IPA"]:
      ipa_dev_phoneme = set(self._ipa_deva_map_df["IPA_Phoneme"])
      assert phoneme in ipa_dev_phoneme, f'{phoneme} not in IPA-Devanagari mapping. Please review the mapping file: {self._ipa_deva_path}'

  def _initialize_mappings(self):
    self._update_nltk_resources(['cmudict', 'averaged_perceptron_tagger_eng'])
    self._load_ipa_arpa_map()
    self._load_ipa_deva_map()
    self._assert_complete_mapping()

  @staticmethod
  def _get_devanagari_selection(candidate_devanagari_list, arpabet_notation, current_arpabet_position):
    candidate_list_size = len(candidate_devanagari_list)

    if candidate_list_size == 0:
      raise Exception('No candidate in Devanagari List. Review IPA Devanagari Mapping')

    final_deva_list = []
    for deva_symbol in candidate_devanagari_list:

      deva_symbol = deva_symbol.strip('‹› ').strip()
      # print(f"After stripping: {deva_symbol}")

      if RomanToDevaTransliterator.isERSound(arpabet_notation, current_arpabet_position):

        # print("Inside ER Sound")

        prev_consonant = RomanToDevaTransliterator.isPreviousSoundConsonant(arpabet_notation, current_arpabet_position)
        prev_vowel = RomanToDevaTransliterator.isPreviousSoundVowel(arpabet_notation, current_arpabet_position)
        if prev_consonant and RomanToDevaTransliterator.isSvara(deva_symbol[0]):
          continue

        if prev_vowel and (RomanToDevaTransliterator.isSvara(deva_symbol[0])):
          continue

        if current_arpabet_position == 0 and RomanToDevaTransliterator.isVyanjan(deva_symbol[0]):
          continue

      elif RomanToDevaTransliterator.isSoundFullyVowel(arpabet_notation, current_arpabet_position): #sound starts with a vowel (doesn't need to be fully vowel). The first condition

        # print("Inside Fully Vowel")
        if not RomanToDevaTransliterator.isSvara(deva_symbol[0]) and not RomanToDevaTransliterator.isMatra(deva_symbol[0]):
          continue

        prev_consonant = RomanToDevaTransliterator.isPreviousSoundConsonant(arpabet_notation, current_arpabet_position)

        if prev_consonant and RomanToDevaTransliterator.isSvara(deva_symbol[0]):
          continue

        if not prev_consonant and RomanToDevaTransliterator.isMatra(deva_symbol[0]):
          continue

      else:
        #ER arpabet sound needs to be accounted for since it isn't exclusively a vowel or a consonant sound

        # print("Inside Consonant Sound")

        if not RomanToDevaTransliterator.isVyanjan(deva_symbol[0]):
          continue

        if RomanToDevaTransliterator.isNaVariant(deva_symbol[0]):
          continue

        if RomanToDevaTransliterator.isNextSoundConsonant(arpabet_notation, current_arpabet_position) and deva_symbol[len(deva_symbol) - 1] != '्' :
          deva_symbol = "".join([deva_symbol,chr(int('094D', 16))])#add halanta or virama if it isn't already there

      final_deva_list.append(deva_symbol)

    print(final_deva_list)
    if len(final_deva_list) > 1:
      raise Exception("Cannot determine a unique Devanagari output for phonetic unit!")
    return "" if len(final_deva_list) == 0 else final_deva_list[0]

  def _get_devanagari(self, phonetic_spel:str) -> str:
    arpabet_out_len = len(phonetic_spel)

    op_deva_word = []

    arpabet_wo_digits = []
    for i in range(arpabet_out_len):
      phoneme = phonetic_spel[i]
      remove_digits = str.maketrans('', '', digits)
      phoneme = phoneme.translate(remove_digits)
      arpabet_wo_digits.append(phoneme)

    # print(arpabet_wo_digits)
    puncs_spaces = [' ', ',', '.']
    for i in range(arpabet_out_len):
      phoneme = arpabet_wo_digits[i]

      if phoneme in puncs_spaces:
        op_deva_word.append(phoneme)
        continue

      ipa_phoneme = self._ipa_arpa_map_df.loc[self._ipa_arpa_map_df["ARPABET"] == phoneme, 'IPA'].iloc[0] #ipa phoneme from ipa arpabet mapping
      unicodes = [hex(ord(character)) for character in ipa_phoneme] #unicodes needed to distinguish similar looking phoneme alphabets to manually add to ipa devanagari mapping
      # print(f'Arpabet: {arpabet_wo_digits[i]} \t IPA: /{ipa_phoneme}/ \t Unicode: {unicodes}')
      try:
        candidate_devanagari_list = list(self._ipa_deva_map_df.loc[self._ipa_deva_map_df["IPA_Phoneme"]==ipa_phoneme]["Symbol"]) #outputs all possible rows
        # print(candidate_devanagari_list)
        final_deva_symbol = RomanToDevaTransliterator._get_devanagari_selection(candidate_devanagari_list, arpabet_wo_digits, i)
        # print(final_deva_symbol)
        op_deva_word.append(final_deva_symbol)
      except Exception:
        print(traceback.format_exc())
      # print(f'/{ipa_phoneme}/')
    return "".join(op_deva_word)

  def translit_using_rules(self, word: str) -> str:
    """
    To do: include typehints
    """
    g2p = G2p()
    return self._get_devanagari(g2p(word))
  

if __name__ == "__main__":
    transliterator = RomanToDevaTransliterator()
    print(f"{transliterator.translit('institution')}")