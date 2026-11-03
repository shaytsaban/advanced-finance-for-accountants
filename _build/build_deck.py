# Lesson deck. Run: python3 build_deck.py 1  (or 2)  ->  ../lectures/lecture-N/presentation.html
import os, re, json, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
R = lambda f: open(os.path.join(H, f), encoding='utf8').read()
MODE = 'deck'
LESSON = int(sys.argv[1]) if len(sys.argv) > 1 else 1
exec(R('content_a.py'))

HEAD = f'{COURSE} · מפגש {LESSON}' + (f' · {LMETA["date"]}' if LMETA['date'] else '')


def render(s, total):
    k = s['kind']
    if k == 'title':
        chips = [f'{NX} גיליונות Excel חיים בתוך השקפים'] + ([f'{NSV} תרגילים עם רמזים'] if NSV else []) + [f'{NMC} שאלות רב ברירה', LMETA['chip']]
        return (f'<section class="slide dark s1 on" id="s-title" data-title="פתיחה">'
                '<div class="orb" style="width:320px;height:320px;background:radial-gradient(circle at 30% 30%,#58e0cf,#0f9d90 60%,transparent 72%);left:-90px;top:-70px"></div>'
                '<div class="orb" style="width:180px;height:180px;background:radial-gradient(circle at 30% 30%,#ffd37a,#e8960c 60%,transparent 72%);left:230px;bottom:90px;animation-delay:-3s"></div>'
                '<div style="position:absolute;right:70px;top:84px;width:960px">'
                f'<div class="kick" style="color:#ffb199"><span>{TX(HEAD)}</span></div>'
                f'<h1><span>{LMETA["h1"][0]}</span> <span style="color:#7fe3d6">{LMETA["h1"][1]}</span></h1>'
                '<p class="sub" style="margin-top:20px;font-size:27px;color:#c8d4f2">' + TX(LMETA['sub']) + '</p>'
                '<div class="chipbar" style="margin-top:24px">' + ''.join(f'<span class="chip">{TX(c)}</span>' for c in chips) + '</div></div>'
                f'<div style="position:absolute;right:70px;bottom:58px;font-size:22px;color:#c8d4f2"><b style="color:#fff">ד״ר שי צבאן</b> · {INST} · {SEM}</div></section>')
    if k == 'end':
        return ('<section class="slide dark s1" id="s-end" data-title="סיום"><div style="position:relative;max-width:980px;margin-top:110px">'
                f'<div class="kick" style="color:#ffb199">סוף מפגש {LESSON}</div>'
                f'<h1 style="font-size:60px">במפגש הבא: <span style="color:#7fe3d6">{LMETA["next_h"]}</span></h1>'
                '<p class="sub" style="font-size:25px;margin-top:20px;color:#c8d4f2;max-width:940px">' + TX(LMETA['next_t']) + '</p>'
                '<p class="sub" style="font-size:22px;margin-top:26px;color:#c8d4f2">פניות רק במייל: <span dir="ltr">shay.tsaban@gmail.com</span>. חובה לרשום את שם המוסד ואת שם הקורס.</p></div></section>')
    if k == 'opener':
        n = s['part']
        when = f'לעבודה עצמית · כ-{s["mins"]} דקות' if n == total else f'כ-{s["mins"]} דקות'
        note = f'<div class="pd-note">{TX(s["note"])}</div>' if s.get('note') else ''
        return (f'<section class="slide dark pd" id="{s["id"]}" data-title="{s["title"]}" style="--pc:#7fe3d6"><div class="pd-num">{n}</div><div class="pd-in">'
                f'<div class="kick" style="color:#ffb199"><span>חלק <span class="n">{n}</span> מתוך <span class="n">{total}</span> · {TX(when)}</span></div><div class="pd-h">{s["h"]}</div><div class="pd-q">{TX(s["q"])}</div>{note}'
                f'<div class="pd-cols"><div class="pd-box"><b>מה נעשה בחלק הזה</b><ul>{"".join("<li>" + TX(x) + "</li>" for x in s["learn"])}</ul></div></div></div></section>')
    kick = f'<div class="kick"><span>{TX(s["kick"])}</span></div>' if s.get('kick') else ''
    return f'<section class="slide {s["cls"]}" id="{s["id"]}" data-title="{re.sub("<[^>]+>", "", s["title"])}">{kick}<h2>{TX(s["h"])}</h2>{s["body"]}</section>'


NMC = sum(s['body'].count('class="mc"') for s in SL)
NX = sum(s['body'].count('act xlq') for s in SL)
NSV = sum(s['body'].count('act sv') for s in SL)
slides_html = '\n'.join(render(s, TOTAL_PARTS) for s in SL)
fonts = R('shell/fonts.css')
base = R('shell/base.css')
tail = R('shell/tail.html')
gj = json.dumps({k: {f: (TX(FXW(v)) if f != 'en' else v) for f, v in g.items()} for k, g in G.items()}, ensure_ascii=False)
js = f'const COURSE={json.dumps(COURSE, ensure_ascii=False)};const LESSON={LESSON};\nconst G={gj};\n' + R('deck.js') + '\n' + R('xl.js') + '\n' + R('act.js')
title = f'{COURSE} | שיעור {LESSON} | {LMETA["title"]}'
html = (f'<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>{title}</title>\n<style>\n'
        + fonts + base + R('deck.css') + '</style>\n</head>\n<body>\n<div class="stage" id="stage">\n' + slides_html + '\n' + tail
        + '<script>\n(function(){\n' + js + '\n})();\n</script>\n</body>\n</html>\n').replace('¤', '$')
for bad in ('—', '־', '–', '…'):
    assert bad not in html.replace(fonts, ''), 'forbidden character ' + bad
out = os.path.join(H, '..', 'lectures', f'lecture-{LESSON}')
os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'presentation.html'), 'w', encoding='utf8').write(html)
css = fonts + base + R('deck.css')
used = set()
for m in re.finditer(r'class="([^"]+)"', slides_html + tail + R('deck.js') + R('act.js')):
    for c in m.group(1).split():
        if re.fullmatch(r'[\w-]+', c): used.add(c)
missing = sorted(c for c in used if not re.search(r'\.' + re.escape(c) + r'(?![\w-])', css))
print('slides', html.count('<section class="slide'), 'activities', NACT[0], 'excel', NX, 'solve', NSV, 'mc', NMC, 'bytes', len(html))
print('classes without a rule:', missing)
