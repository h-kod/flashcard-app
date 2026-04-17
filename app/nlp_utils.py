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
    'bir', 've', 'veya', 'da', 'de', 'ile', 'ben', 'sen', 'o', 'bu', 'şu',
    'ama', 'fakat', 'çünkü', 'ise', 'ki', 'bile', 'çok', 'az', 'en', 'için',
    'gibi', 'var', 'yok', 'olarak', 'tarafından', 'değil', 'olan', 'olanlar',
    'olanı', 'olanlar', 'bazı', 'her', 'herkes', 'şey', 'şu', 'sanki', 'ama',
    'daima', 'herhangi', 'aynı', 'yeni', 'son', 'önce', 'sonra', 'daha', 'ise',
    'ne', 'nasıl', 'nerede', 'zaman', 'kadar', 'sadece',
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'were', 'will', 'with', 'this', 'these', 'those',
    'or', 'if', 'but', 'not', 'can', 'may', 'should', 'could', 'would',
    'also', 'so', 'we', 'they', 'their', 'them', 'our', 'you', 'your',
}

QUESTION_TEMPLATES = [
    "'{keyword}' kavramı bu cümlede ne anlama geliyor?",
    "Metinde '{keyword}' nasıl tanımlanıyor?",
    "Neden '{keyword}' bu notta önemli?",
]


def clean_text(text: str) -> str:
    text = text.replace('\r', ' ').replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def split_sentences(text: str) -> List[str]:
    text = clean_text(text)
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
    return [normalize_word(word) for word in re.findall(r"[A-Za-zığüşöçİĞÜŞÖÇ']+", text, flags=re.UNICODE)
            if normalize_word(word) not in STOPWORDS and len(normalize_word(word)) > 2]


def word_frequencies(text: str) -> Counter:
    return Counter(extract_words(text))


def extract_keywords(text: str, top_n: int = 8) -> List[str]:
    freq = word_frequencies(text)
    most_common = [word for word, count in freq.most_common(top_n) if count > 0]
    return most_common


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
    selected.sort(key=lambda s: sentences.index(s))
    return ' '.join(selected)


def build_question(keyword: str) -> str:
    template = QUESTION_TEMPLATES[hash(keyword) % len(QUESTION_TEMPLATES)]
    return template.format(keyword=keyword)


def generate_flashcards(text: str, max_cards: int = 5) -> List[Dict[str, str]]:
    sentences = split_sentences(text)
    keywords = extract_keywords(text, top_n=10)
    cards: List[Dict[str, str]] = []
    used_sentences = set()

    for keyword in keywords:
        if len(cards) >= max_cards:
            break
        for sentence in sentences:
            if sentence in used_sentences:
                continue
            if keyword in sentence.lower():
                question = build_question(keyword)
                answer = sentence
                cards.append({'question': question, 'answer': answer, 'source': sentence})
                used_sentences.add(sentence)
                break

    if not cards and sentences:
        cards.append({
            'question': 'Notun ana fikri nedir?',
            'answer': sentences[0],
            'source': sentences[0],
        })
    return cards[:max_cards]


def generate_qa_pairs(text: str, max_pairs: int = 5) -> List[Dict[str, str]]:
    sentences = split_sentences(text)
    keywords = extract_keywords(text, top_n=max_pairs)
    qa: List[Dict[str, str]] = []

    for keyword in keywords:
        answer_sentence = next((sentence for sentence in sentences if keyword in sentence.lower()), '')
        question = f"Metinde '{keyword}' neyi ifade ediyor?"
        answer = answer_sentence if answer_sentence else f"'{keyword}' metnin önemli kavramlarından biridir."
        qa.append({'question': question, 'answer': answer})
        if len(qa) >= max_pairs:
            break
    return qa
