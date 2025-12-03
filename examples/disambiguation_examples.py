from typing import Optional
from symspellpy import Verbosity
from symspellpy.suggest_item import SuggestItem
from transliteration.disambiguation import get_native_candidates, native_scoring, scoring, language_model_score, combined_scoring
from transliteration.devanagari.utils import sep_plural_n_case_markers, join_plural_n_case_markers, word_is_split

def correct_spelling(word:str, sym_spell = None, edit_dist: Optional[int] = None)-> set[str]:
    spell_corrs = [word]
    if sym_spell:
        sugg_item_list: list[SuggestItem] = sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=edit_dist, include_unknown=True)
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

def get_native_sentence(score_map: list[tuple[str, dict[str, float]]], sep_case_plural:bool = False) -> str:
    native_sentence = []
    for red_word, cand_score_map in score_map:
        native_sentence.append(max(cand_score_map, key=cand_score_map.get))
    sen = " ".join(native_sentence)
    if sep_case_plural:
        sen = join_plural_n_case_markers(sen)
    return sen


def disambiguate(sentence: str,
    model, 
    reverse_dict, 
    sym_spell = None, 
    edit_dist: Optional[int] = None, 
    lang_scoring:bool = True, 
    sep_case_plural:bool = False) -> str:
    if sep_case_plural:
        sentence = split_plural_n_case_markers(sen = sentence, reverse_dict=reverse_dict, sep_deva = True)
    words = get_words_from_sentence(sentence)
    nativ_scored_map: list[tuple[str, dict[str, float]]] = list() #values will also have native scoring. Therefore we opt for list (of tuples) data type for values
    for word in words:
        spell_corrs = correct_spelling(word, sym_spell)
        candidates = get_native_candidates(spell_corrs, reverse_dict)
        scored_candidates = native_scoring(candidates)
        nativ_scored_map.append((word, scored_candidates))

    norm_lang_scored_map: list[tuple[str, dict[str, float]]] = list()
    if lang_scoring:
        norm_lang_scored_map = scoring(nativ_scored_map, window_size = 5)
    else:
        norm_lang_scored_map = nativ_scored_map
    lang_model_score_map = language_model_score(nativ_scored_map, window_size = 5, model=model, sep_case_plural=sep_case_plural)
    combined_score_map = combined_scoring(norm_lang_scored_map, lang_model_score_map)
    return get_native_sentence(combined_score_map, sep_case_plural)
