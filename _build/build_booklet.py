# The exercise booklet, re-laid by lessons as taught (booklet_plan.py): chapter N is exactly the homework of lesson N.
# From the original files in src/ it writes the full exercise file, the full solutions booklet and the solutions workbook
# (../materials/afm-*.pdf, .xlsx), and for each built lesson its own chapter (../lectures/lecture-N/exercises-N.pdf, solutions-N.*).
# Chapters 1 to 4 are cut exercise by exercise and renumbered; later chapters keep their pages and move one lesson forward.
# Run: python3 build_booklet.py            (all)      python3 build_booklet.py pdf | xlsx
import copy, os, re, shutil, subprocess, sys, tempfile
import fitz
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from booklet_plan import RELAID, SHIFT, NEW, CH
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, '..'))
SRC = os.path.join(H, 'src')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
FONTS = os.path.join(ROOT, '..', 'iit-build', 'fonts')
FB, FR = os.path.join(FONTS, 'davidbd.ttf'), os.path.join(FONTS, 'david.ttf')
FONT = {True: fitz.Font(fontfile=FB), False: fitz.Font(fontfile=FR)}
LESSON_FILES = [1, 2, 3]        # lessons that have a card on the site
TOP, BOT = 72, 772              # the body of a page, between the running header and the page number
OLD = sorted({int(k[0]) for k in NEW})   # chapters of the original that are cut into pieces
HEB = re.compile(r'[֐-׿]')


def vis(t):
    """Hebrew text in visual order for insert_text (left to right): words reversed in place, numbers kept."""
    out = []
    for w in t.split(' ')[::-1]:
        out.append(w[::-1] if HEB.search(w) else w)
    return ' '.join(out)


def put(page, x_right, y, t, size, bold=True, color=(0, 0, 0)):
    """Draw t so that it ends at x_right on baseline y."""
    f = FONT[bold]; name = 'dvb' if bold else 'dvr'
    w = f.text_length(t, fontsize=size)
    page.insert_text((x_right - w, y), t, fontsize=size, fontname=name, fontfile=FB if bold else FR, color=color)
    return w


def chapters(doc):
    """Old chapter label -> first page, from the big ״שיעור N״ banners; plus the page after the last chapter."""
    st = []
    for i in range(doc.page_count):
        for b in doc[i].get_text('dict')['blocks'][:4]:
            for l in b.get('lines', []):
                for s in l['spans']:
                    if abs(s['size'] - 20) < .3 and 'שיעור' in s['text']:
                        st.append((re.sub(r'\s*שיעור\s*', '', s['text']).strip()[::-1] if 'א' in s['text'] else re.sub(r'\s*שיעור\s*', '', s['text']).strip(), i))
    end = next((i for i in range(st[-1][1], doc.page_count) if doc[i].get_text().lstrip().startswith('נספח')), doc.page_count)
    return st, end


def anchors(doc, ch, p0, p1):
    """Where each exercise, exam and exam section of old chapter ch starts: [(key, page, y)], in reading order."""
    out = []
    for i in range(p0, p1 + 1):
        for b in sorted((b for b in doc[i].get_text('dict')['blocks'] if 'lines' in b), key=lambda b: b['bbox'][1]):
            t = ' '.join(s['text'] for l in b['lines'] for s in l['spans'])
            y = b['bbox'][1] - 7
            m = re.match(r'\s*תרגיל\s*(\d)\.(\d+)', t)
            if m and len(t) < 110 and int(m.group(1)) == ch:
                out.append((f'{ch}.{m.group(2)}', i, y)); continue
            m = re.search(r'(\d)\s*תרגיל בסגנון בחינה', t)
            if m and 'לתוכן העניינים' in t:
                out.append((f'{ch}E{m.group(1)}', i, y)); continue
            m = re.match(r'\s*סעיף ([אבגד])\s', t)
            if m and 'לתוכן העניינים' in t: out.append((f'S{m.group(1)}', i, y))
            elif re.match(r'\s*תרגילים (מאתגרים|בסגנון בחינה)\s*$', t): out.append(('intro', i, y))
    return out


