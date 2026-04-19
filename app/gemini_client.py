import json
import re
from typing import Dict, List, Optional

import requests


API_ROOTS = [
    'https://generativelanguage.googleapis.com/v1',
    'https://gemini.googleapis.com/v1',
]
DEFAULT_MODEL = 'models/gemma-3-1b-it'
DEFAULT_MODEL_CANDIDATES = [
    'gemma-3-1b-it',
    'gemma-3-4b-it',
    'gemma-3-12b-it',
    'gemma-3-27b-it',
    'gemini-2.5-flash-lite',
    'gemini-2.5-flash',
]
MAX_QUESTION_CHARS = 90
MAX_ANSWER_CHARS = 220
MAX_SOURCE_CHARS = 160


class GeminiQuotaExceededError(RuntimeError):
    pass


class GeminiGenerationError(RuntimeError):
    pass


def normalize_model_name(model_name: str) -> str:
    model_name = model_name.strip()
    if not model_name:
        return model_name
    if model_name.startswith('models/'):
        return model_name
    if '/' in model_name:
        return model_name
    return f'models/{model_name}'


def clean_text(text: str) -> str:
    return ' '.join(text.replace('\r', ' ').replace('\n', ' ').split())


def build_flashcard_prompt(text: str, max_cards: int) -> str:
    return (
        'Asagidaki Turkce ders notundan ogretici ve anlamli calisma kartlari uret. '
        f'Tam olarak {max_cards} adet flashcard olustur. '
        'Her kartta "question", "answer" ve "source" alanlari olsun. '
        'Tum soru ve cevaplari yalnizca verilen metne dayanarak yaz. Uydurma bilgi ekleme. '
        'Anlamsiz, asiri genel, bos veya tekrar eden kartlar uretme. '
        'Kartlar birlikte konunun temel kavramlarini, tanimlarini, farklarini ve kritik noktalarini ogretsin. '
        f'Soru en fazla {MAX_QUESTION_CHARS} karakter olsun. '
        f'Cevap en fazla {MAX_ANSWER_CHARS} karakter olsun. '
        f'Source en fazla {MAX_SOURCE_CHARS} karakter olsun. '
        'Yazi kart ekranina sigacak kadar kisa ve net olsun. '
        'Her cevap tek paragraf olsun. '
        'Ciktida yalnizca gecerli JSON ver, aciklama veya markdown ekleme.\n'
        '{"flashcards":[{"question":"...","answer":"...","source":"..."}]}\n---\n'
        f'{text}'
    )


def build_repair_prompt(text: str, max_cards: int, previous_output: str) -> str:
    return (
        'Onceki flashcard cikti kurallara tam uymadi. Yeni bir cikti olustur. '
        f'Tam olarak {max_cards} adet flashcard ver. '
        'Yalnizca verilen metne dayan. Uydurma veya anlamsiz kart uretme. '
        'Tekrarlanan kartlardan kacin. '
        f'Her question en fazla {MAX_QUESTION_CHARS} karakter, '
        f'her answer en fazla {MAX_ANSWER_CHARS} karakter, '
        f'her source en fazla {MAX_SOURCE_CHARS} karakter olsun. '
        'Cevaplar ogretici ama kisa olsun ve karta sigsin. '
        'Yalnizca gecerli JSON dondur.\n'
        'Metin:\n'
        f'{text}\n'
        'Gecersiz veya yetersiz onceki cikti:\n'
        f'{previous_output}'
    )


def parse_flashcards_response(content: str) -> List[Dict[str, str]]:
    if not content:
        return []

    content = content.strip()
    match = re.search(r'({\s*"flashcards"\s*:\s*\[.*\]})', content, re.S)
    if not match:
        match = re.search(r'({.*})', content, re.S)
    if not match:
        return []

    payload = match.group(1)
    payload = payload.replace('\n', ' ').strip()
    payload = re.sub(r',\s*}', '}', payload)
    payload = re.sub(r',\s*\]', ']', payload)

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return []

    flashcards = data.get('flashcards', [])
    if not isinstance(flashcards, list):
        return []

    results: List[Dict[str, str]] = []
    for item in flashcards:
        if not isinstance(item, dict):
            continue
        question = clean_text(str(item.get('question', '')))
        answer = clean_text(str(item.get('answer', '')))
        source = clean_text(str(item.get('source', '')))
        if question and answer:
            results.append({'question': question, 'answer': answer, 'source': source})
    return results


