from app import routes


def test_save_card_route_redirects_and_cards_page_renders(client):
    response = client.post(
        '/save-card',
        data={
            'question': 'Bellek nedir?',
            'answer': 'Bellek bilgiyi gecici olarak saklar.',
            'source': 'Bellek bilgiyi gecici olarak saklar.',
        },
    )

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/deck')

    cards_response = client.get('/cards')
    assert cards_response.status_code == 200
    assert b'saved-cards-grid' in cards_response.data


def test_index_uses_user_supplied_gemini_api_key(client, monkeypatch):
    captured = {}

    def fake_generate(text, max_cards, api_key, model, api_roots):
        captured['text'] = text
        captured['max_cards'] = max_cards
        captured['api_key'] = api_key
        return [{'question': 'Soru?', 'answer': 'Cevap burada.', 'source': 'Kaynak'}]

    monkeypatch.setattr(routes, 'generate_flashcards_with_gemini', fake_generate)

    response = client.post(
        '/',
        data={
            'note_text': 'kelime ' * 60,
            'card_count': '5',
            'gemini_api_key': 'AIza-user-key',
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/deck')
    assert captured['api_key'] == 'AIza-user-key'
