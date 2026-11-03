# Each lesson's homework: the exercises of the exercise file that match what was actually taught in that lesson.
# The chapters of the file do not follow the meetings one to one (lesson 1 ended before amortizing bonds), so the
# exercises are cut out one by one: from the exercise file, from the solutions booklet, and the blocks of the solutions workbook.
# Run: python3 build_homework.py 1  ->  ../lectures/lecture-1/exercises-1.pdf, solutions-1.pdf, solutions-1.xlsx
# Item keys: '1.3' is exercise 1.3; '1E1' is exam-style exercise 1 of chapter 1; '1E1:אבג' keeps sections א to ג only.
import copy, os, re, shutil, subprocess, sys, tempfile
import fitz
from openpyxl import Workbook, load_workbook
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, '..'))
LESSON = int(sys.argv[1]) if len(sys.argv) > 1 else 1
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
FONTS = os.path.join(ROOT, '..', 'iit-build', 'fonts')

# what was taught (Shay, 2026-11-03): lesson 1 reached the amortizing bond slide; amortizing bonds and value between payment
# dates are lesson 2. Extracting the yield to maturity (IRR and RATE) is the next lesson.
HW = {
 1: dict(items=['1.1', '1.2', '1.4', '1.5', '1.6', '1.8', '1.9', '1.17', '1.18'],
         topic='אג״ח עם קופון קבוע: שווי בטבלה וב-NPV או ב-PV, פרמיה ונכיון, קופון חצי שנתי ורבעוני והמרת ריבית',
         later='שאר התרגילים בפרק 1 עוסקים באג״ח לשיעורין ובשווי בין מועדי תשלום, ונמצאים בתרגילי הבית של שיעור 2.'),
 2: dict(items=['1.3', '1.7', '1.10', '1.11', '1.12', '1.13', '1.14', '1.15', '1.16', '1E1', '1E2',
                '2.1', '2.3', '2.4', '2.6', '2.7', '2.8', '2.9', '2.11', '2.13', '2.15', '2.17', '2E1'],
         topic='אג״ח לשיעורין ושווי לאורך חיי האג״ח: מיד אחרי קופון, רגע לפני קופון ובין מועדי תשלום',
         later='תרגילים 2.2, 2.5, 2.10, 2.12, 2.14 ו-2.16 ותרגיל בסגנון בחינה 2 בפרק 2 עוסקים בחילוץ תשואה לפדיון ב-IRR וב-RATE. הם יצורפו לשיעור שבו נלמד הנושא.'),
}[LESSON]
# per chapter: pages (0-based) of the exercise file and of the booklet, first..last and the first page of the next chapter
CH = {1: dict(ex=(4, 16, 17), sol=(4, 50, 51)), 2: dict(ex=(17, 28, 29), sol=(51, 102, 103))}
EXF, SOLF, SOLX = (os.path.join(ROOT, 'materials', f) for f in ('afm-exercises.pdf', 'afm-solutions.pdf', 'afm-solutions.xlsx'))
OUT = os.path.join(ROOT, 'lectures', f'lecture-{LESSON}')
TOP, BOT = 72, 772          # the body of a page, between the running header and the page number


def anchors(doc, ch, p0, p1):
    """Where each exercise, exam and exam section of chapter ch starts: [(key, page, y)], in reading order, pages p0..p1."""
    out = []
    for i in range(p0, p1 + 1):
        for b in sorted((b for b in doc[i].get_text('dict')['blocks'] if 'lines' in b), key=lambda b: b['bbox'][1]):
            t = ' '.join(s['text'] for l in b['lines'] for s in l['spans'])
            y = b['bbox'][1] - 7
            m = re.match(r'\s*תרגיל\s*(\d)\.(\d+)', t)
            if m and len(t) < 110 and (ch == 0 or int(m.group(1)) == ch):
                out.append((f'{m.group(1)}.{m.group(2)}', i, y)); continue
            m = re.search(r'(\d)\s*תרגיל בסגנון בחינה', t)
            if m and 'לתוכן העניינים' in t:
                out.append((f'{ch or ""}E{m.group(1)}', i, y)); continue
            m = re.match(r'\s*סעיף ([אבגד])\s', t)
            if m and 'לתוכן העניינים' in t:
                out.append((f'S{m.group(1)}', i, y))
            elif re.match(r'\s*תרגילים מאתגרים\s*$', t):
                out.append(('intro', i, y))
    return out


def content_bottom(page, y0, y1):
    ys = [b[3] for b in page.get_text('blocks') if b[1] >= y0 - 1 and b[3] <= y1 + 1 and b[1] > TOP - 2 and b[3] < BOT]
    ys += [d['rect'].y1 for d in page.get_drawings() if d['rect'].y0 >= y0 - 1 and d['rect'].y1 <= y1 + 1 and d['rect'].y1 < BOT]
    return min(y1, max(ys) + 6) if ys else None


def pieces(doc, A, key, end_page):
    """The regions of one item: from its anchor to the next anchor, across pages."""
    k, keep = (key.split(':') + [None])[:2]
    i = next(j for j, a in enumerate(A) if a[0] == k)
    j = i + 1
    while j < len(A) and A[j][0].startswith('S'):
        if keep and A[j][0][1] not in keep: break
        j += 1
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


