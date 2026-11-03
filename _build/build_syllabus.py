# Syllabus PDF. Run: python3 build_syllabus.py  ->  ../materials/syllabus.pdf
import html, os, shutil, subprocess, tempfile
H = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(H, '..', '..', 'iit-build', 'fonts')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
SITE = 'https://shaytsaban.github.io/advanced-finance-for-accountants/'
NOTE = 'ייתכנו שינויים קלים בתוכן הקורס ובסדר הנושאים במהלך הסמסטר, בהתאם להתקדמות בשיעורים. עדכונים יפורסמו באתר הקורס.'
TBD = '<span class="tbd">יעודכן</span>'
n = lambda s: f'<span class="n">{s}</span>'
# topics in the order of the lesson files; each row lists the questions those files work through.
# Amortizing bonds open lesson 2: lesson 1 ended before them (Shay, 2026-11-03).
L = [('1', 'אג״ח שקליות: שווי, ריבית נקובה ותשואה לפדיון', 'אגרת חוב: ערך נקוב, ריבית נקובה, קופון ומועד פדיון. שיעור תשואה לפדיון, היוון וערך נוכחי. שווי בטבלת תזרימים ובפונקציות NPV ו-PV. פרמיה, נכיון ופארי. קופון חצי שנתי ורבעוני והמרת תשואה בחזקה.'),
     ('2', 'אג״ח לשיעורין, ומחיר לפי תאריכים, לפני ואחרי קופון', 'אג״ח לשיעורין ולוח סילוקין: קופון על יתרת הערך הנקוב. שווי אג״ח מיד לפני ומיד אחרי תשלום, וביום שבין שני מועדי תשלום. אג״ח לשיעורין שנסחרת אחרי ההנפקה, עם התאמות ריבית ותקופה.'),
     ('3', 'חילוץ תשואה לפדיון ותשואה לתקופת החזקה', 'חילוץ התשואה לפדיון בפונקציות IRR ו-RATE, גם באג״ח לשיעורין ואחרי ההנפקה. תקופות חלקיות. תשואה לתקופת החזקה (HPR, Holding Period Return).'),
     ('4', 'מק״מ, אג״ח צמיתה ומח״מ', 'מלווה קצר מועד (מק״מ): מחיר ותשואה לפי ימים לפדיון. אג״ח צמיתה (קונסול). משך חיים ממוצע (מח״מ) ורגישות המחיר לריבית.'),
     ('5', 'אג״ח צמודות למדד ולדולר', 'ריאלי מול נומינלי. מחיר וחילוץ תשואה באג״ח צמודה למדד המחירים לצרכן ולדולר, עם התאמות זמן.'),
     ('6', 'תמחור מניות: מודל הדיבידנדים', 'מודל גורדון: מחיר מניה, תשואה נדרשת ושיעור צמיחה. תשואת דיבידנד ומכפיל רווח. דיבידנד קרוב, דיבידנדים משתנים וצמיחה משתנה.'),
     ('7', 'תמחור מניות: הזדמנויות צמיחה ומכפילים', 'הערך הנוכחי של הזדמנויות צמיחה (PVGO). מכפיל ענפי לתמחור הנפקה. דיבידנד רבעוני. שווי כלכלי מול מחיר שוק.'),
     ('8', 'מחיר ההון של החברה', 'מחיר ההון העצמי וביטא (β) מחברות דומות. מחיר הון ממוצע משוקלל (WACC, Weighted Average Cost of Capital), עם מסים ובלעדיהם. כדאיות פרויקטים.'),
     ('9-10', 'מינוף פיננסי: מודיליאני ומילר', 'מבנה ההון והסיכון לבעלים. מודל מודיליאני ומילר בעולם בלי מסים: ארביטראז׳ ומחיר ההון העצמי. בעולם עם מסים: מגן המס ושווי החברה.'),
     ('11', 'חכירה לעומת רכישה', 'השוואת תזרימים אחרי מס: פחת, מגן מס, אחזקה ושווי בסוף התקופה. דמי חכירה קריטיים ושיקולים שאינם כספיים.')]
