import re
from collections import Counter

try:
    import spacy
    nlp = spacy.blank('en')
    if not nlp.pipe_names:
        nlp.add_pipe('sentencizer')
except ImportError:
    nlp = None

STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'were', 'will', 'with', 'this', 'these', 'those',
    'or', 'if', 'but', 'not', 'can', 'may', 'should', 'could', 'would',
    'also', 'so', 'we', 'they', 'their', 'them', 'our', 'you', 'your',
}


def clean_text(text: str) -> str:
    text = text.replace('\r', ' ').replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def split_sentences(text: str) -> list[str]:
    text = clean_text(text)
    if nlp is not None:
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    else:
        parts = re.split(r'(?<=[.!?])\s+', text)
        sentences = [part.strip() for part in parts if part.strip()]
    return sentences


def extract_words(text: str) -> list[str]:
    return [word.lower() for word in re.findall(r"[A-Za-z']+", text) if word.lower() not in STOPWORDS]


def extract_keywords(text: str, top_n: int = 8) -> list[str]:
    words = extract_words(text)
    most_common = Counter(words).most_common(top_n)
    return [word for word, _ in most_common]


def summarize_text(text: str, max_sentences: int = 3) -> str:
    sentences = split_sentences(text)
    if not sentences:
        return ''
    if len(sentences) <= max_sentences:
        return ' '.join(sentences)

    keywords = set(extract_keywords(text, top_n=12))
    scored = []
    for sentence in sentences:
        words = set(extract_words(sentence))
        score = len(words & keywords)
        scored.append((score, sentence))

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = [sentence for _, sentence in scored[:max_sentences]]
    selected.sort(key=lambda s: sentences.index(s))
    return ' '.join(selected)


def generate_flashcards(text: str, max_cards: int = 5) -> list[dict[str, str]]:
    sentences = split_sentences(text)
    keywords = extract_keywords(text, top_n=12)
    cards = []
    for sentence in sentences:
        if len(cards) >= max_cards:
            break
        if any(keyword in sentence.lower() for keyword in keywords[:3]):
            question = 'What is the key idea of this sentence?'
            answer = sentence
            cards.append({'question': question, 'answer': answer, 'source': sentence})

    if not cards and sentences:
        cards.append({'question': 'What is the main idea?', 'answer': sentences[0], 'source': sentences[0]})
    return cards


def generate_qa_pairs(text: str, max_pairs: int = 5) -> list[dict[str, str]]:
    keywords = extract_keywords(text, top_n=5)
    qa = []
    for keyword in keywords:
        question = f"What does '{keyword}' refer to in the text?"
        answer = f"The text highlights '{keyword}' as an important concept or term."
        qa.append({'question': question, 'answer': answer})
        if len(qa) >= max_pairs:
            break
    return qa
