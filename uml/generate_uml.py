from __future__ import annotations

from pathlib import Path
from textwrap import wrap


OUT_DIR = Path(__file__).resolve().parent


def svg_document(width: int, height: int, title: str, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#334155"/>
    </marker>
    <marker id="arrow-soft" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/>
    </marker>
    <style>
      .bg {{ fill: #f8fafc; }}
      .title {{ font: 700 30px Arial, sans-serif; fill: #0f172a; }}
      .subtitle {{ font: 400 14px Arial, sans-serif; fill: #475569; }}
      .box {{ fill: #ffffff; stroke: #334155; stroke-width: 2; rx: 16; ry: 16; }}
      .box-soft {{ fill: #eff6ff; stroke: #3b82f6; stroke-width: 2; rx: 16; ry: 16; }}
      .box-warm {{ fill: #fff7ed; stroke: #f97316; stroke-width: 2; rx: 16; ry: 16; }}
      .box-green {{ fill: #ecfdf5; stroke: #10b981; stroke-width: 2; rx: 16; ry: 16; }}
      .box-violet {{ fill: #f5f3ff; stroke: #8b5cf6; stroke-width: 2; rx: 16; ry: 16; }}
      .text {{ font: 400 15px Arial, sans-serif; fill: #0f172a; }}
      .text-small {{ font: 400 13px Arial, sans-serif; fill: #334155; }}
      .text-bold {{ font: 700 16px Arial, sans-serif; fill: #0f172a; }}
      .label {{ font: 700 13px Arial, sans-serif; fill: #475569; }}
      .line {{ stroke: #334155; stroke-width: 2.2; fill: none; marker-end: url(#arrow); }}
      .line-soft {{ stroke: #64748b; stroke-width: 1.8; fill: none; marker-end: url(#arrow-soft); stroke-dasharray: 5 4; }}
      .lifeline {{ stroke: #94a3b8; stroke-width: 1.8; stroke-dasharray: 8 6; }}
    </style>
  </defs>
  <rect class="bg" x="0" y="0" width="{width}" height="{height}"/>
  <text class="title" x="40" y="48">{title}</text>
  {body}
</svg>
'''


def lines(text: str, x: float, y: float, size: int = 15, color: str = "#0f172a", anchor: str = "middle", line_height: int = 20) -> str:
    pieces = text.split("\n")
    tspans = []
    for index, piece in enumerate(pieces):
        dy = 0 if index == 0 else line_height
        tspans.append(f'<tspan x="{x}" dy="{dy}">{piece}</tspan>')
    return f'<text class="text" x="{x}" y="{y}" text-anchor="{anchor}" style="font-size:{size}px; fill:{color};">' + "".join(tspans) + "</text>"


def box(x: int, y: int, w: int, h: int, title: str, body: list[str], cls: str = "box") -> str:
    title_y = y + 28
    body_y = title_y + 24
    body_text = []
    if title:
        body_text.append(f'<text class="text-bold" x="{x + w/2}" y="{title_y}" text-anchor="middle">{title}</text>')
    for i, line in enumerate(body):
        body_text.append(f'<text class="text-small" x="{x + w/2}" y="{body_y + i * 19}" text-anchor="middle">{line}</text>')
    return f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="16" ry="16"/>' + "".join(body_text)


def arrow(x1: int, y1: int, x2: int, y2: int, label: str | None = None, dashed: bool = False) -> str:
    cls = "line-soft" if dashed else "line"
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    label_svg = ""
    if label:
        label_svg = f'<text class="label" x="{mid_x}" y="{mid_y - 6}" text-anchor="middle">{label}</text>'
    return f'<path class="{cls}" d="M {x1} {y1} L {x2} {y2}"/>' + label_svg


def vertical_lifeline(x: int, y1: int, y2: int) -> str:
    return f'<line class="lifeline" x1="{x}" y1="{y1}" x2="{x}" y2="{y2}"/>'


def wrap_lines(text: str, width: int) -> list[str]:
    result: list[str] = []
    for paragraph in text.split("\n"):
        result.extend(wrap(paragraph, width=width) or [""])
    return result


def component_diagram() -> str:
    body = []
    body.append(box(70, 150, 170, 110, "Kullanıcı", ["Metin girer", "Kartları yönetir"], "box-warm"))
    body.append(box(70, 360, 170, 110, "Tarayıcı", ["HTML / CSS", "Jinja2 sayfaları"], "box-soft"))
    body.append(box(330, 220, 260, 260, "Flask Uygulaması", ["routes.py", "__init__.py", "session yönetimi", "blueprint"], "box"))
    body.append(box(680, 120, 240, 140, "Gemini API", ["Flashcard üretimi", "JSON yanıtı"], "box-green"))
    body.append(box(680, 360, 240, 140, "SQLite DB", ["cards tablosu", "created_at"], "box-violet"))
    body.append(box(1010, 210, 300, 160, "Uygulama Katmanları", ["templates/", "static/", "nlp_utils.py", "models.py"], "box"))
    body.append(arrow(240, 205, 330, 280, "POST /, /cards"))
    body.append(arrow(330, 330, 240, 415, "render_template", dashed=True))
    body.append(arrow(590, 280, 680, 190, "generateContent"))
    body.append(arrow(680, 420, 590, 410, "CRUD sorguları"))
    body.append(arrow(590, 350, 1010, 290, "temel akış"))
    body.append(arrow(1010, 330, 420, 470, "Jinja2 / static", dashed=True))
    body.append(lines("Veri akışı: kullanıcı not girer, Flask metni işler, Gemini kart üretir,\nsonuç session'a yazılır ve SQLite'da saklanır.", 700, 560, size=15, anchor="middle"))
    return svg_document(1400, 650, "Component Diagram", "".join(body))


def class_diagram() -> str:
    body = []
    body.append(box(50, 100, 300, 210, "app.__init__", ["create_app()", "get_gemini_api_key()"], "box-soft"))
    body.append(box(400, 100, 320, 250, "app.routes", ["index()", "deck()", "cards()", "edit_card()", "export_cards()"], "box"))
    body.append(box(780, 100, 260, 210, "app.models", ["save_card()", "list_cards()", "get_card()", "update_card()", "delete_card()"], "box-violet"))
    body.append(box(1090, 100, 260, 190, "app.db", ["get_db()", "init_db()", "close_db()", "DATABASE_SCHEMA"], "box-green"))
    body.append(box(400, 400, 320, 220, "app.gemini_client", ["clean_text()", "build_flashcard_prompt()", "parse_flashcards_response()", "generate_flashcards_with_gemini()"], "box-warm"))
    body.append(box(780, 400, 260, 220, "app.nlp_utils", ["split_sentences()", "extract_keywords()", "generate_flashcards()", "generate_qa_pairs()"], "box"))

    body.append(arrow(350, 205, 400, 205, "register_blueprint"))
    body.append(arrow(720, 270, 780, 200, "calls"))
    body.append(arrow(920, 210, 1090, 210, "uses"))
    body.append(arrow(850, 310, 850, 400, "DB helpers", dashed=True))
    body.append(arrow(560, 400, 560, 310, "API request", dashed=True))
    body.append(arrow(720, 510, 780, 510, "NLP helpers"))
    body.append(lines("Not: Bu proje fonksiyon ağırlıklı olduğu için UML sınıf diyagramı, modülleri ve\nana fonksiyonları sınıf benzeri kutularla gösteriyor.", 700, 620, size=14))
    return svg_document(1400, 700, "Class Diagram", "".join(body))


def use_case_diagram() -> str:
    body = []
    body.append(box(70, 200, 200, 90, "Aktör", ["Öğrenci"], "box-warm"))
    body.append(box(1130, 200, 200, 90, "Sistem", ["Flashcard Uygulaması"], "box"))
    body.append(box(330, 90, 320, 100, "Kullanım Senaryoları", ["Metin gir", "Dosya yükle"], "box-soft"))
    body.append(box(330, 220, 320, 100, "Kullanım Senaryoları", ["Flashcard üret", "Deck görüntüle"], "box-soft"))
    body.append(box(330, 350, 320, 100, "Kullanım Senaryoları", ["Kart kaydet", "Kart düzenle / sil"], "box-soft"))
    body.append(box(760, 155, 280, 190, "Ek İşlevler", ["Kart dışa aktar (CSV/JSON)", "Geçmiş deck göster"], "box-green"))

    body.append(arrow(270, 245, 330, 140, "girdi"))
    body.append(arrow(270, 245, 330, 270, "işleme"))
    body.append(arrow(270, 245, 330, 400, "yönetim"))
    body.append(arrow(650, 140, 760, 240, "tüm işlemler"))
    body.append(arrow(650, 270, 760, 240, "sonuç gösterimi", dashed=True))
    body.append(arrow(650, 400, 760, 240, "kalıcı kayıt", dashed=True))
    body.append(lines("Kapsam özeti: uygulama metin yükleme, otomatik kart üretimi, kart yönetimi\nve dışa aktarma işlevlerini destekler.", 700, 585, size=15))
    return svg_document(1400, 650, "Use Case Diagram", "".join(body))


def sequence_diagram() -> str:
    body = []
    actors = [
        ("Kullanıcı", 100),
        ("Tarayıcı", 320),
        ("index()", 560),
        ("Gemini API", 820),
        ("Session", 1060),
        ("deck()", 1280),
    ]
    for label, x in actors:
        body.append(box(int(x - 85), 85, 170, 55, label, [], "box-soft" if label in {"Kullanıcı", "Tarayıcı"} else "box"))
        body.append(vertical_lifeline(x, 140, 900))

    messages = [
        (100, 170, 320, 170, "form gönder", False),
        (320, 220, 560, 220, "POST /", False),
        (560, 270, 820, 270, "generate_flashcards_with_gemini()", False),
        (820, 330, 560, 330, "JSON kartlar", False),
        (560, 390, 1060, 390, "session['flashcards']", False),
        (560, 450, 1280, 450, "redirect('/deck')", False),
        (1280, 520, 320, 520, "render_template('deck.html')", False),
        (320, 590, 100, 590, "çalışma kartlarını göster", True),
    ]
    for x1, y1, x2, y2, label, dashed in messages:
        body.append(arrow(x1, y1, x2, y2, label, dashed=dashed))

    body.append(lines("Akış: kullanıcı not gönderir, route metni Gemini'ye yollar, dönen kartlar session'a alınır\nve deck sayfası render edilir.", 700, 980, size=15))
    return svg_document(1400, 1030, "Sequence Diagram - Flashcard Generation", "".join(body))


def crud_sequence() -> str:
    body = []
    actors = [
        ("Kullanıcı", 100),
        ("cards()", 330),
        ("models.py", 570),
        ("SQLite", 810),
        ("edit_card()", 1080),
        ("export()", 1270),
    ]
    for label, x in actors:
        body.append(box(int(x - 85), 85, 170, 55, label, [], "box-soft" if label == "Kullanıcı" else "box"))
        body.append(vertical_lifeline(x, 140, 860))

    messages = [
        (100, 170, 330, 170, "kart listesi aç", False),
        (330, 220, 570, 220, "list_cards()", False),
        (570, 270, 810, 270, "SELECT * FROM cards", False),
        (810, 320, 570, 320, "rows", False),
        (570, 370, 330, 370, "cards.html", True),
        (100, 430, 1080, 430, "düzenle / sil", False),
        (1080, 480, 570, 480, "get_card() / update_card() / delete_card()", False),
        (570, 530, 810, 530, "CRUD sorguları", False),
        (100, 590, 1270, 590, "CSV / JSON indir", False),
        (1270, 640, 570, 640, "veri derle", False),
        (570, 690, 100, 690, "dosya", True),
    ]
    for x1, y1, x2, y2, label, dashed in messages:
        body.append(arrow(x1, y1, x2, y2, label, dashed=dashed))

    body.append(lines("Kart yönetimi, listeleme, düzenleme, silme ve dışa aktarma işlemlerini gösterir.", 700, 930, size=15))
    return svg_document(1400, 980, "Sequence Diagram - Card Management", "".join(body))


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write(OUT_DIR / "component-diagram.svg", component_diagram())
    write(OUT_DIR / "class-diagram.svg", class_diagram())
    write(OUT_DIR / "use-case-diagram.svg", use_case_diagram())
    write(OUT_DIR / "sequence-flashcard-generation.svg", sequence_diagram())
    write(OUT_DIR / "sequence-card-management.svg", crud_sequence())


if __name__ == "__main__":
    main()