def content_bottom(page, y0, y1):
    ys = [b[3] for b in page.get_text('blocks') if b[1] >= y0 - 1 and b[3] <= y1 + 1 and b[1] > TOP - 2 and b[3] < BOT]
    ys += [d['rect'].y1 for d in page.get_drawings() if d['rect'].y0 >= y0 - 1 and d['rect'].y1 <= y1 + 1 and d['rect'].y1 < BOT]
    return min(y1, max(ys) + 6) if ys else None


def pieces(doc, A, key, end_page):
    i = next(j for j, a in enumerate(A) if a[0] == key)
    j = i + 1
    while j < len(A) and A[j][0].startswith('S'): j += 1
    (_, p0, y0) = A[i]
    (p1, y1) = (A[j][1], A[j][2]) if j < len(A) else (end_page, TOP)
    out = []
    for p in range(p0, p1 + 1):
        a = y0 if p == p0 else TOP
        b = y1 if p == p1 else BOT
        if b - a < 4: continue
        cb = content_bottom(doc[p], a, b)
        if cb and cb - a > 4: out.append((p, a, cb))
    return out


_pm = {}
def bg(doc, pno, x, y):
    k = (id(doc), pno)
    if k not in _pm: _pm[k] = doc[pno].get_pixmap(dpi=72)
    pm = _pm[k]
    r, g, b = pm.pixel(max(0, min(pm.width - 1, int(x))), max(0, min(pm.height - 1, int(y))))[:3]
    return (r / 255, g / 255, b / 255)


def header_spans(page, y0=0, y1=9999):
    """The spans that carry an exercise number, an exam number or a chapter number, with their number glyphs (leftmost run)."""
    out = []
    for b in page.get_text('rawdict')['blocks']:
        for l in b.get('lines', []):
            for s in l['spans']:
                if not (y0 - 1 <= s['bbox'][1] and s['bbox'][3] <= y1 + 1): continue
                t = ''.join(c['c'] for c in s['chars'])
                kind = ('ex' if abs(s['size'] - 12.5) < .3 and re.search(r'תרגיל', t) and re.search(r'\d', t) else
                        'exam' if abs(s['size'] - 16) < .3 and 'בסגנון בחינה' in t and re.search(r'\d', t) else
                        'chap' if abs(s['size'] - 20) < .3 and 'שיעור' in t else None)
                if not kind: continue
                cs = sorted((c for c in s['chars']), key=lambda c: c['bbox'][0])
                grp = []
                for c in cs:
                    if c['c'] == ' ':
                        if grp: break
                        continue
                    grp.append(c)
                out.append(dict(kind=kind, tok=''.join(c['c'] for c in grp), x0=grp[0]['bbox'][0], x1=grp[-1]['bbox'][2], y0=s['bbox'][1], y1=s['bbox'][3], base=grp[0]['origin'][1], size=s['size']))
    return out


def renumber(page, sp, new, dy=0, src=None, spno=None):
    """Cover the number of a header and draw the new one, ending where the old one ended."""
    col = bg(src, spno, sp['x0'] - 2.5, (sp['y0'] + sp['y1']) / 2) if src is not None else (1, 1, 1)
    w = FONT[True].text_length(new, fontsize=sp['size'])
    page.draw_rect(fitz.Rect(min(sp['x0'], sp['x1'] - w) - 1, sp['y0'] + dy, sp['x1'] + .6, sp['y1'] + dy), color=None, fill=col)
    put(page, sp['x1'], sp['base'] + dy, new, sp['size'])


def prepare(src, first, nxt):
    """Renumber the source in place, before anything is cut from it: in the chapters that are re-laid, every exercise and exam
    header gets its new number; in the chapters that only move, the chapter number changes. The old glyphs are removed, not covered."""
    shift = dict(SHIFT)
    for lab, p0 in first.items():
        for pno in range(p0, nxt[lab]):
            page = src[pno]; todo = []
            for sp in header_spans(page):
                if lab in shift:
                    new = shift[lab]
                    t = (('א' + new[:-1]) if new.endswith('א') else new) if sp['kind'] == 'chap' else re.sub(r'^\d+', new.rstrip('א'), sp['tok']) if sp['kind'] == 'ex' else None
                else:
                    key = sp['tok'] if sp['kind'] == 'ex' else f'{lab}E{sp["tok"]}' if sp['kind'] == 'exam' else None
                    t = NEW.get(key) if key else None
                if t is None: continue
                todo.append((sp, t, bg(src, pno, sp['x0'] - 2.5, (sp['y0'] + sp['y1']) / 2)))
            for sp, t, col in todo:
                page.add_redact_annot(fitz.Rect(sp['x0'] - .3, sp['y0'] + 1, sp['x1'] - .4, sp['y1'] - 1), fill=col)
            if todo:
                page.apply_redactions(images=0, graphics=0)
                for sp, t, col in todo:
                    w = FONT[True].text_length(t, fontsize=sp['size'])
                    if w > sp['x1'] - sp['x0'] + .5: page.draw_rect(fitz.Rect(sp['x1'] - w - 1, sp['y0'] + 1, sp['x0'], sp['y1'] - 1), color=None, fill=col)
                    put(page, sp['x1'], sp['base'], t, sp['size'])
    _pm.clear()


