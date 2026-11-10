# Course hub. Run: python3 build_hub.py  ->  ../index.html
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from booklet_plan import RELAID as BK, span as BKSPAN
H = os.path.dirname(os.path.abspath(__file__))
n = lambda s: f'<span class="n">{s}</span>'
UP = [(2, 'אג״ח לשיעורין, ומחיר לפי תאריכים, לפני ואחרי קופון'), (3, 'חילוץ תשואה לפדיון ותשואה לתקופת החזקה'), (4, 'מלווה קצר מועד (מק״מ), אג״ח צמיתה ומשמעות משך החיים הממוצע (מח״מ)'), (5, 'אג״ח צמודות למדד ולדולר'), (6, 'תמחור מניות: מודל הדיבידנדים, תשואת דיבידנד ומכפיל רווח'), (7, 'תמחור מניות: הזדמנויות צמיחה, מכפיל ענפי ודיבידנד רבעוני'), (8, 'מחיר ההון של החברה: ביטא ומחיר הון ממוצע משוקלל'), ('9 ו-10', 'מינוף פיננסי: מודיליאני ומילר, בלי מסים ועם מסים'), (11, 'חכירה לעומת רכישה')]
UP = UP[1:]   # lesson 2 has its card
UP = [(4, 'חילוץ תשואה בין מועדי תשלום ותשואה לתקופת החזקה. ' + UP[1][1])] + UP[2:]   # lesson 3 has its card; the rest of the old topic 3 opens lesson 4
ups = ''.join(f'<li><span class="un">{n(i if isinstance(i, int) else i.replace(" ו-", "-"))}</span><span>{t}</span><em>בקרוב</em></li>' for i, t in UP)
# Shay, 2026-11-03: lesson 1 ended before amortizing bonds; they open lesson 2. Homework is cut from chapter 1 by what each lesson taught.
LESSONS = [
 dict(k=1, date='3.11.2026', rec='https://youtu.be/DHylIX0bqH0', h='אג״ח שקליות: שווי, ריבית נקובה ותשואה לפדיון',
      learn=['אגרת חוב (אג״ח): ערך נקוב, ריבית נקובה, קופון ומועד פדיון', 'שיעור תשואה לפדיון (YTM), רציונל ותהליך התמחור', 'שווי אג״ח בטבלת תזרימים ובפונקציות NPV ו-PV, ומוסכמת הסימן',
             'פרמיה, נכיון ופארי, וקופון חצי שנתי ורבעוני', 'שבעה תרגילים חדשים לעבודה עצמית, עם רמזים ופתרון'],
      ),
 dict(k=2, date='10.11.2026', h='אג״ח לשיעורין ושווי אחרי ההנפקה',
      learn=['תזכורת קצרה לשיעור 1', 'אג״ח לשיעורין ויתרת ערך נקוב: הקופון מחושב על היתרה בתחילת התקופה', 'לוח סילוקין מלא בגיליון, ושווי ב-NPV, גם בקופון חצי שנתי ורבעוני',
             'שווי מיד אחרי תשלום, ושווי בין מועדי תשלום: NPV ודחיפה קדימה לפי חודשים', 'תרגול עצמי מהקל אל הכבד, עם רמזים ופתרון בשלבים'],
      ),
 dict(k=3, h='שווי לפני תשלום, מסחר בין מועדים וחילוץ תשואה',
      learn=['תזכורת קצרה לשיעור 2, וממשיכים מהשאלה שבה עצרנו: שאלה 3 מקובץ שיעור 2, סעיפים ג ו-ד', 'שווי רגע לפני תשלום: שתי דרכים לאותה תוצאה', 'אג״ח שנקנית ביום שבין שני מועדי תשלום',
             'חילוץ תשואה לפדיון: הפונקציות IRR ו-RATE, והמרה לתשואה שנתית בחזקה', 'חילוץ תשואה באג״ח לשיעורין, ותרגול עצמי'],
      ),
]


