import json

from app import gemini_client


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload
        self.status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


def test_generate_flashcards_with_gemini_parses_mocked_response(monkeypatch):
    expected_cards = [
        {
            'question': 'Kavram nedir?',
            'answer': 'Kavram bir fikri temsil eder.',
            'source': 'Kavram bir fikri temsil eder.',
        },
        {
            'question': 'Sistem neden onemli?',
            'answer': 'Sistem duzenli calismayi saglar.',
            'source': 'Sistem duzenli calismayi saglar.',
        },
    ]
    payload = {
        'candidates': [
            {
                'content': {
                    'parts': [
                        {
                            'text': json.dumps({'flashcards': expected_cards}),
                        }
                    ]
                }
            }
        ]
    }
    calls = []

    def fake_post(url, params=None, json=None, timeout=None):
        calls.append({'url': url, 'params': params, 'json': json, 'timeout': timeout})
        return FakeResponse(payload)

    monkeypatch.setattr(gemini_client.requests, 'post', fake_post)

    cards = gemini_client.generate_flashcards_with_gemini(
        text='Kavram bir fikri temsil eder. Sistem duzenli calismayi saglar.',
        max_cards=2,
        api_key='test-api-key',
        model='models/test-model',
        api_roots=['https://example.invalid'],
    )

    assert cards == expected_cards
    assert len(calls) == 1
    assert calls[0]['url'] == 'https://example.invalid/models/test-model:generateContent'
    assert calls[0]['params'] == {'key': 'test-api-key'}
    assert calls[0]['timeout'] == 30
