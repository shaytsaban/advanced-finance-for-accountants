# Lesson content, shared by the deck and the summary. Executed with MODE = 'deck' or 'pdf'.
from lib import *
import json, html as _html

COURSE = 'מימון מתקדם לחשבונאים'
INST = 'המכללה למנהל · מסלול חשבונאות'
SEM = 'סמסטר א׳ תשפ״ז'
LESSON = globals().get('LESSON', 1)
TOTAL_PARTS = {1: 4, 2: 3}[LESSON]
# per lesson: deck title, subtitle, chips, cover line and the next meeting. The first meeting date is not in the source files.
# Shay, 2026-11-03: lesson 1 ended before amortizing bonds. From that slide on, the content is lesson 2.
LMETA = {
 1: dict(date='3.11.2026', h1=('אג״ח שקליות:', 'שווי, ריבית נקובה ותשואה לפדיון'), title='אג״ח שקליות',
         sub='מה קונים כשקונים אג״ח, איך מחשבים את שוויה, ומה משתנה כשהקופון חצי שנתי או רבעוני.', chip='שבעה תרגילים לעבודה עצמית',
         cover='ערך נקוב, ריבית נקובה, שיעור תשואה לפדיון, היוון, NPV ו-PV, פרמיה ונכיון, קופון חצי שנתי ורבעוני והמרת ריבית, ושבעה תרגילים לעבודה עצמית.',
         next_h='אג״ח לשיעורין', next_t='אג״ח שהקרן שלה מוחזרת בחלקים: יתרת ערך נקוב, קופון על היתרה ולוח סילוקין מלא. לפני המפגש: תרגילי הבית של שיעור 1.'),
 2: dict(date='10.11.2026', h1=('אג״ח לשיעורין', 'ושווי לאורך חיי האג״ח'), title='אג״ח לשיעורין ושווי בין מועדים',
         sub='כשהקרן מוחזרת בחלקים: לוח סילוקין וקופון על היתרה. ושווי האג״ח מיד אחרי תשלום, רגע לפני תשלום ובין שני מועדי תשלום.', chip='תזכורת לשיעור 1, ושאלות 1 עד 4 מקובץ שיעור 2',
         cover='אג״ח לשיעורין, יתרת ערך נקוב, לוח סילוקין, קופון על היתרה, שווי מיד אחרי תשלום ורגע לפניו, שווי בין מועדי תשלום, תרגיל בסגנון בחינה ותרגול על כל נושאי האג״ח השקליות.',
         next_h='חילוץ תשואה לפדיון', next_t='כשהמחיר ידוע והתשואה לא: הפונקציות IRR ו-RATE, גם באג״ח לשיעורין ובין מועדי תשלום. לפני המפגש: תרגילי הבית של שיעור 2.')}[LESSON]
XSPECS = []        # every live sheet, in deck order: the practice workbooks are built from these
SL = []            # every slide, in order
CUR = [None]       # current part number
NACT = [0]


def S(sid, title, h, body, kick=None, cls='', kind='slide'):
    SL.append(dict(id=sid, title=title, h=h, body=link_terms(body), kick=kick, cls=cls, kind=kind, part=CUR[0]))


def ST(n, html, tag='div', cls=''):
    return f'<{tag} class="st {cls}" data-n="{n * 10}">{html}</{tag}>'


def DEF(name, text, demo, n=0, trm=None, cls=''):
    """One definition with its small numeric demonstration."""
    hd = f'[[{trm}|{name}]]' if trm else name
    inner = f'<b class="dn">{TX(hd)}</b><p>{TX(text)}</p><div class="demo"><b>דוגמה:</b> {TX(demo)}</div>'
    return ST(n, inner, cls='card def ' + cls) if n else f'<div class="card def {cls}">{inner}</div>'


def BAND(kind, text, n=0):
    lab = {'dg': 'דגש', 'trap': 'המלכודת', 'note': 'הערה', 'tip': 'טיפ'}.get(kind, '')
    inner = (f'<b>{lab}:</b> ' if lab else '') + TX(text)
    return ST(n, inner, cls='band ' + kind) if n else f'<div class="band {kind}">{inner}</div>'