def chrome_pdf(html, name):
    d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
    for f in ('david.ttf', 'davidbd.ttf'): shutil.copy(os.path.join(FONTS, f), d)
    open(os.path.join(d, name + '.html'), 'w', encoding='utf8').write(html)
    out = os.path.join(d, name + '.pdf')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/p', '--no-pdf-header-footer', '--virtual-time-budget=5000', f'--print-to-pdf={out}', 'file://' + os.path.join(d, name + '.html')], capture_output=True, timeout=180)
    return fitz.open(out)


CSS = '''@font-face{font-family:"David";src:url("david.ttf");font-weight:400}@font-face{font-family:"David";src:url("davidbd.ttf");font-weight:700}
html{direction:rtl}body{font-family:"David";color:#000;margin:0}.n{direction:ltr;unicode-bidi:isolate;display:inline-block}'''
N = lambda s: f'<span class="n">{s}</span>'


def banners(kind):
    """One small page per re-laid chapter: the chapter box, its title and what it holds, in the look of the booklet."""
    pages = ''
    for c, P in RELAID.items():
        n = sum(len(i) for _, i in P['groups']); e = len(P['exams'])
        rows = ''.join(f'<tr><td>{g}</td><td>{"תרגילים" if len(i) > 1 else "תרגיל"} {N(NEW[i[0]])}{("" if len(i) == 1 else (" ו-" if len(i) == 2 else " עד ") + N(NEW[i[-1]]))}</td></tr>' for g, i in P['groups'])
        if e: rows += f'<tr><td>תרגילים בסגנון בחינה</td><td>{"תרגיל" if e == 1 else "תרגילים"} {N(1)}{"" if e == 1 else (" ו-" if e == 2 else " עד ") + N(e)}</td></tr>'
        pages += (f'<div class="pg"><div class="bx b1">שיעור {N(c)}</div><div class="bx b2">{P["title"]}</div>'
                  f'<div class="cnt">{N(n)} תרגילים{"" if not e else "  |  " + (N(e) + " תרגילים בסגנון בחינה" if e > 1 else "תרגיל אחד בסגנון בחינה")}</div>'
                  f'<table><tr><th>הנושא</th><th>{"התרגילים" if kind == "ex" else "הפתרונות"}</th></tr>{rows}</table></div>')
    html = (f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>{CSS}@page{{size:595.28pt 300pt;margin:0}}'
            '.pg{width:595.28pt;height:300pt;box-sizing:border-box;padding:6pt 68pt 0 68pt;break-after:page;overflow:hidden}'
            '.bx{border:1.4pt solid #000;padding:5pt 10pt;font-weight:700;margin-bottom:7pt}.b1{font-size:20pt}.b2{font-size:15pt;line-height:1.3}'
            '.cnt{font-size:11pt;margin:2pt 0 8pt}table{border-collapse:collapse;width:100%;font-size:11.5pt}th,td{border:.8pt solid #888;padding:3pt 8pt;text-align:right}th{background:#eee}'
            f'</style></head><body>{pages}</body></html>')
    return chrome_pdf(html, 'ban')


