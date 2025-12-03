from itertools import product
from math import e as exp

from transliteration.utils import isEnglish, multiply_common_keys, normalize_scores
from transliteration.devanagari.utils import join_plural_n_case_markers
from transliteration import logger

def get_native_candidates(words: list[str]|set[str], reverse_dict: dict[str, str]) -> set[str]:
    candidates = set()
    for word in words:
        candidates.add(word)
        if word in reverse_dict:
            candidates.update(reverse_dict[word])
    return candidates

def native_scoring(candidates: list[str]) -> dict[str, float]:
    """
    :param word: str
    :return: list along with native probabilities
    """
    tot_candidates = len(candidates)
    return {candidate: round(1.0/tot_candidates, 2) for candidate in candidates}

def stride(coleczn: list|dict, counter: int, window_size: int) -> tuple[int, list|dict]:
    """
    Windowing operation by stride. Increments counter and returns a tuple (counter, list) or (counter, dict) based on whethere list or dict was supplied
    :param coleczn: list|dict
    :param counter: int Current count
    :param window_size: int Size of the window
    :return: tuple[int, list|dict]  Returns a tuple (counter, window)
    """
    if not isinstance(coleczn, list) and not isinstance(coleczn, dict):
        raise ValueError("Colection must be list or dict")

    if window_size%2 == 0:
        raise ValueError("Window size must be odd")

    arm_len = int((window_size - 1) / 2)
    l_idx = max(0, counter - arm_len)
    r_idx = min(len(coleczn), counter + arm_len + 1)
    counter += 1

    if isinstance(coleczn, list):
        return counter, coleczn[l_idx: r_idx]

    return counter, dict(list(coleczn.items())[l_idx:r_idx])


def scoring(score_map: list[tuple[str, dict[str, float]]], window_size: int) -> list[tuple[str, dict[str, float]]]:
    """
    :param score_map: list[tuple[str, dict[str, float]]] Sends the whole sentence/phrase to be reversed to native. Each tuple format: Element 1 (str)= reduced, Element 2 (dict) = {native_1: score_1, native_2: score_2...}
    :param window_size: int Window size for language scoring
    :return: dict[str, dict[str, float]] Returns normalized language scored map. Format: key = reduced, value = {native_1: normalized_lang_score_1, native_2: normalized_lang_score_2...}
    """
    norm_lang_scored_map = list()
    counter = 0
    for red_word, cand_score_map in score_map:
        #windowing
        counter, window = stride(score_map, counter, window_size)
        norm_lang_scored_map.append((red_word,language_scoring(window, red_word, cand_score_map)))
    return norm_lang_scored_map

def language_model_score(native_score_map: list[tuple[str, dict[str, float]]], window_size: int, model, sep_case_plural: bool = False) -> list[tuple[str, dict[str, float]]]:
    """
    :param native_score_map: list[tuple[str, dict[str, float]] Element 1 = reduced word, Element 2 = dictionary with candidate native words as keys, scores as values
    :param window_size: int Window to create sentence from
    :param model: kenlm.LanguageModel kenlm model 
    :return: list[tuple[str, dict[str, float]] Element 1 = reduced word, Element 2 = dictionary with candidate native words as keys, best(maximum) lm probability out of all sentences for the native word as values
    """
    lang_model_score_map = list()
    counter = 0
    for red_word, cand_score_map in native_score_map:
        counter, window = stride(native_score_map, counter, window_size)
        lang_model_score_map.append((red_word, language_model_scoring(window, red_word, cand_score_map, model, sep_case_plural)))
    return lang_model_score_map

def language_scoring(window: list[tuple[str, dict[str, float]]], red_word: str, candid_score_map: dict[str, float])-> dict[str, float]:
    nep_score = 0 #Initial total score for Nepali in window
    eng_score = 0 #Initial total score for English in window
    for reduc_word, cand_score_map in window:
        for nativ, score in cand_score_map.items():
            if isEnglish(nativ):
                eng_score += score
            else:
                nep_score += score

    lang_scored_map = dict()
    for nativ, score in candid_score_map.items():
        if isEnglish(nativ):
            score = score * eng_score
        else:
            score = score * nep_score
        lang_scored_map[nativ] = score

    return normalize_scores(lang_scored_map)

def language_model_scoring(window: list[tuple[str, dict[str, float]]], red_word: str, candid_score_map: dict[str, float], model, sep_case_plural:bool = False) -> dict[str, float]:
    lang_model_nativ_score_map = dict() # keys = native candidates for red_word, score = best lm probability
    for native in candid_score_map.keys():
        option_seq = [[native] if k == red_word else v.keys() for k, v in window] #list of list
        red_word_cand_sent_list = product(*option_seq) #all possible list
        lang_model_probs_for_nativ: list[float] = [] # list of all lm probabilities for a native candidate.
        for red_word_cand_sen in red_word_cand_sent_list:
            red_word_cand_sen = " ".join(red_word_cand_sen)
            logger.debug(f"{red_word}: {native} : {red_word_cand_sen}")
            if sep_case_plural:
                red_word_cand_sen = join_plural_n_case_markers(red_word_cand_sen)
            lang_model_probs_for_nativ.append(model.score(red_word_cand_sen))
            # lang_model_probs_for_nativ.append(-4.0)
        lang_model_nativ_score_map[native] = exp**max(lang_model_probs_for_nativ)
    return lang_model_nativ_score_map

def combined_scoring(native_score_map: list[tuple[str, dict[str, float]]], lang_model_score_map: list[tuple[str, dict[str, float]]]) -> list[tuple[str, dict[str, float]]]:
    """
    :param native_score_map: list[tuple[str, dict[str, float]]] Element 1 = reduced word, Element 2 = dictionary with candidate native words as keys, scores as values
    :param lang_model_score_map: list[tuple[str, dict[str, float]]] Element 1 = reduced word, Element 2 = dictionary with candidate native words as keys
    """
    combined_score_map = list()
    for nativ, lang_mod in zip(native_score_map, lang_model_score_map):
        nat_red_word, nativ_score = nativ
        l_m_red_word, l_m_score = lang_mod
        assert nat_red_word == l_m_red_word
        combined_reduc_map = normalize_scores(multiply_common_keys(nativ_score, l_m_score))
        combined_score_map.append((nat_red_word, combined_reduc_map))
    return combined_score_map

