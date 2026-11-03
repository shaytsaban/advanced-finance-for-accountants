# The lesson's Excel appendix: one workbook, two sheets. "ללא פתרון": every question of the deck, one under the other, with its
# full text and an empty table. "עם פתרון": the same layout with the data and live formulas. Built from the deck's sheet specs.
# Run: python3 build_appendix.py 1  ->  ../materials/lesson-1-appendix.xlsx  (recalculated and checked with LibreOffice)
import os, re, shutil, subprocess, sys, tempfile
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
R = lambda f: open(os.path.join(H, f), encoding='utf8').read()
MODE = 'pdf'
LESSON = int(sys.argv[1]) if len(sys.argv) > 1 else 1
exec(R('content_a.py'))
NAVY, YEL, GRN = '1B2D55', 'FFF4C2', 'DDF5E6'
thin = Side(style='thin', color='D9D2C3'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
REFS = re.compile(r'("[^"]*")|(\$?)([A-Z]{1,2})(\$?)(\d+)(?![\d(A-Za-z])')


def moved(f, dr):
    """The formula of a table that moved dr rows down: every reference moves with it, absolute ones too, since the whole table moved."""
    return REFS.sub(lambda m: m.group(1) or f'{m.group(2)}{m.group(3)}{m.group(4)}{int(m.group(5)) + dr}', f)


def xfmt(f):
    m = re.fullmatch(r'(pct|num)(\d)', f or '')
    if not m: return None
    d = int(m.group(2)); z = ('.' + '0' * d) if d else ''
    return ('0' + z + '%') if m.group(1) == 'pct' else ('#,##0' + z)


def layout():
    """Where each question goes: (spec, title row, row offset of its table)."""
    out, r = [], 4
    for s in XSPECS:
        out.append((s, r, r + 2 - s['r0']))
        r += 2 + (s['rows'] - s['r0'] + 1) + 2
    return out


def sheet(ws, solved):
    ws.sheet_view.rightToLeft = True
    widths = {}
    for s in XSPECS:
        for j, px in enumerate(s['widths']): widths[j] = max(widths.get(j, 0), round(px / 7))
    for j, w in widths.items(): ws.column_dimensions[chr(65 + j)].width = max(12, w)
    ws['A1'] = f'{COURSE}, שיעור {LESSON}: נספח Excel ' + ('(עם פתרון)' if solved else '(ללא פתרון)'); ws['A1'].font = Font(name='Arial', size=15, bold=True, color=NAVY)
    ws['A2'] = ('בכל תא ירוק: הנתון מהשאלה או הנוסחה. שנו נתון, והתוצאות יתעדכנו.' if solved else 'בכל שאלה: הזינו בתאים הצהובים את נתוני השאלה, ואחר כך את הנוסחאות. לבדיקה: הגיליון ״עם פתרון״.')
    ws['A2'].font = Font(name='Arial', size=11, italic=True, color='5D6A86')
    for s, tr, dr in layout():
        ws.cell(tr, 1, s['title']).font = Font(name='Arial', size=13, bold=True, color=NAVY)
        q = ws.cell(tr + 1, 1, s['qtext']); q.font = Font(name='Arial', size=11); q.alignment = Alignment(wrap_text=True, vertical='top', horizontal='right')
        ws.merge_cells(start_row=tr + 1, start_column=1, end_row=tr + 1, end_column=max(5, s['cols']))
        ws.row_dimensions[tr + 1].height = 15 * (1 + len(s['qtext']) // 95)
        for a, v in s['data'].items():
            m = re.match(r'([A-Z]+)(\d+)', a); r = int(m.group(2))
            if r < s['r0']: continue
            c = ws[f'{m.group(1)}{r + dr}']; c.value = v; c.font = Font(name='Arial', size=11, bold=True)
            if r in s['head']:
                c.fill = PatternFill('solid', fgColor=NAVY); c.font = Font(name='Arial', size=11, bold=True, color='FFFFFF'); c.alignment = Alignment(horizontal='center', wrap_text=True); c.border = BOX
        for a, f in s['sol'].items():
            m = re.match(r'([A-Z]+)(\d+)', a); c = ws[f'{m.group(1)}{int(m.group(2)) + dr}']
            c.fill = PatternFill('solid', fgColor=GRN if solved else YEL); c.border = BOX; c.alignment = Alignment(horizontal='center'); c.font = Font(name='Arial', size=11)
            c.number_format = xfmt(s['fmt'].get(a)) or '#,##0.00'
            if solved:
                if f.startswith('='): c.value = moved(f, dr)
                elif f.endswith('%'): c.value = float(f[:-1]) / 100
                else: c.value = float(f) if re.fullmatch(r'-?\d+(\.\d+)?', f) else f


wb = Workbook(); w1 = wb.active; w1.title = 'ללא פתרון'; sheet(w1, False)
w2 = wb.create_sheet('עם פתרון'); sheet(w2, True)
wb.calculation.fullCalcOnLoad = True
OUT = os.path.abspath(os.path.join(H, '..', 'materials', f'lesson-{LESSON}-appendix.xlsx'))
wb.save(OUT)
d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
pr = subprocess.Popen(['soffice', '--headless', f'-env:UserInstallation=file://{d}/lo', '--convert-to', 'xlsx:Calc MS Excel 2007 XML', '--outdir', d, OUT], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    pr.wait(timeout=900)
except subprocess.TimeoutExpired:
    pr.kill(); shutil.rmtree(d, True); raise SystemExit('LibreOffice did not finish')
rec = os.path.join(d, os.path.basename(OUT))
V = load_workbook(rec, data_only=True)['עם פתרון']; E = load_workbook(rec)['ללא פתרון']
bad, n, worst = [], 0, 0.0
for s, tr, dr in layout():
    for a in s['sol']:
        m = re.match(r'([A-Z]+)(\d+)', a); x = f'{m.group(1)}{int(m.group(2)) + dr}'; n += 1
        lo, py = V[x].value, s['vals'][a]
        if E[x].value is not None: bad.append((s['sid'], a, 'leaked'))
        if not isinstance(lo, (int, float)) or not isinstance(py, (int, float)): bad.append((s['sid'], a, lo, py)); continue
        rel = abs(lo - py) / max(1, abs(py)); worst = max(worst, rel)
        if rel > 1e-9: bad.append((s['sid'], a, lo, py))
print('questions', len(XSPECS), 'cells', n, 'largest relative gap', f'{worst:.1e}', 'problems', bad[:8])
assert not bad
shutil.copy(rec, OUT)   # the recalculated copy, so values show in Protected View too
shutil.rmtree(d, True)
print(os.path.basename(OUT), os.path.getsize(OUT))
