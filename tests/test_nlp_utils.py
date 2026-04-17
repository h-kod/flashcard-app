from app.nlp_utils import clean_text, split_sentences, extract_keywords, summarize_text, generate_flashcards, generate_qa_pairs


def test_clean_text_removes_extra_whitespace():
    text = 'This  is\na   test.'
    assert clean_text(text) == 'This is a test.'


def test_split_sentences_returns_sentences():
    text = 'This is one sentence. This is two.'
    sentences = split_sentences(text)
    assert len(sentences) == 2
    assert sentences[0].startswith('This is one')


def test_extract_keywords_returns_non_empty_list():
    text = 'Natural language processing is an important field in AI.'
    keywords = extract_keywords(text, top_n=3)
    assert len(keywords) == 3
    assert 'language' in keywords or 'natural' in keywords


def test_extract_keywords_ignores_stopwords():
    text = 'This is the best test of the system.'
    keywords = extract_keywords(text, top_n=3)
    assert 'this' not in keywords
    assert 'the' not in keywords


def test_summarize_text_returns_short_summary():
    text = 'Machine learning is useful. Natural language processing is part of AI.'
    summary = summarize_text(text, max_sentences=1)
    assert summary != ''


def test_generate_flashcards_creates_cards():
    text = 'Python is a programming language. It is often used in data science.'
    cards = generate_flashcards(text, max_cards=2)
    assert len(cards) >= 1
    assert any('python' in card['answer'].lower() for card in cards)


def test_generate_flashcards_uses_keywords_in_questions():
    text = 'Python is a programming language. It is often used in data science.'
    cards = generate_flashcards(text, max_cards=2)
    assert any('python' in card['question'].lower() or 'data' in card['question'].lower() for card in cards)


def test_generate_flashcards_turkish_text():
    text = 'Python programlama dili olarak bilinir. Veri bilimi eğitiminde sıkça kullanılır.'
    cards = generate_flashcards(text, max_cards=2)
    assert len(cards) >= 1
    assert any('kavramı' in card['question'].lower() or 'önemli' in card['question'].lower() for card in cards)


def test_generate_qa_pairs_creates_questions():
    text = 'Deep learning and neural networks are central concepts in AI.'
    qas = generate_qa_pairs(text, max_pairs=2)
    assert len(qas) == 2
    assert all('metinde' in qa['question'].lower() or 'what does' in qa['question'].lower() for qa in qas)


def test_generate_qa_pairs_turkish_text():
    text = 'Derin öğrenme yapay zekanın önemli bir alanıdır.'
    qas = generate_qa_pairs(text, max_pairs=1)
    assert len(qas) == 1
    assert 'metinde' in qas[0]['question'].lower()
