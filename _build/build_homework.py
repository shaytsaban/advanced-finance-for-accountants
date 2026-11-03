# Each lesson's homework: the exercises of the exercise file that match what was actually taught in that lesson.
# The chapters of the file do not follow the meetings one to one (lesson 1 ended before amortizing bonds), so the
# exercises are cut out one by one: from the exercise file, from the solutions booklet, and the blocks of the solutions workbook.
# Run: python3 build_homework.py 1  ->  ../lectures/lecture-1/exercises-1.pdf, solutions-1.pdf, solutions-1.xlsx
import copy, os, re, shutil, subprocess, sys, tempfile
import fitz
from openpyxl import Workbook, load_workbook
H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(H, '..'))
LESSON = int(sys.argv[1]) if len(sys.argv) > 1 else 1
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
FONTS = os.path.join(ROOT, '..', 'iit-build', 'fonts')

# what was taught (Shay, 2026-11-03): lesson 1 reached the amortizing bond slide; everything from there moved to lesson 2.
# Value between payment dates (1.12, 1.14 to 1.16, section d of exam 1, exam 2) waits for the lesson that teaches it.
HW = {
 1: dict(items=['1.1', '1.2', '1.4', '1.5', '1.6', '1.8', '1.9', '1.17', '1.18'],
         topic='אג״ח עם קופון קבוע: שווי בטבלה וב-NPV או ב-PV, פרמיה ונכיון, קופון חצי שנתי ורבעוני והמרת ריבית'),
 2: dict(items=['1.3', '1.7', '1.10', '1.11', '1.13', 'E1:אבג'],
         topic='אג״ח לשיעורין: לוח סילוקין, קופון על היתרה ושווי ב-NPV'),
}[LESSON]
LATER = 'תרגילים 1.12, 1.14 עד 1.16, סעיף ד בתרגיל בסגנון בחינה 1 ותרגיל בסגנון בחינה 2 עוסקים בשווי בין מועדי תשלום. הם יצורפו לשיעור שבו נלמד הנושא.'
EXF, SOLF, SOLX = (os.path.join(ROOT, 'materials', f) for f in ('afm-exercises.pdf', 'afm-solutions.pdf', 'afm-solutions.xlsx'))
OUT = os.path.join(ROOT, 'lectures', f'lecture-{LESSON}')
TOP, BOT = 72, 772          # the body of a page, between the running header and the page number


def anchors(doc, p0, p1):
    """Where each exercise, exam and exam section starts: [(key, page, y)], in reading order, pages p0..p1 (0-based, inclusive)."""
    out = []
    for i in range(p0, p1 + 1):
        for b in sorted((b for b in doc[i].get_text('dict')['blocks'] if 'lines' in b), key=lambda b: b['bbox'][1]):
            t = ' '.join(s['text'] for l in b['lines'] for s in l['spans'])
            y = b['bbox'][1] - 7
            m = re.match(r'\s*תרגיל\s*1\.(\d+)', t)
            if m and len(t) < 110:
                out.append((f'1.{m.group(1)}', i, y)); continue
            m = re.search(r'(\d)\s*תרגיל בסגנון בחינה', t)
            if m and 'לתוכן העניינים' in t:
                out.append((f'E{m.group(1)}', i, y)); continue
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
    """The regions of one item: from its anchor to the next anchor, across pages. key 'E1:אבג' keeps those sections only."""
    if ':' in key:
        k, keep = key.split(':')
    else:
        k, keep = key, None
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