def card(L):
    k = L['k']
    D = open(os.path.join(H, '..', 'lectures', f'lecture-{k}', 'presentation.html'), encoding='utf8').read()
    NS, NX = D.count('<section class="slide'), D.count('act xlq')
    learn = ''.join(f'<li>{x}</li>' for x in L['learn'])
    e = len(BK[k]['exams'])
    nums = re.sub(r'(\d+\.\d+)', lambda m: n(m.group(1)), BKSPAN(k))
    L['hw'] = f'פרק {n(k)} בקובץ התרגילים: תרגילים {nums}' + ('' if not e else (', ותרגיל אחד בסגנון בחינה' if e == 1 else f', ו-{n(e)} תרגילים בסגנון בחינה'))
    L['hwnote'] = f'הקובץ כולל רק את התרגילים של שיעור {n(k)}, מסודרים לפי נושא. אין צורך לחפש תרגילים בפרקים אחרים.'
    yid = L['rec'].rstrip('/').split('/')[-1] if L.get('rec') else ''
    rec = (f'<div class="rec" id="recording-{k}"><h4>🎥 הקלטת השיעור · {n(L["date"])}</h4><div class="recbox">'
           f'<iframe src="https://www.youtube.com/embed/{yid}" title="הקלטת שיעור {k}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
           f'<a class="yt" href="{L["rec"]}" target="_blank" rel="noopener">לצפייה ב-YouTube</a></div>') if yid else ''
    return f'''<article class="lec" id="lesson-{k}">
<div class="lec-head"><div class="lec-n">{k}</div><div><h3>{L['h']}</h3><div class="sub">מפגש {n(k)}{(' · ' + n(L['date'])) if L.get('date') else ''}</div></div></div>
<div class="lec-body">
<div><h4>מה לומדים בשיעור</h4><ul class="learn">
{learn}
</ul>{rec}</div>
<div><h4>חומרי השיעור</h4>
<div class="grp"><h5>1. בשיעור</h5><div class="links">
<a class="lk p" href="lectures/lecture-{k}/presentation.html"><span class="e">🖥️</span><span><b>מצגת השיעור</b><span class="d">המצגת שבה עובדים בשיעור: {n(NS)} שקפים, וגיליון Excel חי ליד כל שאלה ({n(NX)} גיליונות), עם בדיקה ומשוב.</span></span></a>
<a class="lk x" href="materials/lesson-{k}-appendix.xlsx" download><span class="e">📊</span><span><b>אקסל תרגילי השיעור</b><span class="d">כל שאלות המצגת, לעבודה ב-Excel בלי המצגת. גיליון ״ללא פתרון״ עם תבנית לכל שאלה, וגיליון ״עם פתרון״.</span></span></a>
</div></div>
<div class="grp"><h5>2. אחרי השיעור, לחזרה</h5><div class="links">
<a class="lk s" href="lectures/lecture-{k}/summary.pdf"><span class="e">📄</span><span><b>סיכום השיעור (PDF)</b><span class="d">כל תוכן המצגת במסמך אחד: הגדרות, השאלות והפתרון שלהן בגיליון, ומילון מושגים.</span></span></a>
</div></div>
<div class="grp"><h5>3. תרגילי בית</h5><div class="links">
<a class="lk p" href="lectures/lecture-{k}/exercises-{k}.pdf" target="_blank" rel="noopener"><span class="e">📝</span><span><b>תרגילי הבית (PDF)</b><span class="d">{L['hw']}. רק התרגילים של השיעור הזה.</span></span></a>
<a class="lk r" href="lectures/lecture-{k}/solutions-{k}.pdf" target="_blank" rel="noopener"><span class="e">✅</span><span><b>פתרונות תרגילי הבית (PDF)</b><span class="d">פרק {n(k)} בחוברת הפתרונות, באותו מספור, שלב אחר שלב. פותחים רק אחרי שפותרים.</span></span></a>
<a class="lk x" href="lectures/lecture-{k}/solutions-{k}.xlsx" download><span class="e">📊</span><span><b>פתרונות תרגילי הבית (Excel)</b><span class="d">אותם פתרונות בנוסחאות חיות.</span></span></a>
</div></div>
</div>
</div>
<div class="todo"><h4>📝 מה עושים בשיעור {n(k)}</h4><ol>
<li><b>בשיעור:</b> עובדים במצגת. מי שמעדיף לעבוד ב-Excel עובד באקסל תרגילי השיעור, שבו אותן שאלות.</li>
<li><b>תרגילי בית:</b> {L['hw']}. {L['hwnote']}</li>
<li><b>בדיקה:</b> רק אחרי שפתרתם, בפתרונות תרגילי הבית.</li>
</ol></div>
</article>
'''


