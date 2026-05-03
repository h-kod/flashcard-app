def test_save_card_route_persists_and_cards_page_lists_card(client):
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
    assert b'Bellek nedir?' in cards_response.data
    assert b'Bellek bilgiyi gecici olarak saklar.' in cards_response.data