def compose(src, A, end_page, front, strip_page):
    """A new PDF: the front pages, then every item's regions flowed onto pages, under the running header of the source."""
    doc = fitz.open()
    for f in front:
        if isinstance(f, int): doc.insert_pdf(src, from_page=f, to_page=f)
        else: doc.insert_pdf(f)
    W, Hh = src[0].rect.width, src[0].rect.height
    page, y = None, None
    for key in HW['items']:
        for (p, a, b) in pieces(src, A, key, end_page):
            h = b - a
            if page is None or y + h > BOT:
                page = doc.new_page(width=W, height=Hh)
                page.show_pdf_page(fitz.Rect(0, 40, W, TOP), src, strip_page, clip=fitz.Rect(0, 40, W, TOP))
                y = TOP + 4
            page.show_pdf_page(fitz.Rect(0, y, W, y + h), src, p, clip=fitz.Rect(0, a, W, b))
            y += h + 6
        y += 6
    return doc


def front_page(kind, titles):
    """One page in the house style: which exercises, from which chapter, and what waits for a later lesson."""
    lis = ''.join(f'<li><b dir="ltr">{k}</b> {t}</li>' for k, t in titles)
    html = f'''<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><style>
@font-face{{font-family:"David";src:url("david.ttf");font-weight:400}}@font-face{{font-family:"David";src:url("davidbd.ttf");font-weight:700}}
@page{{size:A4;margin:22mm 22mm}}body{{font-family:"David";font-size:14pt;line-height:1.45;color:#16213a}}
h1{{font-size:24pt;color:#1b2d55;margin:0 0 2mm}}h2{{font-size:15pt;color:#c4421f;margin:0 0 8mm;font-weight:700}}
ol{{padding-right:7mm;margin:4mm 0 8mm}}li{{margin:1.5mm 0}}li b{{display:inline-block;min-width:16mm;unicode-bidi:isolate}}
.n{{background:#f4f6fb;border-right:4px solid #1b2d55;padding:4mm 6mm;font-size:12.5pt}}</style></head><body>
<h1>שיעור {LESSON}: {'תרגילי בית' if kind == 'ex' else 'פתרונות תרגילי הבית'}</h1>
<h2>{HW['topic']}</h2>
<p>{'התרגילים מתוך פרק 1 בקובץ התרגילים שמתאימים למה שנלמד בשיעור, באותו מספור כמו בקובץ המלא:' if kind == 'ex' else 'הפתרונות מתוך פרק 1 בחוברת הפתרונות, לתרגילי הבית של השיעור, באותו מספור. פותחים רק אחרי שפותרים.'}</p>
<ol>{lis}</ol>
<div class="n">{LATER}</div></body></html>'''
    d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
    for f in ('david.ttf', 'davidbd.ttf'): shutil.copy(os.path.join(FONTS, f), d)
    open(os.path.join(d, 'f.html'), 'w', encoding='utf8').write(html)
    out = os.path.join(d, 'f.pdf')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/p', '--no-pdf-header-footer', '--virtual-time-budget=5000', f'--print-to-pdf={out}', 'file://' + os.path.join(d, 'f.html')], capture_output=True, timeout=180)
    f = fitz.open(out); assert len(f) == 1, 'the front page must fit one page'
    return f


# ---------------------------------------------------------------- the solutions workbook: one sheet, the same blocks
REFS = re.compile(r'("[^"]*")|(\$?)([A-Z]{1,2})(\$?)(\d+)(?![\d(A-Za-z])')
ws0 = load_workbook(SOLX)['שיעור 1']
starts = {}
for r in range(1, ws0.max_row + 1):
    v = ws0.cell(r, 1).value
    if isinstance(v, str):
        m = re.match(r'תרגיל (1\.\d+)\s+\|', v) or re.match(r'תרגיל בסגנון בחינה (\d)\s+\|', v)
        if m: starts[(m.group(1) if '.' in m.group(1) else 'E' + m.group(1))] = r
order = sorted(starts, key=starts.get)
TITLES = {k: re.split(r'\s+\|\s+', ws0.cell(starts[k], 1).value, maxsplit=1)[1] for k in order}