def compose(src, kind, front):
    """A new PDF: the front pages, then every item's regions flowed onto pages, under the running header of the source."""
    doc = fitz.open()
    for f in front:
        if isinstance(f, int): doc.insert_pdf(src, from_page=f, to_page=f)
        else: doc.insert_pdf(f)
    W, Hh = src[0].rect.width, src[0].rect.height
    A = {c: anchors(src, c, *CH[c][kind][:2]) for c in CH}
    page, y = None, None
    for key in HW['items']:
        c = int(key[0])
        assert key.split(':')[0] in {a[0] for a in A[c]}, (kind, key)
        for (p, a, b) in pieces(src, A[c], key, CH[c][kind][2]):
            h = b - a
            if page is None or y + h > BOT:
                page = doc.new_page(width=W, height=Hh)
                page.show_pdf_page(fitz.Rect(0, 40, W, TOP), src, CH[1][kind][0] + 1, clip=fitz.Rect(0, 40, W, TOP))
                y = TOP + 4
            page.show_pdf_page(fitz.Rect(0, y, W, y + h), src, p, clip=fitz.Rect(0, a, W, b))
            y += h + 6
        y += 6
    return doc


def front_page(kind, titles):
    """One page in the house style: which exercises, from which chapter, and what waits for a later lesson."""
    chs = sorted({int(k[0]) for k in HW['items']})
    chap = 'בפרק ' + ' ובפרק '.join(str(c) for c in chs)
    lis = ''.join(f'<li><b dir="ltr">{k}</b> {t}</li>' for k, t in titles)
    html = f'''<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
@font-face{{font-family:"David";src:url("david.ttf");font-weight:400}}@font-face{{font-family:"David";src:url("davidbd.ttf");font-weight:700}}
@page{{size:A4;margin:18mm 22mm}}body{{font-family:"David";font-size:{13.5 if len(titles) < 15 else 12}pt;line-height:1.4;color:#16213a}}
h1{{font-size:24pt;color:#1b2d55;margin:0 0 2mm}}h2{{font-size:15pt;color:#c4421f;margin:0 0 6mm;font-weight:700}}
ol{{padding-right:7mm;margin:3mm 0 6mm}}li{{margin:1mm 0}}li b{{display:inline-block;min-width:22mm;unicode-bidi:isolate}}
.n{{background:#f4f6fb;border-right:4px solid #1b2d55;padding:4mm 6mm;font-size:12pt}}</style></head><body>
<h1>שיעור {LESSON}: {'תרגילי בית' if kind == 'ex' else 'פתרונות תרגילי הבית'}</h1>
<h2>{HW['topic']}</h2>
<p>{f'התרגילים {chap} בקובץ התרגילים שמתאימים למה שנלמד בשיעור, באותו מספור כמו בקובץ המלא:' if kind == 'ex' else f'הפתרונות {chap} בחוברת הפתרונות, לתרגילי הבית של השיעור, באותו מספור. פותחים רק אחרי שפותרים.'}</p>
<ol>{lis}</ol>
<div class="n">{HW['later']}</div></body></html>'''
    d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
    for f in ('david.ttf', 'davidbd.ttf'): shutil.copy(os.path.join(FONTS, f), d)
    open(os.path.join(d, 'f.html'), 'w', encoding='utf8').write(html)
    out = os.path.join(d, 'f.pdf')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/p', '--no-pdf-header-footer', '--virtual-time-budget=5000', f'--print-to-pdf={out}', 'file://' + os.path.join(d, 'f.html')], capture_output=True, timeout=180)
    f = fitz.open(out); assert len(f) == 1, 'the front page must fit one page'
    return f


# ---------------------------------------------------------------- the solutions workbook: one sheet, the same blocks
REFS = re.compile(r'("[^"]*")|(\$?)([A-Z]{1,2})(\$?)(\d+)(?![\d(A-Za-z])')
WB0 = load_workbook(SOLX)
STARTS, ORDER, TITLES = {}, {}, {}
for c in CH:
    ws0 = WB0[f'שיעור {c}']; st = {}
    for r in range(1, ws0.max_row + 1):
        v = ws0.cell(r, 1).value
        if isinstance(v, str):
            m = re.match(r'תרגיל (\d\.\d+)\s+\|', v) or re.match(r'תרגיל בסגנון בחינה (\d)\s+\|', v)
            if m: st[m.group(1) if '.' in m.group(1) else f'{c}E{m.group(1)}'] = r
    STARTS[c] = st; ORDER[c] = sorted(st, key=st.get)
    for k in st: TITLES[k] = re.split(r'\s+\|\s+', ws0.cell(st[k], 1).value, maxsplit=1)[1]


