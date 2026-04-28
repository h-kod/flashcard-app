import csv
import io
import json
from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, session, url_for

from .gemini_client import (
    GeminiGenerationError,
    GeminiQuotaExceededError,
    clean_text,
    generate_flashcards_with_gemini,
)
from .models import delete_card, get_card, list_cards, save_card, update_card

bp = Blueprint('main', __name__)


def build_topic_title(text: str) -> str:
    cleaned = clean_text(text)
    if not cleaned:
        return 'Flashcard Seti'

    words = cleaned.split()
    title_words = words[:7]
    title = ' '.join(title_words).strip()
    if len(words) > 7:
        title = f'{title}...'
    return title or 'Flashcard Seti'


def word_count(text: str) -> int:
    cleaned = clean_text(text)
    if not cleaned:
        return 0
    return len(cleaned.split())


@bp.route('/', methods=['GET', 'POST'])
def index():
    context = {
        'input_text': session.get('input_text', ''),
        'selected_count': session.get('selected_count', 5),
    }

    if request.method == 'POST':
        if request.form.get('action') == 'clear':
            session.clear()
            return redirect(url_for('main.index'))

        raw_text = request.form.get('note_text', '')
        card_count = int(request.form.get('card_count', 5) or 5)
        upload = request.files.get('note_file')
        if upload and upload.filename:
            raw_text = upload.read().decode('utf-8', errors='ignore')

        context.update({'input_text': raw_text, 'selected_count': card_count})

        text = clean_text(raw_text)
        if not text:
            flash('Lütfen metin girin veya bir dosya yükleyin.', 'warning')
            return render_template('index.html', **context)

        if word_count(text) < 50:
            flash('Kart oluşturmak için en az 50 kelimelik not girin.', 'warning')
            return render_template('index.html', **context)

        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            flash(
                'Gemini API anahtarınız bulunamadı. Lütfen gemini_key.txt dosyasını oluşturun veya GEMINI_API_KEY ortam değişkenini ayarlayın.',
                'danger',
            )
            return render_template('index.html', **context)

        try:
            flashcards = generate_flashcards_with_gemini(
                text,
                card_count,
                api_key,
                current_app.config.get('GEMINI_MODEL'),
                current_app.config.get('GEMINI_API_ROOTS'),
            )
        except GeminiQuotaExceededError:
            flash(
                'Gemini kota limitiniz dolu görünüyor. Lütfen biraz sonra tekrar deneyin veya plan ayarlarınızı kontrol edin.',
                'danger',
            )
            return render_template('index.html', **context)
        except GeminiGenerationError as exc:
            flash(f'Kart uretimi sirasinda Gemini yaniti islenemedi: {exc}', 'danger')
            return render_template('index.html', **context)
        except Exception as exc:
            flash(f'Kart uretimi sirasinda beklenmeyen bir hata olustu: {exc}', 'danger')
            return render_template('index.html', **context)

        session['input_text'] = text
        session['selected_count'] = card_count
        session['flashcards'] = flashcards
        session['deck_topic_title'] = build_topic_title(text)
        session['deck_generated_at'] = datetime.now().isoformat(timespec='milliseconds')
        session.modified = True
        return redirect(url_for('main.deck'))

    return render_template('index.html', **context)


@bp.route('/new-note')
def new_note():
    session.clear()
    return redirect(url_for('main.index'))


@bp.route('/deck')
def deck():
    flashcards = session.get('flashcards', [])
    requested_history = request.args.get('history', '').strip()
    if not flashcards and not requested_history:
        flash('Henüz kart yok. Lütfen bir not girin.', 'warning')
        return redirect(url_for('main.index'))

    generated_at = session.get('deck_generated_at', '')
    if requested_history:
        generated_at = requested_history

    return render_template(
        'deck.html',
        flashcards=flashcards,
        topic_title=session.get('deck_topic_title', 'Flashcard Seti'),
        generated_at=generated_at,
    )


@bp.route('/save-card', methods=['POST'])
def save_card_route():
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    source = request.form.get('source', '').strip()
    if not question or not answer:
        flash('Kart kaydetmek icin soru ve cevap gereklidir.', 'danger')
        return redirect(url_for('main.deck'))

    save_card(current_app, question, answer, source)
    flash('Kart basariyla kaydedildi.', 'success')
    return redirect(url_for('main.deck'))


@bp.route('/cards')
def cards():
    items = list_cards(current_app)
    return render_template('cards.html', cards=items)


@bp.route('/cards/<int:card_id>/edit', methods=['GET', 'POST'])
def edit_card(card_id):
    card = get_card(current_app, card_id)
    if not card:
        flash('Kart bulunamadi.', 'danger')
        return redirect(url_for('main.cards'))
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        source = request.form.get('source', '').strip()
        if not question or not answer:
            flash('Karti guncellemek icin soru ve cevap gereklidir.', 'danger')
            return redirect(url_for('main.edit_card', card_id=card_id))
        update_card(current_app, card_id, question, answer, source)
        flash('Kart basariyla guncellendi.', 'success')
        return redirect(url_for('main.cards'))
    return render_template('edit_card.html', card=card)


@bp.route('/cards/<int:card_id>/delete', methods=['POST'])
def delete_card_route(card_id):
    delete_card(current_app, card_id)
    flash('Kart silindi.', 'success')
    return redirect(url_for('main.cards'))


@bp.route('/export', methods=['GET'])
def export_cards():
    format_type = request.args.get('format', 'csv').lower()
    cards = list_cards(current_app)
    if format_type == 'json':
        data = json.dumps(cards, indent=2)
        return send_file(
            io.BytesIO(data.encode('utf-8')),
            mimetype='application/json',
            as_attachment=True,
            download_name='flashcards.json',
        )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['id', 'question', 'answer', 'source', 'created_at'])
    for card in cards:
        writer.writerow([card['id'], card['question'], card['answer'], card['source'], card['created_at']])
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='flashcards.csv',
    )