def front(kind, toc, total):
    """Instructions and table of contents, rebuilt for the new layout."""
    what = 'קובץ תרגילים' if kind == 'ex' else 'חוברת פתרונות מפורטים'
    rows = ''.join(f'<tr><td>שיעור {N(lab)}</td><td>{title}</td><td>{N(p)}</td></tr>' for lab, title, p in toc)
    inst = ('''<p>הקובץ בנוי לפי השיעורים כפי שנלמדו בפועל: פרק לכל שיעור, ובו בדיוק התרגילים שמתאימים לחומר של אותו שיעור. לכן תרגילי הבית של שיעור הם כל הפרק שלו, ולא צריך לחפש תרגילים בפרקים אחרים.</p>
<p>בתוך כל פרק התרגילים מסודרים לפי נושא, ובכל נושא מהקל אל הכבד. רמת הקושי מסומנת בכוכבים. בסוף הפרק תרגילים בסגנון בחינה: סיפור רקע אחד וכמה סעיפים.</p>
<p>כל התרגילים הם שאלות אמריקאיות עם חמש תשובות, ותשובה אחת נכונה בלבד. פותרים ב-Excel: בונים את החישוב בגיליון, ורק אחר כך בוחרים תשובה. כשלא נאמר אחרת, הערך הנקוב של אג״ח הוא 100 ש״ח.</p>
<p>פתרונות מלאים נמצאים בחוברת הפתרונות ובקובץ ה-Excel הנלווה, באותו מספור.</p>''' if kind == 'ex' else
            '''<p>החוברת בנויה לפי השיעורים כפי שנלמדו בפועל, באותו סדר ובאותו מספור כמו קובץ התרגילים: פרק לכל שיעור.</p>
<p>כל פתרון מתחיל במה נתון ומה נדרש, ממשיך בשלבים, ומסתיים בתשובה ובהסבר למה כל אחת מהתשובות האחרות שגויה. כדאי לפתור כל תרגיל בעצמכם, ורק אחר כך לבדוק מול הפתרון.</p>''')
    html = (f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>{CSS}@page{{size:A4;margin:20mm 24mm 18mm}}body{{font-size:11.5pt;line-height:1.38}}'
            'h1{font-size:19pt;border:1.4pt solid #000;padding:5pt 10pt;margin:0 0 4mm}h2{font-size:14pt;margin:5mm 0 2mm}p{margin:0 0 2.5mm}'
            'table{border-collapse:collapse;width:100%}td{border-bottom:.6pt solid #999;padding:2.5pt 6pt;vertical-align:top}td:first-child{font-weight:700;white-space:nowrap;width:22mm}td:last-child{width:12mm;text-align:left}'
            '.upd{font-size:11pt;color:#444;margin-top:6mm}'
            f'</style></head><body><h1>{what}: הנחיות ותוכן עניינים</h1>{inst}<h2>תוכן העניינים</h2><table>{rows}</table>'
            f'<p class="upd">מהדורה מעודכנת לפי ההספק בשיעורים. שיעורים {N(1)} עד {N(max(LESSON_FILES))} מותאמים למה שנלמד בפועל; הפרקים שאחריהם יותאמו אחרי כל שיעור. סך הכל {N(total)} עמודים.</p></body></html>')
    f = chrome_pdf(html, 'front'); assert len(f) == 1, 'the front page must fit one page'
    return f


def footers(doc, skip=1):
    n = doc.page_count
    for i in range(skip, n):
        p = doc[i]
        p.draw_rect(fitz.Rect(0, BOT + 2, p.rect.width, p.rect.height - 20), color=None, fill=(1, 1, 1))
        t = f'{n} ' + 'ךותמ' + f' {i + 1} ' + 'דומע'
        w = FONT[False].text_length(t, fontsize=9.5)
        p.insert_text(((p.rect.width - w) / 2, 788), t, fontsize=9.5, fontname='dvr', fontfile=FR, color=(.2, .2, .2))


