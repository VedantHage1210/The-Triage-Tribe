from app.services.guardrail import contains_red_flag_terms


def test_red_flag_matching_ignores_punctuation_and_case():
    assert contains_red_flag_terms("I have CHEST-PAIN!", ["chest pain"])


def test_red_flag_matching_does_not_match_partial_words():
    assert not contains_red_flag_terms("The chest painless episode ended.", ["chest pain"])


def test_german_red_flag_phrase_is_detected():
    assert contains_red_flag_terms("Ich habe starke Blutung.", ["starke blutung"])