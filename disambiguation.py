from transliteration.utils import isEnglish

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

def normalize_scores(score_map: dict[str, float]) -> dict[str, float]:
    sum_score = sum(score_map.values())
    for item, score in score_map.items():
        score_map[item] = round(score/sum_score, 2)
    return score_map
