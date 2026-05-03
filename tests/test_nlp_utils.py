from app.nlp_utils import clean_text


def test_clean_text_normalizes_whitespace():
    text = '  Ders\nnotu\tburada   '

    assert clean_text(text) == 'Ders notu burada'