cards = ''.join(card(L) for L in LESSONS)
src = open(os.path.join(H, '..', '..', 'finance-for-managers', 'index.html'), encoding='utf8').read()
css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
css += '''
.rec{margin-top:18px}
.rec h4{font-size:18px;margin-bottom:10px;color:var(--navy2)}
.recbox{position:relative;aspect-ratio:16/9;border-radius:16px;overflow:hidden;background:#0c1426;box-shadow:0 10px 26px rgba(22,33,58,.18);border:3px solid var(--navy2)}
.recbox iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.rec a.yt{display:inline-block;margin-top:8px;font-weight:700;font-size:15px;color:var(--navy2);text-decoration:underline}
.cgrid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
.cnote{font-size:15px;color:var(--mut);margin-top:8px}
.grp{margin-bottom:14px}.grp h5{font-size:15.5px;font-weight:800;color:var(--navy2);margin:0 0 8px}
@media (max-width:760px){.cgrid{grid-template-columns:1fr}}
.contact{margin-top:14px;background:#fff7e0;border:2px solid #f0b429;border-radius:18px;padding:16px 24px;display:flex;gap:16px;align-items:center}
.contact .ic{font-size:34px;flex:none}
.contact h2{font-size:20px;font-weight:800;line-height:1.3;color:var(--navy2)}
.contact h2 a{direction:ltr;unicode-bidi:isolate;display:inline-block;text-decoration:underline;overflow-wrap:anywhere}
.contact p{font-size:16.5px;line-height:1.45;margin-top:3px;color:#4a4130}
@media (max-width:760px){.contact{padding:14px 16px}.contact .ic{display:none}.contact h2{font-size:18px}}
.live{margin-top:-26px;position:relative;z-index:2;background:linear-gradient(120deg,#ff6a4d,#ff8f5a);color:#fff;border-radius:20px;padding:22px 28px;display:flex;gap:20px;align-items:center;box-shadow:0 14px 34px rgba(255,106,77,.35)}
.live .ic{font-size:44px;flex:none}
.live h2{font-size:26px;font-weight:800;line-height:1.2}
.live p{font-size:16.5px;margin-top:4px;line-height:1.4}
.live p a{text-decoration:underline;font-weight:700}
.live .go{flex:none;margin-right:auto;background:#fff;color:#c4421f;font-weight:800;font-size:19px;padding:14px 26px;border-radius:14px;text-align:center;transition:transform .15s}
.live .go:hover{transform:translateY(-2px)}
.live .go small{display:block;font-weight:600;font-size:13px;color:#5d6a86}
@media (max-width:760px){.live{flex-direction:column;align-items:stretch;padding:20px 18px;margin-top:-18px}.live .ic{display:none}.live .go{margin-right:0}}
.solutions{margin-top:18px;background:#fff;border-radius:20px;padding:24px 28px;display:flex;gap:22px;align-items:flex-start;box-shadow:0 2px 0 var(--line),0 10px 30px rgba(22,33,58,.07);border-right:8px solid #6d4df2}
.solutions .ic{font-size:44px;flex:none}
.solutions h3{font-size:22px;font-weight:800;line-height:1.25}
.solutions .tag{display:inline-block;background:#ece8ff;color:#4f33c9;border-radius:99px;padding:2px 14px;font-weight:700;font-size:14px;margin-bottom:6px}
.solutions p{font-size:16px;color:var(--ink2);margin-top:6px}
.solutions .warn{margin-top:12px;background:#fff7e0;border-right:5px solid #f0b429;border-radius:10px;padding:10px 14px;font-size:15px;color:#4a4130}
.solutions .btn2{flex:none;margin-right:auto;align-self:center;background:#6d4df2;color:#fff;font-weight:800;font-size:17px;padding:12px 22px;border-radius:14px;text-align:center;transition:transform .15s}
.solutions .btn2:hover{transform:translateY(-2px)}
.solutions .btn2 small{display:block;font-weight:500;font-size:13px;opacity:.9}
.lk.x .e{background:#e3f6ea}.lk.r .e{background:#fff0d2}
.todo{margin:0 30px 26px;background:#fff7e0;border:2px solid #f0b429;border-radius:18px;padding:18px 22px}
.todo h4{font-size:18px;color:var(--navy2);margin-bottom:8px}
.todo ol{padding-inline-start:22px;font-size:16px;line-height:1.6}
.ups{list-style:none;margin-top:18px;background:var(--card);border-radius:18px;box-shadow:0 2px 0 var(--line);overflow:hidden}
.ups li{display:flex;gap:14px;align-items:center;padding:11px 22px;border-bottom:1px solid var(--line);font-size:16.5px;font-weight:600}
.ups li:last-child{border:0}
.ups .un{flex:none;width:34px;height:34px;border-radius:10px;background:#eef0f6;color:var(--navy2);display:grid;place-items:center;font-weight:800}
.ups em{margin-right:auto;font-style:normal;color:var(--mut);font-size:14px;font-weight:500}
@media (max-width:760px){.solutions{flex-direction:column;padding:20px 18px}.solutions .btn2{margin-right:0;width:100%}.todo{margin:0 18px 22px;padding:14px 16px}.ups li{padding:10px 14px}}
'''
page = f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>מימון מתקדם לחשבונאים | אתר הקורס</title>
<meta name="description" content="אתר הקורס מימון מתקדם לחשבונאים, המכללה למנהל, מסלול חשבונאות: מצגות אינטראקטיביות עם גיליונות Excel חיים, סיכומים וקובצי תרגול.">
<link rel="stylesheet" href="assets/fonts.css">
<style>{css}</style>
</head>
<body>
<header class="hero"><div class="wrap">
<div class="kick"><span>המכללה למנהל · מסלול חשבונאות · סמסטר א׳ תשפ״ז</span></div>
<h1>מימון מתקדם לחשבונאים</h1>
<p class="lead">הקורס עוסק בתמחור אגרות חוב ומניות, במחיר ההון ובמבנה ההון של החברה, ובהחלטת חכירה מול רכישה. כל נושא נפתר ביד וב-Excel. לכל שיעור באתר: מצגת אינטראקטיבית עם גיליונות Excel חיים שבודקים את הנוסחה שלכם, סיכום מורחב, וקובץ תרגול עם קובץ פתרונות נפרד.</p>
<p class="meta">ד״ר שי צבאן · מרכזת הקורס: ד״ר גלי אינגבר</p>
</div></header>
<main class="wrap">
<section class="live" id="live">
<div class="ic">🎥</div>
<div><h2>המפגשים החיים ב-Zoom</h2><p>כל המפגשים של הקורס מתקיימים בקישור הזה.</p></div>
<a class="go" href="https://hdq-colman-ac.zoom.us/j/3160447945" target="_blank" rel="noopener">כניסה למפגש החי<small>Zoom</small></a>
</section>
<section class="contact" id="contact">
<div class="ic">✉️</div>
<div><h2>פניות לד״ר שי צבאן רק במייל: <a href="mailto:shay.tsaban@gmail.com">shay.tsaban@gmail.com</a></h2>
<p>תכתובות בכל ערוץ אחר לא ייענו. <b>חובה לרשום בכל תכתובת את שם המוסד ואת שם הקורס.</b></p></div>
</section>
<section class="block" id="course-files">
<h2 class="sec">קובצי הקורס</h2>
<div class="cgrid">
<a class="lk s" href="materials/syllabus.pdf" target="_blank" rel="noopener"><span class="e">📋</span><span><b>סילבוס הקורס (PDF)</b><span class="d">{n(11)} נושאים, לפי סדר קובצי השיעורים. מועדי המפגשים והרכב הציון יעודכנו.</span></span></a>
<a class="lk p" href="materials/afm-exercises.pdf" target="_blank" rel="noopener"><span class="e">📚</span><span><b>קובץ התרגילים המלא (PDF)</b><span class="d">בנוי לפי השיעורים כפי שנלמדו: פרק לכל שיעור, ובו בדיוק תרגילי הבית של אותו שיעור.</span></span></a>
<a class="lk r" href="materials/afm-solutions.pdf" target="_blank" rel="noopener"><span class="e">✅</span><span><b>חוברת הפתרונות המלאה (PDF)</b><span class="d">פתרון מפורט לכל תרגיל בקובץ התרגילים, באותו סדר ומספור.</span></span></a>
<a class="lk x" href="materials/afm-solutions.xlsx" download><span class="e">📊</span><span><b>פתרונות קובץ התרגילים (Excel)</b><span class="d">אותם פתרונות בנוסחאות חיות, גיליון לכל שיעור.</span></span></a>
</div>
<p class="cnote">בכרטיס של כל שיעור למטה מופיע הפרק של אותו שיעור כקובץ נפרד וקצר, עם הפתרונות שלו. הקובץ המלא מתעדכן אחרי כל שיעור, לפי ההספק בפועל.</p>
</section>
<section class="block">
<h2 class="sec">השיעורים</h2>
{cards}<h2 class="sec" style="margin-top:36px">השיעורים הבאים</h2>
<ul class="ups">{ups}</ul>
</section>
<footer>ד״ר שי צבאן · פניות רק במייל: <a href="mailto:shay.tsaban@gmail.com">shay.tsaban@gmail.com</a>, עם שם המוסד ושם הקורס</footer>
</main>
</body>
</html>
'''
assert '—' not in page and '־' not in page
open(os.path.join(H, '..', 'index.html'), 'w', encoding='utf8').write(page)
print('hub', len(page))