def build_pdf(kind):
    src = fitz.open(os.path.join(SRC, 'afm-exercises.pdf' if kind == 'ex' else 'afm-solutions.pdf'))
    st, end = chapters(src)
    first = {lab: p for lab, p in st}; nxt = {st[i][0]: (st[i + 1][1] if i + 1 < len(st) else end) for i in range(len(st))}
    A = {c: anchors(src, c, first[str(c)], nxt[str(c)] - 1) for c in OLD}
    prepare(src, first, nxt)
    W, Hh = src[0].rect.width, src[0].rect.height
    ban = banners(kind)
    body = fitz.open(); toc = []; rng = {}
    strip_page = first['1'] + 1
    def newpage():
        pg = body.new_page(width=W, height=Hh)
        pg.show_pdf_page(fitz.Rect(0, 40, W, TOP), src, strip_page, clip=fitz.Rect(0, 40, W, TOP))
        return pg
    count = 0
    for c, P in RELAID.items():
        page = newpage(); p0 = body.page_count - 1
        toc.append((str(c), P['title'], p0))
        bh = 78 + 26 * (1 + (len(P['title']) > 62)) + 30 + 19 * (1 + len(P['groups']) + (1 if P['exams'] else 0))
        page.show_pdf_page(fitz.Rect(0, TOP + 2, W, TOP + 2 + 300), ban, c - 1)
        y = TOP + 2 + bh
        keys = [k for _, it in P['groups'] for k in it] + P['exams']
        for key in keys:
            oc = int(key[0])
            for n_piece, (p, a, b) in enumerate(pieces(src, A[oc], key, nxt[str(oc)])):
                h = b - a
                if y + h > BOT:
                    page = newpage(); y = TOP + 4
                page.show_pdf_page(fitz.Rect(0, y, W, y + h), src, p, clip=fitz.Rect(0, a, W, b))
                y += h + 6
            y += 6; count += 1
        rng[c] = (p0, body.page_count)
    # the chapters after them: their own pages, one lesson forward
    for old, new in SHIFT:
        p0 = body.page_count
        body.insert_pdf(src, from_page=first[old], to_page=nxt[old] - 1, links=False, annots=False)
        toc.append((new, None, p0)); rng[new] = (p0, body.page_count)
    return src, body, toc, rng, first


OLD_TITLES = {'5': 'תקופות חלקיות ותשואה לתקופת החזקה, מק״מ, אג״ח צמיתה ומשמעות המח״מ', '6': 'אג״ח צמודות: מדד ודולר, ריאלי מול נומינלי, חילוץ תשואה והתאמות זמן', '6א': 'מח״מ: חישוב מספרי וחיסון פיננסי',
              '7': 'תמחור מניות: מודל הדיבידנדים והצמיחה, תשואת דיבידנד, מכפיל רווח ו-PVGO', '8': 'תמחור מניות, יישומים: מכפיל ענפי, PVGO, תשואת דיבידנד, צמיחה משתנה ודיבידנד רבעוני', '10': 'מודיליאני ומילר: מבנה ההון ושווי החברה'}


def pdfs():
    for kind, name in (('ex', 'exercises'), ('sol', 'solutions')):
        src, body, toc, rng, first = build_pdf(kind)
        total = body.page_count + 2
        fr = front(kind, [(lab, t or OLD_TITLES[lab], p + 3) for lab, t, p in toc], total)
        full = fitz.open(); full.insert_pdf(src, from_page=0, to_page=0, links=False); full.insert_pdf(fr); full.insert_pdf(body)
        # each built lesson: the cover and its chapter, numbered on its own
        for c in LESSON_FILES:
            d = fitz.open(); d.insert_pdf(src, from_page=0, to_page=0, links=False); d.insert_pdf(body, from_page=rng[c][0], to_page=rng[c][1] - 1)
            footers(d)
            out = os.path.join(ROOT, 'lectures', f'lecture-{c}'); os.makedirs(out, exist_ok=True)
            d.save(os.path.join(out, f'{name}-{c}.pdf'), garbage=4, deflate=True)
            # every exercise of the chapter, in order, and nothing else: the headers read back from the new file
            got = [sp['text'].strip() for i in range(1, d.page_count) for b in sorted(d[i].get_text('dict')['blocks'], key=lambda b: b['bbox'][1]) for l in b.get('lines', []) for sp in l['spans']
                   if abs(sp['size'] - 12.5) < .3 and re.fullmatch(r'\s*\d+\.\d+\s*', sp['text'])]
            want = [NEW[k] for _, it in RELAID[c]['groups'] for k in it]
            assert got == want, (kind, c, got, want)
            old = [m for i in range(1, d.page_count) for m in re.findall(r'תרגיל\s*\d+\.\d+', d[i].get_text())]
            assert not old, ('an old number is still in the text', old[:5])
            print(name, 'lesson', c, 'pages', d.page_count, 'exercises', len(want), 'exams', len(RELAID[c]['exams']))
        footers(full)
        full.save(os.path.join(ROOT, 'materials', f'afm-{name}.pdf'), garbage=4, deflate=True)
        print(name, 'full pages', full.page_count, 'was', src.page_count)


