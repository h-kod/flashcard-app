import re
from collections import Counter
from typing import Dict, List

try:
    import spacy

    nlp = spacy.blank('tr')
    if not nlp.pipe_names:
        nlp.add_pipe('sentencizer')
except ImportError:
    nlp = None


STOPWORDS = {
    'bir', 've', 'veya', 'da', 'de', 'ile', 'ben', 'sen', 'o', 'bu', 'su',
    'ama', 'fakat', 'cunku', 'ise', 'ki', 'bile', 'cok', 'az', 'en', 'icin',
    'gibi', 'var', 'yok', 'olarak', 'tarafindan', 'degil', 'olan', 'olanlar',
    'olani', 'bazi', 'her', 'herkes', 'sey', 'sanki', 'daima', 'herhangi',
    'ayni', 'yeni', 'son', 'once', 'sonra', 'daha', 'ne', 'nasil', 'nerede',
    'zaman', 'kadar', 'sadece',
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'were', 'will', 'with', 'this', 'these', 'those',
    'or', 'if', 'but', 'not', 'can', 'may', 'should', 'could', 'would',
    'also', 'so', 'we', 'they', 'their', 'them', 'our', 'you', 'your',
}

QUESTION_TEMPLATES = [
    "'{keyword}' kavrami bu cumlede ne anlama geliyor?",
    "Metinde '{keyword}' nasil tanimlaniyor?",
    "Neden '{keyword}' bu notta onemli?",
]

FALLBACK_QUESTION_TEMPLATES = [
    "Bu bolumun ana fikri nedir?",
    "Metindeki bu bilgi neyi acikliyor?",
    "Bu cumleden hangi onemli nokta cikarilabilir?",
]


def clean_text(text: str) -> str:
    text = text.replace('\r', ' ').replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def split_sentences(text: str) -> List[str]:
    text = clean_text(text)
    if not text:
        return []

    if nlp is not None:
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    else:
        parts = re.split(r'(?<=[.!?])\s+', text)
        sentences = [part.strip() for part in parts if part.strip()]
    return sentences


def normalize_word(word: str) -> str:
    return word.lower().strip("'\".,:;()[]{}")


def extract_words(text: str) -> List[str]:
    words = re.findall(r"[A-Za-z0-9']+", text, flags=re.UNICODE)
    results = []
    for word in words:
        normalized = normalize_word(word)
        if normalized and normalized not in STOPWORDS and len(normalized) > 2:
            results.append(normalized)
    return results


def word_frequencies(text: str) -> Counter:
    return Counter(extract_words(text))


def extract_keywords(text: str, top_n: int = 8) -> List[str]:
    freq = word_frequencies(text)
    return [word for word, count in freq.most_common(top_n) if count > 0]


def summarize_text(text: str, max_sentences: int = 3) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return ''
    if len(sentences) <= max_sentences:
        return ' '.join(sentences)

    freq = word_frequencies(text)
    scored: List[tuple[int, str]] = []
    for sentence in sentences:
        words = extract_words(sentence)
        score = sum(freq[word] for word in set(words))
        scored.append((score, sentence))

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = [sentence for _, sentence in scored[:max_sentences]]
    selected.sort(key=lambda sentence: sentences.index(sentence))
    return ' '.join(selected)


def build_question(keyword: str) -> str:
    template_index = sum(ord(character) for character in keyword) % len(QUESTION_TEMPLATES)
    template = QUESTION_TEMPLATES[template_index]
    return template.format(keyword=keyword)


def build_fallback_question(index: int) -> str:
    return FALLBACK_QUESTION_TEMPLATES[index % len(FALLBACK_QUESTION_TEMPLATES)]


def generate_flashcards(text: str, max_cards: int = 5) -> List[Dict[str, str]]:
    sentences = split_sentences(text)
    keywords = extract_keywords(text, top_n=max(max_cards * 2, 10))
    cards: List[Dict[str, str]] = []
    seen_cards = set()
    used_sentences = set()

    def add_card(question: str, answer: str, source: str) -> bool:
        question = clean_text(question)
        answer = clean_text(answer)
        source = clean_text(source)
        signature = (question.lower(), answer.lower())
        if not question or not answer or signature in seen_cards:
            return False
        cards.append({'question': question, 'answer': answer, 'source': source})
        seen_cards.add(signature)
        return True

    for keyword in keywords:
        if len(cards) >= max_cards:
            break
        for sentence in sentences:
            if sentence in used_sentences:
                continue
            if keyword in sentence.lower():
                if add_card(build_question(keyword), sentence, sentence):
                    used_sentences.add(sentence)
                break

    for index, sentence in enumerate(sentences):
        if len(cards) >= max_cards:
            break
        if sentence in used_sentences:
            continue
        if add_card(build_fallback_question(index), sentence, sentence):
            used_sentences.add(sentence)

    summary = summarize_text(text, max_sentences=min(3, max(1, max_cards)))
    summary_source = summary or (sentences[0] if sentences else '')
    while len(cards) < max_cards and summary_source:
        keyword = keywords[len(cards) % len(keywords)] if keywords else f'konu {len(cards) + 1}'
        question = f"'{keyword}' ile ilgili hatirlanmasi gereken temel nokta nedir?"
        if not add_card(question, summary, summary_source):
            add_card(f"{len(cards) + 1}. kartta hangi bilgi one cikiyor?", summary, summary_source)
            break

    if not cards and summary_source:
        add_card('Notun ana fikri nedir?', summary_source, summary_source)

    return cards[:max_cards]


def generate_qa_pairs(text: str, max_pairs: int = 5) -> List[Dict[str, str]]:
    sentences = split_sentences(text)
    keywords = extract_keywords(text, top_n=max_pairs)
    qa: List[Dict[str, str]] = []

    for keyword in keywords:
        answer_sentence = next((sentence for sentence in sentences if keyword in sentence.lower()), '')
        question = f"Metinde '{keyword}' neyi ifade ediyor?"
        answer = answer_sentence if answer_sentence else f"'{keyword}' metnin onemli kavramlarindan biridir."
        qa.append({'question': question, 'answer': answer})
        if len(qa) >= max_pairs:
            break
    return qa
