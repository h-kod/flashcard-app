import io
import csv
import json
from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, url_for
from .nlp_utils import clean_text, summarize_text, extract_keywords, generate_flashcards, generate_qa_pairs
from .models import save_card, list_cards, get_card, update_card, delete_card

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    context = {
        'summary': None,
        'keywords': [],
        'flashcards': [],
        'qas': [],
        'input_text': '',
        'selected_count': 5,
    }
    if request.method == 'POST':
        raw_text = request.form.get('note_text', '')
        card_count = int(request.form.get('card_count', 5) or 5)
        upload = request.files.get('note_file')
        if upload and upload.filename:
            raw_text = upload.read().decode('utf-8', errors='ignore')

        text = clean_text(raw_text)
        if not text:
            flash('Lütfen metin girin veya bir dosya yükleyin.', 'warning')
            return render_template('index.html', **context)

        summary = summarize_text(text)
        keywords = extract_keywords(text)
        flashcards = generate_flashcards(text, max_cards=card_count)
        qas = generate_qa_pairs(text)
        context.update({
            'summary': summary,
            'keywords': keywords,
            'flashcards': flashcards,
            'qas': qas,
            'input_text': text,
            'selected_count': card_count,
        })
    return render_template('index.html', **context)


@bp.route('/save-card', methods=['POST'])
def save_card_route():
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    source = request.form.get('source', '').strip()
    if not question or not answer:
        flash('Kart kaydetmek için soru ve cevap gereklidir.', 'danger')
        return redirect(url_for('main.index'))
    save_card(current_app, question, answer, source)
    flash('Kart başarıyla kaydedildi.', 'success')
    return redirect(url_for('main.cards'))


@bp.route('/cards')
def cards():
    items = list_cards(current_app)
    return render_template('cards.html', cards=items)


@bp.route('/cards/<int:card_id>/edit', methods=['GET', 'POST'])
def edit_card(card_id):
    card = get_card(current_app, card_id)
    if not card:
        flash('Kart bulunamadı.', 'danger')
        return redirect(url_for('main.cards'))
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        source = request.form.get('source', '').strip()
        if not question or not answer:
            flash('Kartı güncellemek için soru ve cevap gereklidir.', 'danger')
            return redirect(url_for('main.edit_card', card_id=card_id))
        update_card(current_app, card_id, question, answer, source)
        flash('Kart başarıyla güncellendi.', 'success')
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