def TABLE(head, rows, cls=''):
    h = ''.join(f'<th>{TX(x)}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f'<td>{TX(c)}</td>' for c in r) + '</tr>' for r in rows)
    return f'<table class="tbl2 {cls}"><tr>{h}</tr>{b}</table>'


def mc(qid, q, opts, a, why, rot=True):
    # options are written with the right answer first; a fixed rotation per question places it
    r = sum(map(ord, qid)) % len(opts) if rot else 0
    opts = opts[r:] + opts[:r]
    a = (a - r) % len(opts)
    o = ''
    for i, t in enumerate(opts):
        mark = ' correct' if MODE == 'pdf' and i == a else ''
        o += f'<button class="o{mark}" data-i="{i}">{"אבגדה"[i]}. {TX(t)}</button>'
    return f'<div class="mc" data-a="{a}" id="{qid}"><div class="q">{TX(q)}</div>{o}<div class="w"><b>הסבר:</b> {TX(why)}</div></div>'


def MCS(sid, title, h, items):
    S(sid, title, h, f'<div class="mcrow n{len(items)}">' + ''.join(items) + '</div>', kick=f'חלק {CUR[0]} · בדיקת הבנה')


def opener(n, title, q, learn, mins, note=''):
    CUR[0] = n
    SL.append(dict(id=f'p-{n}', title=f'פתיחת חלק {n}: {title}', h=title, kind='opener', part=n, q=q, learn=learn, mins=mins, note=note, cls='', kick=None, body=''))


def calc(cid, title, h, intro, fields, pdfx):
    if MODE == 'pdf':
        S('c-' + cid, title, h, f'<div class="calcp"><b>מחשבון במצגת.</b> {TX(intro)} <b>דוגמה:</b> {TX(pdfx)}</div>', kind='calcp')
        return
    NACT[0] += 1
    fs = ''.join(f'<label class="cf"><span>{TX(f[1])}</span><input data-k="{f[0]}" value="{f[2]}" dir="ltr" inputmode="decimal" autocomplete="off" spellcheck="false"></label>' for f in fields)
    S('c-' + cid, title, h, f'<div class="calc" data-calc="{cid}"><div class="cin"><p class="cint">{TX(intro)}</p><div class="cfs">{fs}</div></div><div class="cout" id="out-{cid}"></div></div>', kick=f'חלק {CUR[0]} · מחשבון')


def _solitems(items, start=1):
    out, n = [], start
    for it in items:
        if it.startswith('=!'):
            out.append(ST(n, M(it[2:]), cls='eq fit').replace('class="st eq fit"', 'class="st eq fit" dir="ltr"'))
        elif it.startswith('='):
            out.append(ST(n, M(it[1:]), cls='eq').replace('class="st eq"', 'class="st eq" dir="ltr"'))
        else:
            out.append(ST(n, TX(it), 'p', 'sp'))
        n += 1
    return ''.join(out), n


def Q(sid, tag, title, stem, sol, ans, note=None, extra=None):
    """A worked question: the question beside its solution, the solution revealed click by click."""
    note = note or []
    head = f'{tag}: {title}'
    stem_html = ''.join(f'<p>{TX(x)}</p>' for x in stem)
    s1, n = _solitems(sol)
    if MODE == 'pdf':
        b = f'<div class="qstem">{stem_html}</div>{extra or ""}<div class="sol">{s1}</div><div class="band ans"><b>תשובה:</b> {TX(ans)}</div>' + ''.join(BAND(a, t) for a, t in note)
        S(sid, head, head, b, kind='q')
        return
    end = ST(n, f'<b>תשובה:</b> {TX(ans)}', cls='band ans') + ''.join(BAND(a, t, n + 1 + i) for i, (a, t) in enumerate(note))
    body = f'<div class="qg"><div class="qr"><div class="card qstem">{stem_html}</div>{extra or ""}</div><div class="solw">{s1}{end}</div></div>'
    S(sid, head, head, body, kick=f'חלק {CUR[0]} · {tag}', cls='qslide')


def CAP(t):
    return f'<p class="cap">{TX(t)}</p>'


def rcard(n, t, d, m, go):
    return f'<button class="rcard" data-go="{go}"><div class="n">{n}</div><b>{t}</b><span>{TX(d)}</span><em>{m}</em></button>'


def XL(f):
    """An Excel formula. ¤ stands for the dollar sign, which the text markup reserves for math."""
    return f'<code class="xl" dir="ltr">{f}</code>'


# ---------------------------------------------------------------- activities
def _cfg(d):
    return _html.escape(json.dumps(d, ensure_ascii=False), quote=True)


def _bar(*btns):
    return '<div class="actbar">' + ''.join(btns) + '</div>'


CHK = '<button class="abtn chk">בדיקה</button>'
NXT = '<button class="abtn ghost nxt" disabled>המשך</button>'
RST = '<button class="abtn ghost rst">איפוס</button>'


def SORTER(aid, title, h, task, options, rows):
    """Each row gets one right answer out of options. rows: (text, answer index, why)."""
    if MODE == 'pdf':
        t = ''.join(f'<tr><td>{TX(a)}</td><td><b>{options[b]}</b></td><td>{TX(c)}</td></tr>' for a, b, c in rows)
        S(aid, title, h, f'<p>{TX(task)}</p><table class="tbl2"><tr><th>מצב</th><th>תשובה</th><th>נימוק</th></tr>{t}</table>')
        return
    NACT[0] += 1
    r = ''
    for a, b, c in rows:
        bs = ''.join(f'<button class="so" data-i="{i}">{o}</button>' for i, o in enumerate(options))
        r += f'<tr class="srow" data-a="{b}" data-w="{_html.escape(TX(c), quote=True)}"><td>{TX(a)}</td><td>{bs}</td></tr>'
    body = (f'<div class="act sorter" id="{aid}-w"><div class="tasktxt"><b>המשימה:</b> {TX(task)}</div><table class="stbl">{r}</table>'
            f'<div class="fbbar">בחרו תשובה בכל שורה.</div><div class="actbar">{RST}<span class="score">0 / {len(rows)}</span></div></div>')
    S(aid, title, h, body, kick=f'חלק {CUR[0]} · פעילות')


def NUMQ(qid, q, ans, tol, unit, why, hint):
    """A checked numeric question, to place inside a slide body."""
    if MODE == 'pdf':
        return f'<div class="calcp"><b>בדיקה עצמית.</b> {TX(q)} <b>תשובה:</b> <span class="n">{f'{ans:,}'.replace('-', '−')}</span> {TX(unit)}. {TX(why)}</div>'
    NACT[0] += 1
    return (f'<div class="act numq" id="{qid}" data-a="{ans}" data-tol="{tol}" data-w="{_html.escape(TX(why), quote=True)}" data-h="{_html.escape(TX(hint), quote=True)}"><div class="q">{TX(q)}</div>'
            f'<div class="numrow"><input dir="ltr" inputmode="decimal" autocomplete="off" spellcheck="false" aria-label="תשובה"><span>{TX(unit)}</span>{CHK}</div><div class="fbbar">הקלידו מספר ולחצו ״בדיקה״.</div></div>')


def _txc(s):
    return TX(s)


# ---------------------------------------------------------------- cartoons with a punchline
TOONS = {
 'barrel': '<rect x="28" y="20" width="64" height="88" rx="14" fill="#8a5a2b"/><rect x="24" y="38" width="72" height="7" rx="3" fill="#5b3a1a"/><rect x="24" y="84" width="72" height="7" rx="3" fill="#5b3a1a"/><circle cx="48" cy="58" r="6" fill="#fff"/><circle cx="72" cy="58" r="6" fill="#fff"/><circle cx="49" cy="59" r="3" fill="#111"/><circle cx="73" cy="59" r="3" fill="#111"/><path d="M46 72q14 11 28 0" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/><path d="M40 20l40 0-6-12-28 0z" fill="#1b2d55"/>',
 'plane': '<path d="M12 62q2-14 22-16l58-4q14 0 18 10-4 10-18 12l-58 4q-20 0-22-6z" fill="#e8eefb" stroke="#1b2d55" stroke-width="3"/><path d="M56 62l-20 34h14l28-36z" fill="#27447f"/><path d="M24 46l-10-22h10l16 20z" fill="#ff6a4d"/><circle cx="88" cy="50" r="5" fill="#111"/><path d="M80 60q8 6 16 1" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round"/><path d="M104 28q6 9 0 13q-6-4 0-13z" fill="#58b8e0"/>',
 'seesaw': '<path d="M60 74l-14 26h28z" fill="#1b2d55"/><line x1="10" y1="88" x2="110" y2="52" stroke="#8a5a2b" stroke-width="7" stroke-linecap="round"/><circle cx="22" cy="68" r="13" fill="#ffd37a"/><circle cx="98" cy="34" r="13" fill="#7fe3d6"/><path d="M16 73q6-6 12 0" fill="none" stroke="#111" stroke-width="2.5"/><path d="M92 36q6 6 12 0" fill="none" stroke="#111" stroke-width="2.5"/><circle cx="18" cy="65" r="2" fill="#111"/><circle cx="26" cy="65" r="2" fill="#111"/><circle cx="94" cy="31" r="2" fill="#111"/><circle cx="102" cy="31" r="2" fill="#111"/>',
 'umbrella': '<path d="M14 58q46-56 92 0z" fill="#ff6a4d"/><line x1="60" y1="58" x2="60" y2="100" stroke="#1b2d55" stroke-width="5"/><path d="M60 100q0 10-10 8" fill="none" stroke="#1b2d55" stroke-width="5" stroke-linecap="round"/><path d="M26 12q4 6 0 9q-4-3 0-9zM60 4q4 6 0 9q-4-3 0-9zM94 12q4 6 0 9q-4-3 0-9z" fill="#58b8e0"/>',
 'lever': '<path d="M46 86l-13 22h26z" fill="#1b2d55"/><line x1="4" y1="50" x2="116" y2="92" stroke="#8a5a2b" stroke-width="6" stroke-linecap="round"/><ellipse cx="18" cy="38" rx="17" ry="15" fill="#8a93aa"/><circle cx="104" cy="74" r="9" fill="#ffd37a" stroke="#a86703" stroke-width="2"/><text x="104" y="79" text-anchor="middle" font-size="20" font-weight="800" fill="#a86703">₪</text>',
 'dice': '<rect x="14" y="30" width="60" height="60" rx="12" fill="#fff" stroke="#1b2d55" stroke-width="4" transform="rotate(-12 44 60)"/><circle cx="32" cy="48" r="5" fill="#ff6a4d"/><circle cx="56" cy="44" r="5" fill="#ff6a4d"/><circle cx="44" cy="62" r="5" fill="#ff6a4d"/><circle cx="34" cy="78" r="5" fill="#ff6a4d"/><circle cx="58" cy="74" r="5" fill="#ff6a4d"/><rect x="66" y="58" width="42" height="42" rx="9" fill="#ffd37a" stroke="#1b2d55" stroke-width="4" transform="rotate(14 87 79)"/><circle cx="87" cy="79" r="5" fill="#1b2d55"/>',
 'sweat': '<circle cx="58" cy="62" r="40" fill="#ffd37a"/><circle cx="44" cy="54" r="5" fill="#111"/><circle cx="72" cy="54" r="5" fill="#111"/><path d="M42 80q16-12 32 0" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round"/><path d="M102 30q8 12 0 17q-8-5 0-17z" fill="#58b8e0"/><text x="16" y="28" font-size="28" font-weight="800" fill="#107c41">$</text>',
 'hands': '<rect x="36" y="14" width="48" height="58" rx="5" fill="#fff" stroke="#1b2d55" stroke-width="3"/><line x1="44" y1="28" x2="76" y2="28" stroke="#8a93aa" stroke-width="3"/><line x1="44" y1="38" x2="76" y2="38" stroke="#8a93aa" stroke-width="3"/><line x1="44" y1="48" x2="66" y2="48" stroke="#8a93aa" stroke-width="3"/><path d="M6 84l30-4 24 12 24-12 30 4v16H6z" fill="#27447f"/><path d="M42 82q18-12 36 0q-6 14-18 14t-18-14z" fill="#ffd37a" stroke="#a86703" stroke-width="2"/>',
 'ref': '<circle cx="60" cy="38" r="26" fill="#ffd37a"/><circle cx="50" cy="34" r="4" fill="#111"/><circle cx="70" cy="34" r="4" fill="#111"/><path d="M48 48q12 8 24 0" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round"/><path d="M26 112q0-46 34-46t34 46z" fill="#fff" stroke="#111" stroke-width="3"/><path d="M42 72v40M60 66v46M78 72v40" stroke="#111" stroke-width="6"/><circle cx="98" cy="52" r="8" fill="#ff6a4d"/>',
 'hourglass': '<path d="M30 14h60v8q0 22-22 38q22 16 22 38v8H30v-8q0-22 22-38Q30 44 30 22z" fill="#eef2ff" stroke="#1b2d55" stroke-width="4"/><path d="M42 26h36q-4 16-18 26q-14-10-18-26z" fill="#ffd37a"/><path d="M38 100q6-22 22-30q16 8 22 30z" fill="#ffd37a"/>',
 'wheat': '<rect x="20" y="56" width="80" height="50" fill="#e8eefb" stroke="#1b2d55" stroke-width="3"/><path d="M14 56l46-30 46 30z" fill="#27447f"/><path d="M36 64v36M60 64v36M84 64v36" stroke="#1b2d55" stroke-width="5"/><path d="M104 12v50M104 22l-9-7M104 22l9-7M104 34l-9-7M104 34l9-7M104 46l-9-7M104 46l9-7" stroke="#e8960c" stroke-width="4" stroke-linecap="round"/>',
 'robot': '<rect x="22" y="26" width="76" height="72" rx="14" fill="#217346"/><text x="60" y="58" text-anchor="middle" font-size="24" font-weight="800" fill="#fff">fx</text><circle cx="44" cy="70" r="6" fill="#fff"/><circle cx="76" cy="70" r="6" fill="#fff"/><circle cx="45" cy="71" r="3" fill="#111"/><circle cx="77" cy="71" r="3" fill="#111"/><path d="M46 84q14 9 28 0" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/><line x1="60" y1="26" x2="60" y2="10" stroke="#217346" stroke-width="4"/><circle cx="60" cy="8" r="5" fill="#ff6a4d"/>',
 'voucher': '<rect x="10" y="36" width="100" height="52" rx="8" fill="#fff0d2" stroke="#a86703" stroke-width="3"/><line x1="78" y1="36" x2="78" y2="88" stroke="#a86703" stroke-width="3" stroke-dasharray="4 4"/><path d="M22 62l34-8-6 8 6 8z" fill="#27447f"/><text x="94" y="68" text-anchor="middle" font-size="18" font-weight="800" fill="#a86703">₪</text>',
 'bond': '<rect x="14" y="16" width="92" height="76" rx="8" fill="#fff8e6" stroke="#a86703" stroke-width="3"/><rect x="22" y="24" width="76" height="60" rx="5" fill="none" stroke="#e8c27a" stroke-width="2" stroke-dasharray="4 3"/><text x="60" y="46" text-anchor="middle" font-size="16" font-weight="800" fill="#1b2d55">100 ₪</text><circle cx="46" cy="62" r="4" fill="#111"/><circle cx="74" cy="62" r="4" fill="#111"/><path d="M48 72q12 9 24 0" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round"/><path d="M60 92v18M50 110h20" stroke="#a86703" stroke-width="4" stroke-linecap="round"/>',
 'piggy': '<ellipse cx="58" cy="66" rx="40" ry="30" fill="#ffb3c1"/><circle cx="96" cy="62" r="11" fill="#ff8fa6"/><circle cx="93" cy="60" r="2" fill="#111"/><circle cx="99" cy="60" r="2" fill="#111"/><circle cx="74" cy="52" r="4" fill="#111"/><path d="M40 92v14M72 92v14" stroke="#ff8fa6" stroke-width="8" stroke-linecap="round"/><rect x="46" y="34" width="22" height="5" rx="2" fill="#7a2a3a"/><circle cx="57" cy="16" r="11" fill="#ffd37a" stroke="#a86703" stroke-width="2"/><text x="57" y="22" text-anchor="middle" font-size="17" font-weight="800" fill="#a86703">₪</text>',
 'clock': '<circle cx="60" cy="62" r="42" fill="#fff" stroke="#1b2d55" stroke-width="5"/><path d="M60 62V34M60 62l18 12" stroke="#ff6a4d" stroke-width="5" stroke-linecap="round"/><circle cx="60" cy="62" r="5" fill="#1b2d55"/><path d="M28 18l-12 12M92 18l12 12" stroke="#1b2d55" stroke-width="6" stroke-linecap="round"/><circle cx="44" cy="84" r="3" fill="#111"/><circle cx="76" cy="84" r="3" fill="#111"/>',
 'stairs': '<path d="M10 104h100v-16H86V70H62V52H38V34H14z" fill="#7fe3d6" stroke="#0f9d90" stroke-width="3"/><circle cx="26" cy="22" r="9" fill="#ffd37a"/><path d="M26 31v14M26 36l-8 6M26 36l8 6" stroke="#1b2d55" stroke-width="3" stroke-linecap="round"/><text x="98" y="62" text-anchor="middle" font-size="18" font-weight="800" fill="#c4421f">₪</text>',
 'scale': '<path d="M60 18v74M30 104h60" stroke="#1b2d55" stroke-width="5" stroke-linecap="round"/><path d="M16 40l88-10" stroke="#8a5a2b" stroke-width="5" stroke-linecap="round"/><path d="M16 40l-10 24h20zM104 30l-10 24h20z" fill="#ffd37a" stroke="#a86703" stroke-width="2"/><text x="16" y="80" text-anchor="middle" font-size="15" font-weight="800" fill="#1b2d55">r</text><text x="104" y="70" text-anchor="middle" font-size="15" font-weight="800" fill="#1b2d55">c</text><circle cx="60" cy="16" r="6" fill="#ff6a4d"/>',
 'calc': '<rect x="26" y="10" width="68" height="100" rx="10" fill="#1b2d55"/><rect x="34" y="18" width="52" height="22" rx="4" fill="#dff5f2"/><text x="82" y="35" text-anchor="end" font-size="15" font-weight="800" fill="#1b2d55">90.47</text><g fill="#fff"><rect x="34" y="48" width="14" height="12" rx="3"/><rect x="53" y="48" width="14" height="12" rx="3"/><rect x="72" y="48" width="14" height="12" rx="3"/><rect x="34" y="66" width="14" height="12" rx="3"/><rect x="53" y="66" width="14" height="12" rx="3"/><rect x="34" y="84" width="14" height="12" rx="3"/><rect x="53" y="84" width="14" height="12" rx="3"/></g><rect x="72" y="66" width="14" height="30" rx="3" fill="#ff6a4d"/>',

}


def TOON(key, punch, n=0):
    """A small cartoon with a punchline, in the empty corner of a slide."""
    svg = f'<svg viewBox="0 0 120 120" dir="ltr" role="img" aria-hidden="true">{TOONS[key]}</svg>'
    return ST(n, f'{svg}<div class="bub">{TX(punch)}</div>', cls='toon') if n else f'<div class="toon">{svg}<div class="bub">{TX(punch)}</div></div>'


# ---------------------------------------------------------------- embedded Excel
import fin as _fin


def xl_eval(data, sol):
    """Evaluate the solution in Python (fin.py): used in the PDF, and as an independent check of each exercise."""
    v, _ = _fin.evaluate({**data, **sol})
    return v


def _fmtx(v, f=''):
    """A cell value as the sheet shows it. f: pct0..pct6, num0..num6 or '' (up to 2 decimals)."""
    if isinstance(v, str): return v
    if v is None: return ''
    m = re.fullmatch(r'(pct|num)(\d)', f or '')
    if m:
        d = int(m.group(2)); x = v * 100 if m.group(1) == 'pct' else v
        t = f'{x:,.{d}f}' + ('%' if m.group(1) == 'pct' else '')
    else:
        x = round(v, 2); t = f'{x:,.2f}'.rstrip('0').rstrip('.') if x != int(x) else f'{int(x):,}'
    return t.replace('-', '−')


_ARGN = {'PV': ['rate', 'nper', 'pmt', 'fv', 'type'], 'FV': ['rate', 'nper', 'pmt', 'pv', 'type'], 'PMT': ['rate', 'nper', 'pv', 'fv', 'type'],
         'NPER': ['rate', 'pmt', 'pv', 'fv', 'type'], 'RATE': ['nper', 'pmt', 'pv', 'fv', 'type'], 'NPV': ['rate']}


def _argnames(data, sol, head):
    """Shay, 2026-11-03: beside the Hebrew label, the English name of the argument it feeds (rate, nper, pmt, pv, fv),
    so the order of the arguments is visible where the student points. Read from the solution's function calls."""
    names = {}
    for f in sol.values():
        if not str(f).startswith('='): continue
        for m in re.finditer(r'\b(PV|FV|PMT|NPER|RATE|NPV)\(', f):
            i, depth, args, cur = m.end(), 1, [], ''
            while i < len(f) and depth:
                ch = f[i]
                if ch == '(': depth += 1
                elif ch == ')':
                    depth -= 1
                    if not depth: break
                if ch == ',' and depth == 1: args.append(cur); cur = ''
                else: cur += ch
                i += 1
            args.append(cur)
            for k, a in enumerate(args):
                r = re.fullmatch(r'\$?([A-Z]+)\$?(\d+)', a.strip())
                if r and k < len(_ARGN[m.group(1)]):
                    names.setdefault(r.group(1) + r.group(2), _ARGN[m.group(1)][k])
    for cell, nm in names.items():
        col, row = re.match(r'([A-Z]+)(\d+)', cell).groups(); row = int(row)
        # the label of the row (a text cell to its right in the sheet, so a lower column letter), or else the header of its column
        lab = [a for a in data if re.fullmatch(r'[A-Z]+' + str(row), a) and isinstance(data[a], str) and not data[a].startswith('=') and a[0] < col]
        if not lab:
            lab = [a for a in data if a[0] == col and isinstance(data[a], str) and int(re.sub('[A-Z]', '', a)) < row and int(re.sub('[A-Z]', '', a)) in head]
        if not lab: continue
        rowtxt = ' '.join(str(data[a]) for a in data if re.fullmatch(r'[A-Z]+' + str(row), a) and isinstance(data[a], str))
        a = lab[0]
        # nper is the number of payments in the series, never 'years': the label says so
        if nm == 'nper' and re.fullmatch(r'(מספר )?שנים|שנה', str(data[a]).strip()):
            data[a] = 'מספר תשלומים'
        if re.search(r'\b' + nm + r'\b', rowtxt) or re.search(r'\b' + nm + r'\b', str(data[a])) or '(' in str(data[a]): continue
        data[a] = f'{data[a]} ({nm})'
    # by role, on every sheet (Shay, 2026-11-03): the Excel name of each parameter beside its Hebrew label
    labels = {a: v for a, v in data.items() if isinstance(v, str) and not v.startswith('=') and int(re.sub('[A-Z]', '', a)) not in head}
    amort = any(re.search(r'יתר[הת]', str(v)) for v in data.values())
    for a, v in labels.items():
        t = v.strip()
        if '(' in t: continue
        if re.fullmatch(r'מספר תשלומים', t): data[a] = t + ' (nper)'
        elif not amort and re.fullmatch(r'ערך נקוב', t): data[a] = t + ' (fv)'
        elif not amort and re.fullmatch(r'קופון( שנתי| לחצי שנה| לרבעון| לתשלום)?', t): data[a] = t + ' (pmt)'
    return data


def _auto_steps(data, sol, head, fmt):
    """Shay, 2026-11-10: every sheet has a ״הצעד הבא״ button. Where a question has no hand-written steps, they are built from its
    solution: one step per formula, and one step for a formula dragged down a column, each with its label and its result."""
    vals = xl_eval(data, {**{a: v for a, v in data.items()}, **sol}) if sol else {}
    def label(a):
        col, row = re.match(r'([A-Z]+)(\d+)', a).groups(); row = int(row)
        lab = [str(v) for k, v in data.items() if isinstance(v, str) and not v.startswith('=') and re.fullmatch(r'[A-Z]+' + str(row), k) and k < a and row not in head]
        if lab: return re.sub(r'\s*\((rate|nper|pmt|pv|fv)\)$', '', lab[0])
        hd = [str(data[k]) for k in data if re.fullmatch(col + r'(\d+)', k) and int(k[len(col):]) in head and int(k[len(col):]) < row]
        return hd[-1] if hd else a
    def shown(a):
        v = vals.get(a)
        return '' if not isinstance(v, (int, float)) else ', כלומר ' + _fmtx(v, fmt.get(a, ''))
    out, keys, i = [], list(sol), 0
    while i < len(keys):
        a = keys[i]; col, row = re.match(r'([A-Z]+)(\d+)', a).groups(); j = i
        # a run of cells in one column, one under the other, whose formulas differ only by their relative row numbers: one dragged step
        def rel(k):
            r = int(re.match(r'[A-Z]+(\d+)', k).group(1))
            return re.sub(r'(?<![$A-Z])([A-Z]{1,2})(\d+)', lambda m: m.group(1) + 'R' + str(int(m.group(2)) - r), str(sol[k]))
        while j + 1 < len(keys) and re.fullmatch(col + r'\d+', keys[j + 1]) and int(keys[j + 1][len(col):]) == int(keys[j][len(col):]) + 1 and str(sol[keys[j + 1]]).startswith('=') and rel(keys[j + 1]) == rel(a):
            j += 1
        f = str(sol[a])
        if j > i:
            out.append(dict(cells={k: sol[k] for k in keys[i:j + 1]}, note=f'{label(a)}: {f} בתא {a}, וגוררים עד {keys[j]}' + shown(a) + '.', sel=a, sel2=keys[j]))
        else:
            out.append(dict(cells={a: sol[a]}, note=f'{label(a)}: {f}' + shown(a) + '.', sel=a))
        i = j + 1
    return out


def _xsheet(sid, task, data, sol, widths, head, rows=None, cols=None, hints=None, remind=None, partial=None, chart=None, values=False, done='', extra='',
            fmt=None, traps=None, allow=None, r0=1, maxh=None, tol=None, need=None, needMsg=None, xname=None, xtitle=None, steps=None, side=False, title='', signMsg=None, qtext=None, build=None):
    """The live sheet itself. side=True: the sheet sits beside a question, and its feedback goes under the question (an element .xfb)."""
    fmt = fmt or {}
    # Shay, 2026-11-03: the sheet holds no number of the solution. Every number of the question (and every period number) is typed by the student,
    # and every given formula is written by the student. Only text labels stay as the structure of the table.
    def _raw(a, v):
        if isinstance(v, float) and re.fullmatch(r'pct\d', fmt.get(a, '') or ''):
            return f'{round(v * 100, 10):.12g}%'
        return f'{v:.15g}' if isinstance(v, float) else str(v)
    inputs = {a: _raw(a, v) for a, v in data.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    given_f = {a: v for a, v in data.items() if isinstance(v, str) and v.startswith('=')}
    for a, v in data.items():
        if a in inputs:
            r = inputs[a]; back = float(r[:-1]) / 100 if r.endswith('%') else float(r)
            assert abs(back - v) <= 1e-12 * max(1, abs(v)), (sid, a, v, r)
    data = {a: v for a, v in data.items() if a not in inputs and a not in given_f}
    sol = {**inputs, **given_f, **sol}
    data = _argnames(dict(data), sol, head)
    if not steps:
        steps = _auto_steps(data, {a: v for a, v in sol.items() if a not in inputs and a not in given_f}, head, fmt)
    if steps:
        steps = ([dict(cells=dict(inputs), note='מזינים את נתוני השאלה בתאים, כפי שהם כתובים בשאלה. אחוזים כותבים עם סימן האחוז.', sel=next(iter(inputs)))] if inputs else []) + \
                ([dict(cells=dict(given_f), note='התאמות לתקופה: ' + ' '.join(f'{a}: {f}' for a, f in given_f.items()))] if given_f else []) + steps
    partial = list(inputs) + list(given_f) + list(partial or [a for a in sol if a not in inputs and a not in given_f][:1])
    vals = xl_eval(data, sol)
    targets = list(sol)
    rs = rows or max(int(re.sub('[A-Z]', '', a)) for a in list(data) + targets)
    cs = cols or max(ord(a[0]) - 64 for a in list(data) + targets)
    for st in steps or []:
        assert all(st['cells'][a] == sol[a] for a in st['cells']), (sid, 'a step must write the solution formula')
    if steps: assert set().union(*[set(st['cells']) for st in steps]) == set(sol), (sid, 'the steps must cover every target')
    XSPECS.append(dict(qtext=qtext or task, vin=list(inputs), sid=sid, name=xname or sid, title=xtitle or re.sub('<[^>]+>', '', title), task=re.sub('<[^>]+>', '', task).replace('¤', '$'), data=data, sol=sol, fmt=fmt, widths=widths, head=head, rows=rs, cols=cs, r0=r0, vals=vals, part=CUR[0]))
    if MODE == 'pdf':
        L = [chr(65 + i) for i in range(cs)]
        t = ''
        for r in range(r0, rs + 1):
            cells = []
            for c in L:
                a = f'{c}{r}'
                x = vals.get(a) if (a in sol or str(data.get(a, '')).startswith('=')) else data.get(a, '')
                cells.append(_fmtx(x, fmt.get(a, '')) if not isinstance(x, str) else x)
            if any(cells):
                tag = 'th' if r in head else 'td'
                t += f'<tr><td class="rn">{r}</td>' + ''.join(f'<{tag}>{TX(x)}</{tag}>' for x in cells) + '</tr>'
        hdr = '<tr><th class="rn"></th>' + ''.join(f'<th>{c}</th>' for c in L) + '</tr>'
        if steps:
            fm = '<ol class="xsteps">' + ''.join(f'<li>{TX(FXW(st["note"]))} ' + ' '.join(f'<span class="fx"><b>{a}</b> ' + XL(st['cells'][a].replace('$', '¤')) + '</span>' for a in _repr_targets(st['cells'])) + '</li>' for st in steps) + '</ol>'
        else:
            fm = '<p class="fml">' + ' '.join(f'<span class="fx"><b>{a}</b> ' + XL(sol[a].replace('$', '¤')) + '</span>' for a in _repr_targets(sol)) + '</p>'
        return f'<p class="qstem">{TX(task)}</p><table class="tbl2 xlp">{hdr}{t}</table>{fm}'
    NACT[0] += 1
    # Shay, 2026-11-10: use the screen. The live sheet shows spare empty rows and columns, as a full Excel window does; the slide fit
    # caps its height to the free space, so it always fills the area under and beside the table. The spec (and the appendix) keep the real size.
    real_w = sum(widths) + max(0, cs - len(widths)) * 92
    pad_c = max(0, int(((540 if side else 1100) - real_w - 50) // 80))
    widths = list(widths) + [92] * max(0, cs - len(widths)) + [80] * pad_c
    cfgd = dict(rows=rs + 14, cols=cs + pad_c, widths=widths, data={k: str(v) for k, v in data.items()}, targets=targets, solution=sol, headRows=head, inputs=[], fmt=fmt, solFmt=fmt,
                hints=[TX(FXW(x)) for x in (hints or ['קראו שוב את כותרת העמודה, וכתבו את החישוב במילים לפני הנוסחה.'])], remind=TX(FXW(remind or '')), partial=partial or targets[:1], values=values, done=TX(FXW(done)))
    if not remind: cfgd.pop('remind')
    if traps: cfgd['traps'] = {a: [[f, TX(FXW(m))] for f, m in L] for a, L in traps.items()}
    if allow is not None: cfgd['allow'] = allow
    if r0 > 1: cfgd['r0'] = r0
    cfgd['maxh'] = maxh or 2000   # the real height is fitted to the slide at runtime
    if tol is not None: cfgd['tol'] = tol
    if signMsg: cfgd['signMsg'] = TX(signMsg)
    if inputs: cfgd['vin'] = list(inputs)
    if build:
        # the label cells of each group are held back, and appear one group per click
        bc = [a for cells, _ in build for a in cells]
        assert all(a in data for a in bc), (sid, 'a build cell must be a label')
        cfgd['bdata'] = {a: data[a] for a in bc}
        cfgd['data'] = {k: v for k, v in cfgd['data'].items() if k not in bc}
        cfgd['build'] = [dict(cells=cells, note=TX(FXW(note))) for cells, note in build]
    if need: cfgd['need'] = need; cfgd['needMsg'] = needMsg or ''
    if steps: cfgd['steps'] = [dict(cells=st['cells'], note=TX(FXW(st['note'])), **({'sel': st['sel']} if st.get('sel') else {}), **({'sel2': st['sel2']} if st.get('sel2') else {})) for st in steps]
    sv = ''
    if chart:
        cfgd['chart'] = chart
        sv = f'<svg class="xlc" viewBox="0 0 {chart.get("W", 470)} {chart.get("H", 330)}" role="img" aria-label="תרשים"></svg>'
    if side:
        return cfgd, f'<div class="tasktxt sm">{TX(task)}</div><div class="sheet"></div>{extra}'
    return cfgd, f'<div class="tasktxt">{TX(task)}</div><div class="xlrow{"" if chart else " solo"}"><div class="sheet"></div><div class="xlside">{sv}</div></div>{extra}'


def XLS(sid, title, h, task, data, sol, widths, head, **kw):
    """A slide with one live sheet and its task."""
    r = _xsheet(sid, task, data, sol, widths, head, title=h, **kw)
    if MODE == 'pdf':
        S(sid, title, h, r); return
    cfgd, inner = r
    S(sid, title, h, f'<div class="act xlq" id="{sid}-x" data-cfg="{_cfg(cfgd)}">{inner}</div>', kick=f'חלק {CUR[0]} · אקסל בתוך השקף')


def QX(sid, tag, title, stem, task, data, sol, widths, head, note=None, qmc='', kicktag=None, **kw):
    """A question beside the live sheet in which it is solved. No algebra: the steps are formulas in the sheet."""
    head_t = f'{tag}: {title}' if tag else title
    stem_html = ''.join(f'<p>{TX(x)}</p>' for x in stem)
    notes = ''.join(BAND(*x) if MODE == 'deck' else BAND(x[0], x[1]) for x in (note or []))   # (kind, text) or (kind, text, click): revealed beside the sheet
    r = _xsheet(sid, task, data, sol, widths, head, side=True, title=head_t, qtext=' '.join(re.sub('<[^>]+>', '', x) for x in stem), **kw)
    if MODE == 'pdf':
        S(sid, head_t, head_t, f'<div class="qstem">{stem_html}</div>{qmc}{r}{notes}', kind='q'); return
    cfgd, inner = r
    ch = cfgd.get('chart')
    sv = f'<svg class="xlc" viewBox="0 0 {ch.get("W", 470)} {ch.get("H", 330)}" role="img" aria-label="תרשים"></svg>' if ch else ''
    S(sid, head_t, head_t, f'<div class="act xlq qx" id="{sid}-x" data-cfg="{_cfg(cfgd)}"><div class="qr"><div class="card qstem">{stem_html}</div>{qmc}{sv}{notes}</div><div class="xw">{inner}<div class="xfb"></div></div></div>',
      kick=f'חלק {CUR[0]} · {kicktag or tag or "שאלה ואקסל"}', cls='qslide')


def MCX(sid, title, h, item, task, data, sol, widths, head, **kw):
    """A multiple choice question with a live sheet beside it, where the answer is computed with the right formula."""
    qt = re.sub('<[^>]+>', ' ', item.split('<div class="w">')[0]); qt = re.sub(r'\s+', ' ', qt).strip()
    r = _xsheet(sid, task, data, sol, widths, head, side=True, title=h, qtext=qt + ' ' + re.sub('<[^>]+>', '', task), **kw)
    if MODE == 'pdf':
        S(sid, title, h, item + r); return
    cfgd, inner = r
    S(sid, title, h, f'<div class="act xlq qx" id="{sid}-x" data-cfg="{_cfg(cfgd)}"><div class="qr">{item}</div><div class="xw">{inner}<div class="xfb"></div></div></div>', kick=f'חלק {CUR[0]} · שאלה ואקסל', cls='qslide')


def _repr_targets(sol):
    """One formula per column of targets (the first one), so the PDF shows the pattern without repeating dragged copies."""
    seen, out = set(), []
    for a in sol:
        c = re.match(r'[A-Z]+', a).group(0)
        if c not in seen: seen.add(c); out.append(a)
    return out


def SOLVE(sid, title, h, story, parts, hints, remind, steps):
    """A math exercise: parts (label, answer, tolerance). Buttons give a hint, a reminder, a partial or a full solution."""
    if MODE == 'pdf':
        p = ''.join(f'<li>{TX(l)} <b>{_fmtv(float(a)) if not isinstance(a, str) else a}</b></li>' for l, a, t in parts)
        S(sid, title, h, f'<p class="qstem">{TX(story)}</p><ol>{p}</ol>' + ''.join(f'<p>{TX(x)}</p>' for x in steps))
        return
    NACT[0] += 1
    ps = ''.join(f'<label class="svp" data-a="{a}" data-tol="{t}"><span>{TX(l)}</span><input dir="ltr" inputmode="decimal" autocomplete="off" spellcheck="false"></label>' for l, a, t in parts)
    ss = ''.join(f'<div class="svs">{TX(x)}</div>' for x in steps)
    cfgd = dict(hints=[TX(x) for x in hints], remind=TX(remind))
    btn = lambda c, t: f'<button class="abtn ghost {c}">{t}</button>'
    S(sid, title, h, f'<div class="act sv" id="{sid}-w" data-cfg="{_cfg(cfgd)}"><div class="tasktxt">{TX(story)}</div><div class="svps">{ps}</div><div class="actbar">{CHK}{btn("hnt", "💡 רמז")}{btn("rmd", "📐 תזכורת נוסחה")}{btn("prt", "פתרון חלקי")}{btn("ful", "פתרון מלא")}{RST}</div><div class="fbbar">הקלידו את התשובות, ולחצו ״בדיקה״. הפסד כותבים כמספר שלילי.</div><div class="svsol">{ss}</div></div>', kick=f'חלק {CUR[0]} · תרגיל')


def CASE(sid, title, story, qtext, opts, a, why, steps, toon=None):
    """One situation on its own slide: a question, then a multi step explanation revealed by clicks."""
    q = mc(sid + '-q', qtext, opts, a, why, rot=False)
    st = ''.join(ST(i + 1, TX(x), 'p', 'sp') for i, x in enumerate(steps))
    S(sid, title, title, f'<div class="qg"><div class="qr"><div class="card qstem"><p>{TX(story)}</p></div>{q}</div><div class="solw card">{st}</div></div>', kick=f'חלק {CUR[0]} · מקרה', cls='qslide')


def STEPS(chart, items, cls=''):
    """A chart built click by click beside its explanation. items: prose or '=' + math, in click order."""
    return f'<div class="qg {cls}"><div class="card chartw">{chart}</div><div class="rl">{items}</div></div>'


def RL(items, start=1):
    out = ''
    for i, x in enumerate(items):
        n = start + i
        if isinstance(x, tuple):
            n, x = x
        out += ST(n, M(x[1:]), cls='eq').replace('class="st eq"', 'class="st eq" dir="ltr"') if x.startswith('=') else ST(n, TX(x), 'p', 'sp')
    return out


exec(R('content_g.py'))
for _f in {1: ['content_l1a.py', 'content_l1b.py', 'content_l1c.py'], 2: ['content_l2a.py', 'content_l2b.py', 'content_l2c.py']}[LESSON]:
    exec(R(_f))
