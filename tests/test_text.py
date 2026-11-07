import pytest
from pydantic import ValidationError

from aieng.text import Review, normalize, script_of


def test_normalize_collapses_spaces_and_trims():
    assert normalize("  очень   вкусно \t\n кофе  ") == "очень вкусно кофе"


def test_normalize_unifies_spaces_and_quotes():
    assert normalize("кофейня\u00a0«Зерно»") == 'кофейня "Зерно"'


def test_normalize_composes_decomposed_letters():
    decomposed = "ёлка"  # "е" + combining diaeresis
    assert normalize(decomposed) == "ёлка"


def test_normalize_lower_is_opt_in():
    assert normalize("Вкусно") == "Вкусно"
    assert normalize("Вкусно", lower=True) == "вкусно"


def test_script_of_counts_kyrgyz_as_cyrillic():
    assert script_of("Абдан даамдуу, үй-бүлө менен келебиз") == "cyrillic"


def test_script_of_latin_mixed_and_none():
    assert script_of("Great coffee") == "latin"
    assert script_of("заказ через WhatsApp") == "mixed"
    assert script_of("5/5 !!!") == "none"


def test_review_rejects_rating_out_of_range():
    with pytest.raises(ValidationError) as err:
        Review(text="Отлично", rating=7)
    assert err.value.errors()[0]["loc"] == ("rating",)


def test_review_rejects_blank_text():
    with pytest.raises(ValidationError) as err:
        Review(text="   \u00a0 ")
    assert err.value.errors()[0]["loc"] == ("text",)


def test_review_rating_is_optional_and_text_is_normalized():
    review = Review(text="  Норм  кофе ")
    assert review.text == "Норм кофе"
    assert review.rating is None


def test_normalize_keeps_kyrgyz_letters():
    assert normalize("Салам  достор, ыңгайлуу!") == "Салам достор, ыңгайлуу!"
