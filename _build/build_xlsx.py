# Practice workbook and solutions workbook, built from the same sheet specs as the deck (same cell addresses).
# Run: python3 build_xlsx.py 1  ->  ../materials/practice-1.xlsx and practice-1-solutions.xlsx
# practice: yellow cells are empty. solutions: the same cells hold live formulas. Every answer is checked three ways:
# the Python evaluator (fin.py), the deck's own engine (xl.js in node) and a LibreOffice recalculation.
import json, os, re, shutil, subprocess, sys, tempfile
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import ScatterChart, Reference, Series
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
R = lambda f: open(os.path.join(H, f), encoding='utf8').read()
MODE = 'pdf'
LESSON = int(sys.argv[1]) if len(sys.argv) > 1 else 1
exec(R('content_a.py'))
OUT = os.path.join(H, '..', 'materials')
NAVY, YEL, GRN, GIV = '1B2D55', 'FFF4C2', 'DDF5E6', 'EEF2FF'
thin = Side(style='thin', color='D9D2C3'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
NOTE = 'הנתונים בגיליון לקוחים מהשאלות של הקורס ואינם נתוני שוק.'


def xfmt(f):
    m = re.fullmatch(r'(pct|num)(\d)', f or '')
    if not m: return None
    d = int(m.group(2)); z = ('.' + '0' * d) if d else ''
    return ('0' + z + '%') if m.group(1) == 'pct' else ('#,##0' + z)


def sname(sp):
    return re.split(r'[:׃]', sp['title'])[0].strip()[:31]


def build(path, solved):
    wb = Workbook(); w0 = wb.active; w0.title = 'הוראות'; w0.sheet_view.rightToLeft = True; w0.column_dimensions['A'].width = 100
    lines = [f'{COURSE}, שיעור {LESSON}: ' + ('קובץ פתרונות' if solved else 'קובץ תרגול'), f'{INST} · ד״ר שי צבאן · {SEM}', '',
             ('התאים הירוקים מכילים נוסחאות חיות. שנו נתון בתא כחול, והתוצאות יתעדכנו.' if solved else 'התאים הצהובים ריקים: כתבו בהם נוסחאות. התאים הכחולים הם הנתונים.'),
             'כל גיליון כאן הוא גיליון מהמצגת, באותן כתובות תאים. כתבו נוסחאות עם הפניות לתאים, ולא מספרים. קבעו תאים עם $ לפני גרירה.',
             ('השוו לקובץ שלכם רק אחרי שפתרתם, נוסחה מול נוסחה (Ctrl+`).' if solved else 'רק אחרי שפתרתם: משווים לקובץ הפתרונות.'),
             'כל נוסחה נכונה מתקבלת. בקובץ הפתרונות מופיעה דרך אחת בלבד.', NOTE, '', 'הגיליונות:'] + [sname(s) + ': ' + s['title'].split(':', 1)[-1].strip() for s in XSPECS]
    for i, t in enumerate(lines, 1):
        c = w0.cell(i, 1, t); c.alignment = Alignment(horizontal='right', wrap_text=True); c.font = Font(name='Arial', size=16 if i == 1 else 12, bold=i == 1, color=NAVY if i == 1 else '16213A')
    for s in XSPECS:
        ws = wb.create_sheet(sname(s)); ws.sheet_view.rightToLeft = True
        for j, px in enumerate(s['widths']): ws.column_dimensions[chr(65 + j)].width = max(8, round(px / 7))
        # the title and task sit above the table when there is room (as in the lesson file), else beside it
        if s['r0'] >= 4:
            tc, tr = 'A', 1
        else:
            tc, tr = chr(65 + s['cols'] + 1), 1
            ws.column_dimensions[tc].width = 70
        ws[f'{tc}{tr}'] = s['title']; ws[f'{tc}{tr}'].font = Font(name='Arial', size=14, bold=True, color=NAVY)
        ws[f'{tc}{tr + 1}'] = s['task']; ws[f'{tc}{tr + 1}'].font = Font(name='Arial', size=11)
        if tc != 'A': ws[f'{tc}{tr + 1}'].alignment = Alignment(wrap_text=True, vertical='top', horizontal='right')
        for a, v in s['data'].items():
            c = ws[a]; r = int(re.sub('[A-Z]', '', a)); c.value = v; c.font = Font(name='Arial', size=12)
            if r in s['head']:
                c.fill = PatternFill('solid', fgColor=NAVY); c.font = Font(name='Arial', size=12, bold=True, color='FFFFFF'); c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); c.border = BOX
            elif isinstance(v, str) and not v.startswith('='):
                c.font = Font(name='Arial', size=12, bold=True); c.alignment = Alignment(horizontal='right')
            else:
                c.fill = PatternFill('solid', fgColor=GIV); c.border = BOX; c.alignment = Alignment(horizontal='center')
            if xfmt(s['fmt'].get(a)): c.number_format = xfmt(s['fmt'][a])
        for a, f in s['sol'].items():
            c = ws[a]; c.fill = PatternFill('solid', fgColor=GRN if solved else YEL); c.border = BOX; c.alignment = Alignment(horizontal='center'); c.font = Font(name='Arial', size=12)
            c.number_format = xfmt(s['fmt'].get(a)) or '#,##0.00'
            if solved: c.value = f
        if solved and s['sid'] == 'x-curve':
            ch = ScatterChart(); ch.style = 13; ch.title = 'מחיר האג״ח מול התשואה לפדיון'; ch.height = 9; ch.width = 15
            ch.x_axis.title = 'תשואה לפדיון (%)'; ch.y_axis.title = 'מחיר (ש״ח)'; ch.x_axis.delete = False; ch.y_axis.delete = False
            se = Series(Reference(ws, min_col=2, min_row=4, max_row=16), Reference(ws, min_col=1, min_row=5, max_row=16), title_from_data=True); se.marker.symbol = 'circle'; ch.series.append(se)
            ws.add_chart(ch, 'D5')
        ws[f'{tc}{tr + 2}'] = NOTE; ws[f'{tc}{tr + 2}'].font = Font(name='Arial', size=10, italic=True, color='5D6A86')
    wb.calculation.fullCalcOnLoad = True
    wb.save(path)