rows = ''.join(f'<tr{" class=hi" if i == 0 else ""}><td class="c">{n(k)}</td><td><b>{t}</b></td><td>{w}</td></tr>' for i, (k, t, w) in enumerate(L))
body = f'''
<div class="hd"><div class="k">המכללה למנהל · מסלול חשבונאות · סמסטר א׳ תשפ״ז</div><h1 class="t">מימון מתקדם לחשבונאים</h1><div class="s">סילבוס הקורס</div></div>
<table class="meta"><tr><td>מרכזת הקורס</td><td>ד״ר גלי אינגבר</td></tr><tr><td>מרצה</td><td>ד״ר שי צבאן</td></tr><tr><td>מתרגלים</td><td>אין</td></tr>
<tr><td>קוד קורס</td><td>{TBD}</td></tr><tr><td>מועדי המפגשים</td><td>{TBD}</td></tr><tr><td>אתר הקורס</td><td><span class="url">{SITE}</span></td></tr></table>
<h3>תיאור הקורס</h3>
<p>הקורס עוסק בכלים הפיננסיים שחשבונאים פוגשים בעבודתם: תמחור אגרות חוב, שקליות וצמודות, ותשואתן; תמחור מניות לפי מודל הדיבידנדים ולפי מכפילים; מחיר ההון של החברה ומבנה ההון שלה; והחלטת חכירה מול רכישה. כל נושא נפתר גם ביד וגם ב-Excel, בטבלת תזרימים ובפונקציות המימון.</p>
<h3>תוצרי למידה: בסוף הקורס הסטודנטים ידעו</h3>
<ul><li>לחשב מחיר ותשואה לפדיון של אג״ח: שקלית, לשיעורין, צמודה, בין מועדי תשלום ומלווה קצר מועד.</li><li>לבנות טבלת תזרימים ב-Excel, ולהשתמש נכון בפונקציות NPV, PV, IRR ו-RATE ובמוסכמת הסימן.</li>
<li>להסביר פרמיה, נכיון ופארי, ואת הקשר בין תשואה, מחיר ומשך חיים ממוצע.</li><li>לתמחר מניה לפי מודל הדיבידנדים ולפי מכפיל, ולפרק את המחיר להזדמנויות צמיחה.</li>
<li>לחשב מחיר הון ממוצע משוקלל, ולהסביר את השפעת המינוף על מחיר ההון ועל שווי החברה לפי מודיליאני ומילר.</li><li>להשוות בין חכירה לרכישה על בסיס תזרימים אחרי מס.</li></ul>
<h3>נושאי המפגשים</h3>
<table class="plan"><thead><tr><th>שיעור</th><th>נושא</th><th>תכנים עיקריים</th></tr></thead><tbody>{rows}</tbody></table>
<div class="note">הסדר והתכנים לפי קובצי השיעורים של הקורס. {NOTE}</div>
<h3>שיטות הוראה</h3>
<p>הרצאות שבהן כל שאלה נפתרת בגיליון Excel, צעד אחר צעד. בכל שיעור מצגת אינטראקטיבית עם גיליונות Excel חיים: הסטודנטים כותבים נוסחה בתוך השקף ומקבלים משוב. לכל שיעור באתר: סיכום מורחב, קובץ תרגול ב-Excel וקובץ פתרונות נפרד.</p>
<h3>חומרי הקורס</h3>
<ul><li>קובצי האקסל של השיעורים, עם השאלות שנפתרות בכיתה.</li><li>קובץ התרגילים: לכל שיעור פרק, עם תרגילים בקושי עולה, תרגילים מאתגרים ותרגילים בסגנון בחינה.</li><li>דף הנוסחאות של הקורס.</li><li>בחינות לדוגמה.</li></ul>
<h3>הרכב הציון</h3>
<p>{TBD}. הבחינות לדוגמה של הקורס כוללות {n(20)} שאלות אמריקאיות, עם חמש תשובות לכל שאלה.</p>
<h3>יצירת קשר</h3>
<p>פניות לד״ר שי צבאן רק במייל: {n('shay.tsaban@gmail.com')}. תכתובות בכל ערוץ אחר לא ייענו. חובה לרשום בכל תכתובת את שם המוסד ואת שם הקורס.</p>'''
CSS = '''
@font-face{font-family:"David";src:url("david.ttf");font-weight:400}
@font-face{font-family:"David";src:url("davidbd.ttf");font-weight:700}
@page{size:A4;margin:16mm;@bottom-center{content:counter(page);font-family:"David";font-size:10pt;color:#5d6a86}}
:root{--ink:#16213a;--navy:#1b2d55;--coral:#ff6a4d;--mut:#5d6a86;--line:#d9d2c3}
*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html{direction:rtl}body{font-family:"David";font-size:11.8pt;line-height:1.34;color:var(--ink);margin:0}
.n{direction:ltr;unicode-bidi:isolate}
.hd{background:linear-gradient(160deg,#0f1b33 0%,#1b2d55 60%,#27447f 100%);color:#fff;border-radius:3mm;padding:6mm 8mm;margin-bottom:4mm}
.hd .k{color:#7fe3d6;font-weight:700;font-size:12pt}.hd h1.t{color:#fff;margin:1.5mm 0 1mm;font-size:24pt}.hd .s{color:#d6e0f7;font-size:13.5pt}
h3{font-size:13.4pt;color:var(--navy);margin:4mm 0 1.2mm;break-after:avoid;border-bottom:.5mm solid var(--coral);padding-bottom:.6mm}
p{margin:0 0 1.6mm}ul{margin:0 0 1.6mm;padding-right:6mm}li{margin-bottom:.5mm}
table{width:100%;border-collapse:collapse;font-size:10.8pt;margin:1.2mm 0 2mm}th{background:var(--navy);color:#fff;text-align:right;padding:1mm 2mm}td{padding:1mm 2mm;border-bottom:.25mm solid var(--line);vertical-align:top}tr{break-inside:avoid}
table.meta td:first-child{font-weight:700;width:30mm;color:var(--navy)}td.c{text-align:center;font-weight:700}td.r{white-space:nowrap}
tr.hi td{background:#fff0d2}.note{background:#eef2ff;border-right:1.2mm solid var(--navy);border-radius:1mm;padding:1.2mm 2.6mm;font-size:10.8pt}
.url{direction:ltr;unicode-bidi:isolate;font-family:Arial,sans-serif;font-size:10pt;color:var(--navy)}
.tbd{background:#fff0d2;border:.3mm dashed #a86703;border-radius:1mm;padding:0 2mm;font-weight:700;color:#7a4a00}
.lit{list-style:none;padding:0}.lit .n{display:block;text-align:left}
'''
page = f'<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8"><title>מימון מתקדם לחשבונאים | סילבוס</title><style>{CSS}</style></head><body>{body}</body></html>'
assert '—' not in page and '־' not in page
d = tempfile.mkdtemp(dir=os.environ.get('TMPDIR'))
for f in ('david.ttf', 'davidbd.ttf'): shutil.copy(os.path.join(FONTS, f), d)
open(os.path.join(d, 's.html'), 'w', encoding='utf8').write(page)
out = os.path.abspath(os.path.join(H, '..', 'materials', 'syllabus.pdf'))
subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox', f'--user-data-dir={d}/p', '--no-pdf-header-footer', '--virtual-time-budget=6000', f'--print-to-pdf={out}', 'file://' + d + '/s.html'], capture_output=True, timeout=120)
shutil.rmtree(d, True)
import fitz
D = fitz.open(out); print('pages', len(D), 'bytes', os.path.getsize(out), sorted({f[3].split('+')[-1] for p in D for f in p.get_fonts()}))
