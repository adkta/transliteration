from transliteration.disambiguation import native_scoring, scoring, language_model_score, combined_scoring

def correct_spelling(word:str)-> str:
    return word

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
        spelling_corrected_word = correct_spelling(word)
        native_candidates = native_scoring(spelling_corrected_word, reverse_dict)
        nativ_scored_map[spelling_corrected_word] = native_candidates

    norm_lang_scored_map = scoring(nativ_scored_map, window_size = 5)
    lang_model_score_map = language_model_score(nativ_scored_map, window_size = 5, model=model)
    combined_score_map = combined_scoring(norm_lang_scored_map, lang_model_score_map)
    return get_native_sentence(combined_score_map)
