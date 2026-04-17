from .db import get_db


def save_card(app, question: str, answer: str, source: str = '') -> int:
    db = get_db(app)
    cursor = db.execute(
        'INSERT INTO cards (question, answer, source) VALUES (?, ?, ?)',
        (question, answer, source),
    )
    db.commit()
    return cursor.lastrowid


def list_cards(app) -> list[dict]:
    db = get_db(app)
    rows = db.execute('SELECT * FROM cards ORDER BY created_at DESC').fetchall()
    return [dict(row) for row in rows]


def get_card(app, card_id: int) -> dict | None:
    db = get_db(app)
    row = db.execute('SELECT * FROM cards WHERE id = ?', (card_id,)).fetchone()
    return dict(row) if row else None


def update_card(app, card_id: int, question: str, answer: str, source: str = '') -> None:
    db = get_db(app)
    db.execute(
        'UPDATE cards SET question = ?, answer = ?, source = ? WHERE id = ?',
        (question, answer, source, card_id),
    )
    db.commit()


def delete_card(app, card_id: int) -> None:
    db = get_db(app)
    db.execute('DELETE FROM cards WHERE id = ?', (card_id,))
    db.commit()
