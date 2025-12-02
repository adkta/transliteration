from typing import Optional
from symspellpy import Verbosity
from symspellpy.suggest_item import SuggestItem
from transliteration.disambiguation import get_native_candidates, native_scoring, scoring, language_model_score, combined_scoring
from transliteration.devanagari.utils import sep_plural_n_case_markers, NEP_WORD, word_is_split

def correct_spelling(word:str, sym_spell, edit_dist: Optional[int] = None)-> set[str]:
    spell_corrs = [word]
    if sym_spell:
        sugg_item_list: list[SuggestItem] = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2, include_unknown=True)
        spell_corrs = {sugg_item.term for sugg_item in sugg_item_list}
    return spell_corrs

def split_plural_n_case_markers(sen: str, reverse_dict:Optional[dict] = None, sep_deva:bool = False) -> str:
    """
    Separate case markers from words in a sentence.
    """
    words = get_words_from_sentence(sen)
    out_words = list()
    for word in words:
        if not reverse_dict or (word not in reverse_dict): #split if word isn't found in reduc dict
            sep_wrd, base_type = sep_plural_n_case_markers(word, sep_deva)
            if word_is_split(base_type, sep_deva): 
                base_wrd = sep_wrd.split()[0]
                if not reverse_dict or (base_wrd in reverse_dict): # We honour the split if word is found in reduc dict
                    word = sep_wrd
        out_words.append(word)
    return " ".join(out_words)

def get_words_from_sentence(sentence: str)-> list:
    return sentence.split(" ")

def get_native_sentence(score_map: dict[str, dict[str, float]]) -> str:
    native_sentence = []
    for red_word in score_map:
        native_sentence.append(max(score_map[red_word], key=score_map[red_word].get))
    return " ".join(native_sentence)

def disambiguate(sentence: str, model, reverse_dict, sym_spell, edit_dist: Optional[int] = None, lang_scoring:bool = True) -> str:
    words = get_words_from_sentence(sentence)
    nativ_scored_map: dict[str, dict[str, float]] = dict() #values will also have native scoring. Therefore we opt for dict data type for values
    for word in words:
        spell_corrs = correct_spelling(word, sym_spell)
        candidates = get_native_candidates(spell_corrs, reverse_dict)
        scored_candidates = native_scoring(candidates)
        nativ_scored_map[word] = scored_candidates

    norm_lang_scored_map = dict()
    if lang_scoring:
        norm_lang_scored_map = scoring(nativ_scored_map, window_size = 5)
    else:
        norm_lang_scored_map = nativ_scored_map
    lang_model_score_map = language_model_score(nativ_scored_map, window_size = 5, model=model)
    combined_score_map = combined_scoring(norm_lang_scored_map, lang_model_score_map)
    return get_native_sentence(combined_score_map)