def engine_values():
    """The deck's engine on every spec: data plus solution, recalculated in node."""
    js = ("const fs=require('fs');eval(fs.readFileSync(process.argv[1],'utf8')+';global.XL=XL;');const P=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));"
          "const out=P.map(p=>{const S=new XL.Sheet(p.rows,p.cols);for(const k in p.data)S.set(k,String(p.data[k]));for(const k in p.sol)S.set(k,p.sol[k]);S.recalc();const o={};for(const k in p.sol){const v=S.val[k];o[k]=v&&v.err?v.err:v;}return o;});console.log(JSON.stringify(out));")
    d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
    try:
        f = os.path.join(d, 'p.json'); json.dump([dict(rows=s['rows'], cols=s['cols'], data=s['data'], sol=s['sol']) for s in XSPECS], open(f, 'w'), ensure_ascii=False)
        return json.loads(subprocess.run(['node', '-e', js, os.path.join(H, 'xl.js'), f], capture_output=True, text=True, check=True).stdout)
    finally:
        shutil.rmtree(d, True)


os.makedirs(OUT, exist_ok=True)
pr, so = f'practice-{LESSON}.xlsx', f'practice-{LESSON}-solutions.xlsx'
build(os.path.join(OUT, pr), False)
raw = os.path.join(OUT, so)
build(raw, True)
d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
pr_ = subprocess.Popen(['soffice', '--headless', f'-env:UserInstallation=file://{d}/lo', '--convert-to', 'xlsx:Calc MS Excel 2007 XML', '--outdir', d, raw], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    pr_.wait(timeout=900)
except subprocess.TimeoutExpired:
    pr_.kill(); shutil.rmtree(d, True); raise SystemExit('LibreOffice did not finish')
rec = os.path.join(d, so)
V = load_workbook(rec, data_only=True); FM = load_workbook(rec)
EV = engine_values()
errs, nform, worst = [], 0, 0.0
for s, ev in zip(XSPECS, EV):
    n = sname(s)
    for a in s['sol']:
        nform += 1
        lo, py, js = V[n][a].value, s['vals'][a], ev[a]
        if not str(FM[n][a].value).startswith('='): errs.append((n, a, 'lost formula'))
        if not isinstance(lo, (int, float)) or isinstance(lo, bool): errs.append((n, a, 'LibreOffice', lo)); continue
        for who, x in (('python', py), ('engine', js)):
            if not isinstance(x, (int, float)): errs.append((n, a, who, x)); continue
            rel = abs(x - lo) / max(1, abs(lo)); worst = max(worst, rel)
            if rel > 1e-9: errs.append((n, a, who, x, lo))
print('sheets', len(XSPECS), 'formulas', nform, 'largest relative gap (python, engine vs LibreOffice)', f'{worst:.1e}', 'errors', errs[:10])
print('rtl', all(FM[sname(s)].sheet_view.rightToLeft for s in XSPECS), '| charts', sum(len(FM[sname(s)]._charts) for s in XSPECS))
KEY = {'q-1': ('D23', 90.4669206805), 'q-2': ('D58', 78.3244608797), 'q-3': ('D82', 209.9721399946), 'q-4': ('D105', 413.0914195154), 'x-e1': ('B7', 259626.7326879), 'x-e7': ('B9', 6.3614868858)}
for s in XSPECS:
    if s['sid'] in KEY:
        a, e = KEY[s['sid']]; v = V[sname(s)][a].value
        assert abs(v - e) < 1e-6, (s['sid'], a, v, e)
print('key answers match the lesson file and the exercise file:', len(KEY))
assert not errs
shutil.copy(rec, raw)   # ship the recalculated copy, so values also show in Protected View
shutil.rmtree(d, True)
P = load_workbook(os.path.join(OUT, pr))
leak = sum(1 for s in XSPECS for a in s['sol'] if P[sname(s)][a].value is not None)
print(pr, os.path.getsize(os.path.join(OUT, pr)), so, os.path.getsize(raw), 'answers leaked into practice:', leak)
assert leak == 0
