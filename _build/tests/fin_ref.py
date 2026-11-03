# Reference test of the sheet engine's functions: LibreOffice recalculates the same formulas, and the engine must agree.
# Run: python3 tests/fin_ref.py   (needs soffice and node)
import json, os, shutil, subprocess, tempfile
from openpyxl import Workbook, load_workbook
H = os.path.dirname(os.path.abspath(__file__))
DATA = {'A1': 0.07, 'A2': 6, 'A3': 5, 'A4': 100, 'A5': -90.4669206804718, 'A6': 0.05, 'A7': 0, 'A8': -0.02, 'A9': 1, 'A10': 0.1025,
        'C1': -1000, 'C2': 300, 'C3': 400, 'C4': None, 'C5': 500, 'C6': 'טקסט', 'C7': 200,
        'D1': -95, 'D2': 6, 'D3': 6, 'D4': 106,
        'E1': -10000, 'E2': 2750, 'E3': 4250, 'E4': 3250, 'E5': 2750}
CASES = [
 '=PV(A1,A2,A3,A4)', '=PV(A1,A2,A3,A4,1)', '=PV(A1,A2,A3)', '=PV(A1,A2,,A4)', '=-PV(A1,A2,A3,A4)', '=PV(A7,A2,A3,A4)', '=PV(0,A2,A3,A4,1)', '=PV(A8,A2,A3,A4)',
 '=PV((1+A10)^(1/2)-1,16,3,100)', '=PV(5%,10,-100)', '=PV(0.12/4,16,15,1000)', '=PV(A1,0.5,A3,A4)',
 '=FV(A6,10,-100)', '=FV(A6,10,-100,0,1)', '=FV(0,10,-100,-50)', '=FV(A6,4/12,0,-A4)', '=FV(A8,3,10,100,1)', '=FV(A1,A2,,A5)',
 '=PMT(A6,10,1000)', '=PMT(A6,10,1000,0,1)', '=PMT(0,10,1000)', '=PMT(A6/12,360,-500000,0)', '=PMT(A1,A2,-100,50,1)',
 '=NPER(A6,-100,1000)', '=NPER(A6,-100,1000,0,1)', '=NPER(0,-100,1000)', '=NPER(A1,A3,A5,A4)', '=NPER(0.01,-50,-1000,10000)',
 '=RATE(A2,A3,A5,A4)', '=RATE(A2,A3,A5,A4,1)', '=RATE(10,-100,800)', '=RATE(10,0,-50,100)', '=RATE(36,-300,9000,0,0,0.01)', '=RATE(5,-100,500)', '=RATE(12,-1000,10000,0,1)', '=RATE(4,0,D1,100)',
 '=NPV(A1,A3,A3,A3,A3,A3,A3+A4)', '=NPV(A6,C2:C7)', '=NPV(A6,C1:C7)+0', '=NPV(0,C2:C5)', '=NPV(A8,C2,C3,C5)', '=NPV(A1,D2:D4)',
 '=IRR(C1:C7)', '=IRR(E1:E5)', '=IRR(E1:E5,0.3)', '=IRR(D1:D4)', '=(1+IRR(D1:D4))^2-1',
 '=XNPV(0.1,E1:E5,F1:F5)', '=XIRR(E1:E5,F1:F5)', '=XNPV(A6,E1:E3,F1:F3)',
 '=ROUND(A5,2)', '=ROUND(2.345,2)', '=ROUND(-2.345,2)', '=ROUND(1234.5,-2)', '=ROUND(0.125,2)',
 '=POWER(1.1025,0.5)-1', '=EFFECT(0.1,2)', '=NOMINAL(0.1025,2)', '=SQRT(A4)', '=LN(A9+A6)', '=EXP(A6)', '=SUMPRODUCT(C2:C3,E2:E3)', '=DATE(2026,11,3)', '=DATE(2027,2,29)',
 '=SUM(C1:C7)', '=AVERAGE(D2:D4)', '=MAX(E1:E5)-MIN(E1:E5)', '=(1+A1)^(1/12)-1', '=A4*A6/2', '=-A5*(1+A1)^(3/12)'
]
DATES = {'F1': (2026, 1, 1), 'F2': (2026, 7, 15), 'F3': (2027, 3, 1), 'F4': (2027, 12, 31), 'F5': (2029, 1, 1)}


def main():
    wb = Workbook(); ws = wb.active
    for a, v in DATA.items():
        if v is not None: ws[a] = v
    for a, (y, m, d) in DATES.items(): ws[a] = f'=DATE({y},{m},{d})'
    for i, f in enumerate(CASES): ws[f'H{i + 1}'] = f
    d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
    try:
        src = os.path.join(d, 'ref.xlsx'); wb.save(src)
        out = os.path.join(d, 'out'); os.makedirs(out)
        subprocess.run(['soffice', '--headless', f'-env:UserInstallation=file://{d}/lo', '--convert-to', 'xlsx:Calc MS Excel 2007 XML', '--outdir', out, src], capture_output=True, timeout=180)
        V = load_workbook(os.path.join(out, 'ref.xlsx'), data_only=True).active
        import datetime as _dt
        lo = [V[f'H{i + 1}'].value for i in range(len(CASES))]
        lo = [(x - _dt.datetime(1899, 12, 30)).days if isinstance(x, _dt.datetime) else x for x in lo]   # dates as Excel serials
        cells = {a: ('' if v is None else str(v)) for a, v in DATA.items()}
        cells.update({a: f'=DATE({y},{m},{dd})' for a, (y, m, dd) in DATES.items()})
        cells.update({f'H{i + 1}': f for i, f in enumerate(CASES)})
        js = ("const fs=require('fs');eval(fs.readFileSync(process.argv[1],'utf8')+';global.XL=XL;');"
              "const c=JSON.parse(process.argv[2]),S=new XL.Sheet(80,10);for(const k in c)S.set(k,c[k]);S.recalc();"
              "const o=[];for(let i=1;i<=+process.argv[3];i++){const v=S.val['H'+i];o.push(v&&v.err?v.err:v);}console.log(JSON.stringify(o));")
        eng = json.loads(subprocess.run(['node', '-e', js, os.path.join(H, '..', 'xl.js'), json.dumps(cells), str(len(CASES))], capture_output=True, text=True, check=True).stdout)
    finally:
        shutil.rmtree(d, True)
    bad = 0; worst = 0
    for f, a, b in zip(CASES, lo, eng):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            rel = abs(a - b) / max(1, abs(a)); worst = max(worst, rel); ok = rel < 1e-9
        else:
            ok = (a == b) or (isinstance(a, str) and a.startswith('#') and isinstance(b, str) and b.startswith('#'))
        if not ok: bad += 1
        print(('ok  ' if ok else 'BAD ') + f'{f:38} LibreOffice {a!r:28} engine {b!r}')
    print(f'{len(CASES)} formulas, {bad} disagree, largest relative gap {worst:.2e}')
    return bad


if __name__ == '__main__':
    raise SystemExit(main())
