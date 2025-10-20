from itertools import product
from math import e as exp

from transliteration.utils import isEnglish, multiply_common_keys, normalize_scores

def native_scoring(word: str, reverse_dict: dict[str, list[str]]) -> dict[str, float]:
    """
    :param word: str
    :return: list along with native probabilities
    """
    if word in reverse_dict:
        native_candidates = reverse_dict[word]
        tot_candidates = len(native_candidates)
        return {candidate: round(1.0/tot_candidates, 2) for candidate in native_candidates}

    return {word: 1.0}

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


def scoring(rev_reduc_map: dict[str, dict[str, float]], window_size: int) -> dict[str, dict[str, float]]:
    """
    :param reduction_map: dict[str, dict[str, float]] Sends the whole sentence/phrase to be reversed to native. Format: key = reduced, value = {native_1: score_1, native_2: score_2...}
    :param window_size: int Window size for language scoring
    :return: dict[str, dict[str, float]] Returns normalized language scored map. Format: key = reduced, value = {native_1: normalized_lang_score_1, native_2: normalized_lang_score_2...}
    """
    norm_lang_scored_map = dict()
    counter = 0
    for red_word in rev_reduc_map:
        #windowing
        counter, window = stride(rev_reduc_map, counter, window_size)
        norm_lang_scored_map[red_word] = language_scoring(window, red_word)
    return norm_lang_scored_map

def language_model_score(native_score_map: dict[str, dict[str, float]], window_size: int, model) -> dict[str, dict[str, float]]:
    """
    :param native_score_map: dict key = reduced word, value = dictionary with candidate native words as keys, scores as values
    :param window_size: int Window to create sentence from
    :param model: kenlm.LanguageModel kenlm model 
    :return: dict key = reduced word, value = dictionary with candidate native words as keys, best(maximum) lm probability out of all sentences for the native word as values
    """
    lang_model_score_map = dict()
    counter = 0
    for red_word in native_score_map:
        counter, window = stride(native_score_map, counter, window_size)
        lang_model_score_map[red_word] = language_model_scoring(window, red_word, model)
    return lang_model_score_map

def language_scoring(window: dict[str, dict[str, float]], red_word: str)-> dict[str, float]:
    nep_score = 0
    eng_score = 0
    for reduc_word in window:
        for nativ, score in window[reduc_word].items():
            if isEnglish(nativ):
                eng_score += score
            else:
                nep_score += score

    lang_scored_map = dict()
    for nativ, score in window[red_word].items():
        if isEnglish(nativ):
            score = score * eng_score
        else:
            score = score * nep_score
        lang_scored_map[nativ] = score

    return normalize_scores(lang_scored_map)

def language_model_scoring(window: dict[str, dict[str, float]], red_word: str, model) -> dict[str, float]:
    lang_model_nativ_score_map = dict() # keys = native candidates for red_word, score = best lm probability
    for native in window[red_word].keys():
        option_seq = [[native] if k == red_word else v.keys() for k, v in window.items()] #list of list
        red_word_cand_sent_list = product(*option_seq) #all possible list
        lang_model_probs_for_nativ: list[float] = [] # list of all lm probabilities for a native candidate.
        for red_word_cand_list in red_word_cand_sent_list:
            red_word_cand = " ".join(red_word_cand_list)
            print(f"{red_word}: {native} : {red_word_cand}")
            lang_model_probs_for_nativ.append(model.score(red_word_cand))
            # lang_model_probs_for_nativ.append(-4.0)
        lang_model_nativ_score_map[native] = exp**max(lang_model_probs_for_nativ)
    return lang_model_nativ_score_map

def combined_scoring(native_score_map: dict[str, dict[str, float]], lang_model_score_map: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """
    :param native_score_map: dict key = reduced word, value = dictionary with candidate native words as keys, scores as values
    :param lang_model_score_map: dict key = reduced word, value = dictionary with candidate native words as keys
    """
    combined_score_map = dict()
    for red_word in native_score_map:
        combined_reduc_map = normalize_scores(multiply_common_keys(native_score_map[red_word], lang_model_score_map[red_word]))
        combined_score_map[red_word] = combined_reduc_map
    return combined_score_map