def block_rows(key):
    k, keep = (key.split(':') + [None])[:2]
    c = int(k[0]); ws0 = WB0[f'שיעור {c}']; st, order = STARTS[c], ORDER[c]
    a = st[k]; i = order.index(k)
    b = st[order[i + 1]] if i + 1 < len(order) else ws0.max_row + 1
    if keep:
        for r in range(a, b):
            v = ws0.cell(r, 1).value
            if isinstance(v, str) and re.fullmatch(r'סעיף ([אבגד])', v.strip()) and v.strip()[-1] not in keep:
                b = r; break
    while b - 1 > a and all(x.value is None for x in ws0[b - 1]): b -= 1
    return c, a, b


def build_xlsx():
    wb = Workbook(); ws = wb.active; ws.title = f'שיעור {LESSON}'
    ws.sheet_view.rightToLeft = True
    for k, dim in WB0['שיעור 1'].column_dimensions.items(): ws.column_dimensions[k].width = dim.width
    plan = [(1, 1, 4)] + [block_rows(k) for k in HW['items']]
    r_out, mapping = 1, []
    for c, a, b in plan:
        ws0 = WB0[f'שיעור {c}']; dr = r_out - a
        for r in range(a, b):
            if ws0.row_dimensions[r].height: ws.row_dimensions[r + dr].height = ws0.row_dimensions[r].height
            for x in ws0[r]:
                if x.value is None and not x.has_style: continue
                n = ws.cell(r + dr, x.column)
                v = x.value
                if isinstance(v, str) and v.startswith('='):
                    assert '!' not in v, ('a formula reads another sheet', x.coordinate)
                    v = REFS.sub(lambda m: m.group(1) or f'{m.group(2)}{m.group(3)}{m.group(4)}{int(m.group(5)) + dr}', v)
                    mapping.append((c, x.coordinate, n.coordinate))
                n.value = v
                if x.has_style:
                    n.font, n.fill, n.border, n.alignment = copy.copy(x.font), copy.copy(x.fill), copy.copy(x.border), copy.copy(x.alignment)
                    n.number_format, n.protection = x.number_format, copy.copy(x.protection)
        for mr in ws0.merged_cells.ranges:
            if a <= mr.min_row and mr.max_row < b:
                ws.merge_cells(start_row=mr.min_row + dr, start_column=mr.min_col, end_row=mr.max_row + dr, end_column=mr.max_col)
        r_out = b + dr + 1
    ws['A1'] = f'פתרונות תרגילי הבית של שיעור {LESSON}: {HW["topic"]}'
    wb.calculation.fullCalcOnLoad = True
    out = os.path.join(OUT, f'solutions-{LESSON}.xlsx'); wb.save(out)
    # recalculate both with LibreOffice; every formula must give the value it gives in the full workbook
    d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
    for f in (out, SOLX):
        pr = subprocess.Popen(['soffice', '--headless', f'-env:UserInstallation=file://{d}/lo', '--convert-to', 'xlsx:Calc MS Excel 2007 XML', '--outdir', d, f], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try: pr.wait(timeout=900)
        except subprocess.TimeoutExpired: pr.kill(); raise SystemExit('LibreOffice did not finish')
    V = load_workbook(os.path.join(d, os.path.basename(out)), data_only=True)[f'שיעור {LESSON}']
    V0 = load_workbook(os.path.join(d, os.path.basename(SOLX)), data_only=True)
    same = lambda p, q: p == q or (isinstance(p, (int, float)) and isinstance(q, (int, float)) and abs(p - q) < 1e-9 * max(1, abs(p)))
    bad = [(c, a, b, V0[f'שיעור {c}'][a].value, V[b].value) for c, a, b in mapping if not same(V0[f'שיעור {c}'][a].value, V[b].value)]
    errs = [x.coordinate for row in V.iter_rows() for x in row if isinstance(x.value, str) and x.value.startswith('#')]
    print('workbook formulas', len(mapping), 'mismatch', bad[:5], 'errors', errs[:5])
    assert not bad and not errs
    shutil.copy(os.path.join(d, os.path.basename(out)), out)   # recalculated, so values show in Protected View
    shutil.rmtree(d, True)


def label(k):
    b = k.split(':')[0]
    name = f'בחינה {b[2]} (פרק {b[0]})' if 'E' in b else b
    return name, TITLES[b] + (' (סעיפים ' + ', '.join(k.split(':')[1]) + ')' if ':' in k else '')


os.makedirs(OUT, exist_ok=True)
titles = [label(k) for k in HW['items']]
want = [x for k in HW['items'] for x in [k.split(':')[0]]]
for kind, f, name in (('ex', EXF, 'exercises'), ('sol', SOLF, 'solutions')):
    src = fitz.open(f)
    doc = compose(src, kind, [0, front_page(kind, titles), 3])
    doc.save(os.path.join(OUT, f'{name}-{LESSON}.pdf'), garbage=4, deflate=True)
    # every item in the extract, in order, and nothing else: the headers read back from the new PDF (ch 0: any chapter)
    got = [a[0] for a in anchors(doc, 0, 3, len(doc) - 1) if a[0] != 'intro' and not a[0].startswith('S')]
    exp = [k if 'E' not in k else k[1:] for k in want]
    print(name, 'pages', len(doc), 'items', len(got))
    assert got == exp, (got, exp)
build_xlsx()