# ---------------------------------------------------------------- the solutions workbook, in the same layout
REFS = re.compile(r'("[^"]*")|(\$?)([A-Z]{1,2})(\$?)(\d+)(?![\d(A-Za-z])')


def xlsx():
    W0 = load_workbook(os.path.join(SRC, 'afm-solutions.xlsx'))
    starts, order, titles = {}, {}, {}
    for c in OLD:
        ws0 = W0[f'שיעור {c}']; st = {}
        for r in range(1, ws0.max_row + 1):
            v = ws0.cell(r, 1).value
            if isinstance(v, str):
                m = re.match(r'תרגיל (\d\.\d+)\s+\|', v) or re.match(r'תרגיל בסגנון בחינה (\d)\s+\|', v)
                if m: st[m.group(1) if '.' in m.group(1) else f'{c}E{m.group(1)}'] = r
        starts[c] = st; order[c] = sorted(st, key=st.get)
        for k in st: titles[k] = re.split(r'\s+\|\s+', ws0.cell(st[k], 1).value, maxsplit=1)[1]
    def block(key):
        c = int(key[0]); ws0 = W0[f'שיעור {c}']; a = starts[c][key]; i = order[c].index(key)
        b = starts[c][order[c][i + 1]] if i + 1 < len(order[c]) else ws0.max_row + 1
        while b - 1 > a and all(v.value is None for v in ws0[b - 1]): b -= 1
        return c, a, b
    wb = Workbook(); toc = wb.active; toc.title = 'תוכן'; toc.sheet_view.rightToLeft = True
    mapping, index = [], []
    def copy_rows(ws, ws0, sheet0, a, b, r_out, rename=None):
        dr = r_out - a
        for r in range(a, b):
            if ws0.row_dimensions[r].height: ws.row_dimensions[r + dr].height = ws0.row_dimensions[r].height
            for x in ws0[r]:
                if x.value is None and not x.has_style: continue
                n = ws.cell(r + dr, x.column); v = x.value
                if isinstance(v, str) and v.startswith('='):
                    assert '!' not in v, ('a formula reads another sheet', x.coordinate)
                    v = REFS.sub(lambda m: m.group(1) or f'{m.group(2)}{m.group(3)}{m.group(4)}{int(m.group(5)) + dr}', v)
                    mapping.append((sheet0, x.coordinate, ws.title, n.coordinate))
                elif rename and isinstance(v, str): v = rename(v)
                n.value = v
                if x.has_style:
                    n.font, n.fill, n.border, n.alignment = copy.copy(x.font), copy.copy(x.fill), copy.copy(x.border), copy.copy(x.alignment)
                    n.number_format, n.protection = x.number_format, copy.copy(x.protection)
        for mr in ws0.merged_cells.ranges:
            if a <= mr.min_row and mr.max_row < b:
                ws.merge_cells(start_row=mr.min_row + dr, start_column=mr.min_col, end_row=mr.max_row + dr, end_column=mr.max_col)
        return b + dr
    for c, P in RELAID.items():
        ws = wb.create_sheet(f'שיעור {c}'); ws.sheet_view.rightToLeft = True
        for k, dim in W0['שיעור 1'].column_dimensions.items(): ws.column_dimensions[k].width = dim.width
        r_out = copy_rows(ws, W0['שיעור 1'], 'שיעור 1', 1, 4, 1) + 2
        ws['A1'] = f'פתרונות שיעור {c}: {P["title"]}'
        index.append((ws.title, None, f'שיעור {c}: {P["title"]}', 1))
        for key in [k for _, it in P['groups'] for k in it] + P['exams']:
            oc, a, b = block(key)
            head = (f'תרגיל {NEW[key]}' if 'E' not in key else f'תרגיל בסגנון בחינה {NEW[key]}')
            index.append((ws.title, head, titles[key], r_out))
            end = copy_rows(ws, W0[f'שיעור {oc}'], f'שיעור {oc}', a, b, r_out)
            ws.cell(r_out, 1).value = f'{head}  |  {titles[key]}'
            r_out = end + 1
    for old, new in SHIFT:
        ws0 = W0[f'שיעור {old}']; ws = wb.create_sheet(f'שיעור {new}'); ws.sheet_view.rightToLeft = True
        for k, dim in ws0.column_dimensions.items(): ws.column_dimensions[k].width = dim.width
        ren = lambda v, old=old, new=new: re.sub(r'^(תרגיל )' + re.escape(old) + r'(?=[.א])', r'\g<1>' + new.rstrip('א') if not old.endswith('א') else r'\g<1>' + new, v) if v.startswith('תרגיל ') else re.sub(r'^(פתרונות שיעור )' + re.escape(old) + r'(?=[:\s])', r'\g<1>' + new, v)
        copy_rows(ws, ws0, f'שיעור {old}', 1, ws0.max_row + 1, 1, rename=ren)
        index.append((ws.title, None, str(ws['A1'].value).replace('פתרונות ', ''), 1))
        for r in range(1, ws.max_row + 1):
            v = ws.cell(r, 1).value
            if isinstance(v, str) and re.match(r'תרגיל .+\s+\|', v):
                h, t = re.split(r'\s+\|\s+', v, maxsplit=1); index.append((ws.title, h, t, r))
    # the contents sheet, with a link to every exercise
    for i, t in enumerate(['פתרונות קובץ התרגילים באקסל: מימון מתקדם לחשבונאים', W0['תוכן']['A2'].value, W0['תוכן']['A3'].value, 'הגיליונות בנויים לפי השיעורים כפי שנלמדו בפועל, באותו מספור כמו קובץ התרגילים. לחצו על שם הגיליון או על תרגיל כדי לעבור אליו.'], 1):
        toc.cell(i, 1, t).font = Font(name='Arial', size=14 if i == 1 else 11, bold=i == 1)
    toc.column_dimensions['A'].width = 30; toc.column_dimensions['B'].width = 90
    r = 6
    for sheet, head, title, row in index:
        a = toc.cell(r, 1, head or sheet); a.hyperlink = f"#'{sheet}'!A{row}"; a.font = Font(name='Arial', size=11, bold=head is None, color='1B2D55', underline='single')
        toc.cell(r, 2, title).font = Font(name='Arial', size=11, bold=head is None)
        r += 1
    wb.calculation.fullCalcOnLoad = True
    out = os.path.join(ROOT, 'materials', 'afm-solutions.xlsx'); wb.save(out)
    d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
    def recalc(f):
        pr = subprocess.Popen(['soffice', '--headless', f'-env:UserInstallation=file://{d}/lo', '--convert-to', 'xlsx:Calc MS Excel 2007 XML', '--outdir', d, f], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try: pr.wait(timeout=1200)
        except subprocess.TimeoutExpired: pr.kill(); raise SystemExit('LibreOffice did not finish')
        return os.path.join(d, os.path.basename(f))
    rn = recalc(out); os.rename(rn, os.path.join(d, 'new.xlsx'))
    V = load_workbook(os.path.join(d, 'new.xlsx'), data_only=True); V0 = load_workbook(recalc(os.path.join(SRC, 'afm-solutions.xlsx')), data_only=True)
    same = lambda p, q: p == q or (isinstance(p, (int, float)) and isinstance(q, (int, float)) and abs(p - q) < 1e-9 * max(1, abs(p)))
    bad = [(s0, a, s1, b, V0[s0][a].value, V[s1][b].value) for s0, a, s1, b in mapping if not same(V0[s0][a].value, V[s1][b].value)]
    errs = [(ws.title, x.coordinate) for ws in V for row in ws.iter_rows() for x in row if isinstance(x.value, str) and x.value.startswith('#')]
    n0 = sum(1 for ws in W0 for row in ws.iter_rows() for x in row if isinstance(x.value, str) and x.value.startswith('='))
    print('workbook sheets', wb.sheetnames, 'formulas', len(mapping), 'of', n0, 'mismatch', bad[:4], 'errors', errs[:4])
    assert not bad and not errs and len(mapping) == n0
    shutil.copy(os.path.join(d, 'new.xlsx'), out)
    for c in LESSON_FILES:
        one = load_workbook(out)
        for ws in list(one):
            if ws.title != f'שיעור {c}': del one[ws.title]
        one.save(os.path.join(ROOT, 'lectures', f'lecture-{c}', f'solutions-{c}.xlsx'))
    shutil.rmtree(d, True)


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if what in ('all', 'pdf'): pdfs()
    if what in ('all', 'xlsx'): xlsx()
