from transliteration.disambiguation import get_native_candidates, native_scoring, scoring, language_model_score, combined_scoring

def correct_spelling(word:str)-> set[str]:
    return [word]

def get_words_from_sentence(sentence: str)-> list:
    return sentence.split(" ")

def get_native_sentence(score_map: dict[str, dict[str, float]]) -> str:
    native_sentence = []
    for red_word in score_map:
        native_sentence.append(max(score_map[red_word], key=score_map[red_word].get))
    return " ".join(native_sentence)

def disambiguate(sentence: str, model, reverse_dict) -> str:
    words = get_words_from_sentence(sentence)
    nativ_scored_map: dict[str, dict[str, float]] = dict() #values will also have native scoring. Therefore we opt for dict data type for values
    for word in words:
        spell_corrs = correct_spelling(word)
        candidates = get_native_candidates(spell_corrs, reverse_dict)
        scored_candidates = native_scoring(candidates)
        nativ_scored_map[word] = scored_candidates

    norm_lang_scored_map = scoring(nativ_scored_map, window_size = 5)
    lang_model_score_map = language_model_score(nativ_scored_map, window_size = 5, model=model)
    combined_score_map = combined_scoring(norm_lang_scored_map, lang_model_score_map)
    return get_native_sentence(combined_score_map)