def block_rows(key):
    k, keep = (key.split(':') + [None])[:2]
    a = starts[k]; i = order.index(k)
    b = starts[order[i + 1]] if i + 1 < len(order) else ws0.max_row + 1
    if keep:
        for r in range(a, b):
            v = ws0.cell(r, 1).value
            if isinstance(v, str) and re.fullmatch(r'סעיף ([אבגד])', v.strip()) and v.strip()[-1] not in keep:
                b = r; break
    while b - 1 > a and all(c.value is None for c in ws0[b - 1]): b -= 1
    return a, b


def build_xlsx():
    wb = Workbook(); ws = wb.active; ws.title = f'שיעור {LESSON}'
    ws.sheet_view.rightToLeft = True
    for k, dim in ws0.column_dimensions.items(): ws.column_dimensions[k].width = dim.width
    plan = [(1, 4)] + [block_rows(k) for k in HW['items']]
    r_out, mapping = 1, []
    for a, b in plan:
        dr = r_out - a
        for r in range(a, b):
            if ws0.row_dimensions[r].height: ws.row_dimensions[r + dr].height = ws0.row_dimensions[r].height
            for c in ws0[r]:
                if c.value is None and not c.has_style: continue
                n = ws.cell(r + dr, c.column)
                v = c.value
                if isinstance(v, str) and v.startswith('='):
                    v = REFS.sub(lambda m: m.group(1) or f'{m.group(2)}{m.group(3)}{m.group(4)}{int(m.group(5)) + dr}', v)
                    mapping.append((c.coordinate, n.coordinate))
                n.value = v
                if c.has_style:
                    n.font, n.fill, n.border, n.alignment = copy.copy(c.font), copy.copy(c.fill), copy.copy(c.border), copy.copy(c.alignment)
                    n.number_format, n.protection = c.number_format, copy.copy(c.protection)
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
    V0 = load_workbook(os.path.join(d, os.path.basename(SOLX)), data_only=True)['שיעור 1']
    bad = [(a, b, V0[a].value, V[b].value) for a, b in mapping if V0[a].value != V[b].value and not (isinstance(V[b].value, float) and isinstance(V0[a].value, float) and abs(V[b].value - V0[a].value) < 1e-9 * max(1, abs(V0[a].value)))]
    errs = [c.coordinate for row in V.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith('#')]
    print('workbook formulas', len(mapping), 'mismatch', bad[:5], 'errors', errs[:5])
    assert not bad and not errs
    shutil.copy(os.path.join(d, os.path.basename(out)), out)   # recalculated, so values show in Protected View
    shutil.rmtree(d, True)


os.makedirs(OUT, exist_ok=True)
titles = [(k.split(':')[0].replace('E', 'בחינה ') if k.startswith('E') else k, TITLES[k.split(':')[0]] + (' (סעיפים ' + ', '.join(k.split(':')[1]) + ')' if ':' in k else '')) for k in HW['items']]
src = fitz.open(EXF); A = anchors(src, 4, 16)
need = {k.split(':')[0] for k in HW['items']}
assert need <= {a[0] for a in A}, ('exercise file', need - {a[0] for a in A})
ex = compose(src, A, 17, [0, front_page('ex', titles), 3], 5)
ex.save(os.path.join(OUT, f'exercises-{LESSON}.pdf'), garbage=4, deflate=True)
sol = fitz.open(SOLF); B = anchors(sol, 4, 50)
assert need <= {a[0] for a in B}, ('solutions', need - {a[0] for a in B})
so = compose(sol, B, 51, [0, front_page('sol', titles), 3], 5)
so.save(os.path.join(OUT, f'solutions-{LESSON}.pdf'), garbage=4, deflate=True)
# every exercise in the extract, and nothing else: its headers, read back from the new PDF
for name, d in (('exercises', ex), ('solutions', so)):
    got = [a[0] for a in anchors(d, 3, len(d) - 1) if a[0] != 'intro']
    want = [x for k in HW['items'] for x in ([k] if ':' not in k else [k.split(':')[0]] + ['S' + c for c in k.split(':')[1]])]
    print(name, 'pages', len(d), got)
    assert got == want, (got, want)
build_xlsx()