def is_card_meaningful(card: Dict[str, str]) -> bool:
    question = card.get('question', '')
    answer = card.get('answer', '')
    source = card.get('source', '')

    if len(question) > MAX_QUESTION_CHARS or len(answer) > MAX_ANSWER_CHARS or len(source) > MAX_SOURCE_CHARS:
        return False
    if len(question) < 8 or len(answer) < 12:
        return False

    normalized_question = question.lower()
    normalized_answer = answer.lower()
    banned_fragments = [
        'ana fikir nedir',
        'hangi bilgi one cikiyor',
        'bu bolumun ana fikri',
        'metindeki bu bilgi',
        'notun ana fikri',
    ]
    if any(fragment in normalized_question for fragment in banned_fragments):
        return False
    if normalized_question == normalized_answer:
        return False
    return True


def filter_flashcards(cards: List[Dict[str, str]], max_cards: int) -> List[Dict[str, str]]:
    filtered: List[Dict[str, str]] = []
    seen = set()

    for card in cards:
        if len(filtered) >= max_cards:
            break
        if not is_card_meaningful(card):
            continue
        signature = (card['question'].lower(), card['answer'].lower())
        if signature in seen:
            continue
        seen.add(signature)
        filtered.append(card)

    return filtered


def generate_flashcards_with_gemini(
    text: str,
    max_cards: int,
    api_key: str,
    model: Optional[str] = None,
    api_roots: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    def request_model(prompt: str, model_name: str, api_root: str):
        payload = {
            'contents': [
                {
                    'parts': [
                        {'text': prompt},
                    ],
                },
            ],
            'generation_config': {
                'temperature': 0.2,
                'top_p': 1,
                'top_k': 40,
                'max_output_tokens': 1600,
            },
        }
        model_path = normalize_model_name(model_name)
        url = f'{api_root.rstrip("/")}/{model_path}:generateContent'
        response = requests.post(url, params={'key': api_key}, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def format_http_error(exc: requests.HTTPError) -> str:
        response = exc.response
        if response is None:
            return str(exc)

        try:
            response_payload = response.json()
        except ValueError:
            response_payload = {}

        error = response_payload.get('error', {}) if isinstance(response_payload, dict) else {}
        message = error.get('message') or response.text or str(exc)
        return f'HTTP {response.status_code}: {message}'

    def extract_content(response_data: dict) -> str:
        candidate = {}
        if isinstance(response_data, dict):
            candidates = response_data.get('candidates') or []
            if candidates:
                candidate = candidates[0]
            else:
                candidate = response_data.get('response', {})

        if isinstance(candidate, dict):
            parts = []
            if isinstance(candidate.get('content'), dict):
                for part in candidate['content'].get('parts', []):
                    if isinstance(part, dict) and 'text' in part:
                        parts.append(str(part['text']))
            if parts:
                return ' '.join(parts).strip()
            return str(candidate.get('content') or candidate.get('output_text') or '').strip()
        if isinstance(candidate, str):
            return candidate.strip()
        return ''

    desired_model = model or DEFAULT_MODEL
    models_to_try = [desired_model] + [m for m in DEFAULT_MODEL_CANDIDATES if m != desired_model]
    api_roots = list(api_roots or API_ROOTS)
    prompts = [build_flashcard_prompt(text, max_cards)]
    last_error = None
    last_raw_content = ''
    attempted_models = []
    received_any_response = False
    saw_quota_error = False

    for attempt_index in range(2):
        prompt = prompts[attempt_index]
        for api_root in api_roots:
            for model_name in models_to_try:
                attempted_models.append(f'{api_root.rstrip("/")}/{normalize_model_name(model_name)}')
                try:
                    response_data = request_model(prompt, model_name, api_root)
                    received_any_response = True
                    raw_content = extract_content(response_data)
                    last_raw_content = raw_content
                    cards = filter_flashcards(parse_flashcards_response(raw_content), max_cards)
                    if len(cards) == max_cards:
                        return cards
                except requests.HTTPError as exc:
                    if exc.response is not None and exc.response.status_code == 429:
                        saw_quota_error = True
                    if exc.response is not None and exc.response.status_code == 404:
                        continue
                    last_error = RuntimeError(format_http_error(exc))
                    continue
                except requests.RequestException as exc:
                    last_error = exc
                    continue

        if attempt_index == 0 and received_any_response:
            prompts.append(build_repair_prompt(text, max_cards, last_raw_content))
        else:
            break

    attempted_summary = ', '.join(dict.fromkeys(attempted_models))
    if saw_quota_error:
        raise GeminiQuotaExceededError(
            'Gemini kart uretimi basarisiz oldu. '
            f'Denenen modeller: {attempted_summary}. '
            f'Son hata: {last_error}'
        )
    if last_error is not None:
        raise GeminiGenerationError(
            'Gemini kart uretimi basarisiz oldu. '
            f'Denenen modeller: {attempted_summary}. '
            f'Son hata: {last_error}'
        )

    raise GeminiGenerationError(
        'Gemini gecerli ve yeterli sayida flashcard uretemedi. '
        'Lutfen daha acik veya daha zengin bir not ile tekrar deneyin.'
    )
