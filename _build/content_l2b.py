# Lesson 2, part 3: value along the life of a bond. Shay, 2026-11-10: lesson 2 reached question 3, sections a and b (slide 20).
# The rest of the part (sections c and d, question 4, question 2, before a payment, a bond traded between dates) is lesson 3.
_h = 1.0609 ** 0.5 - 1
assert round(_fin.NPV(_h, 4, 24, 3.2, 23.2, 2.4, 22.4, 1.6, 21.6, 0.8, 20.8), 4) == 105.3195
assert round(_fin.NPV(_h, 24, 3.2, 23.2, 2.4, 22.4, 1.6, 21.6, 0.8, 20.8) * 1.0609 ** 0.25, 4) == 106.0347

# ================================================================ part 3
opener(3, 'שווי לאורך חיי האג״ח', 'שאלת החלק: כמה שווה האג״ח ביום שאינו יום ההנפקה?',
       ['שלושה רגעים: מיד אחרי תשלום, רגע לפני תשלום, ובין שני מועדים', 'לאיזה מועד NPV מחזיר את הערך, ולמה', 'שאלה 3 מקובץ השיעור: ביום ההנפקה, מיד אחרי קופון ובין מועדים'], 40)

S('s-life', 'שלושה רגעים בחיי האג״ח', 'הגדרות מקדימות: שווי ביום שאינו יום ההנפקה',
  '<div class="row eq2 top">'
  + DEF('מיד אחרי תשלום', 'התשלום של היום כבר שולם, ולכן אינו בשווי. השווי הוא ההיוון של התזרימים שעוד נותרו.', 'אג״ח עם 3 תשלומים של 110 שנותרו, ב-10% לתקופה: ' + XL('=NPV(10%,110,110,110)') + ' נותן 273.55.', n=1)
  + DEF('רגע לפני תשלום', 'התשלום של היום עוד לא שולם, ולכן הוא חלק מהשווי. השווי הוא השווי מיד אחרי התשלום, ועוד התשלום עצמו.', 'אותה אג״ח, רגע לפני תשלום של 110: ' + XL('=273.55+110') + ' נותן 383.55.', n=2)
  + DEF('בין שני מועדי תשלום', 'NPV מחזיר את השווי למועד התשלום האחרון שכבר עבר. משם דוחפים קדימה, לפי מספר החודשים שעברו.', 'NPV נותן 100 ליום התשלום האחרון, ועברו 3 חודשים, בתשואה שנתית 8.16%: ' + XL('=100*(1+8.16%)^(3/12)') + ' נותן 101.98.', n=3)
  + '</div>'
  ,
  kick=f'חלק {CUR[0]} · הגדרות מקדימות')

# the principle before the first question on value along the bond's life: where NPV lands, and how to move from there.
# Shay, 2026-11-10: a clearer chart. Full width, cash flows as bars, the jump back drawn as one bold arc, the landing point ringed.
def _life_chart():
    """Five semiannual payments, spaced wide. Each step has its own lane: the jump back under the axis, the step forward above it."""
    W, H = 1160, 430
    X = lambda t: 100 + t * 200
    y0 = 236
    cf = {1: 5, 2: 5, 3: 5, 4: 5, 5: 105}
    hgt = lambda v: 40 if v < 50 else 100
    p = ['<defs><linearGradient id="lg-cf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2bc4b4"/><stop offset="1" stop-color="#0f9d90"/></linearGradient>'
         '<linearGradient id="lg-pd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3e6ee"/><stop offset="1" stop-color="#c9ced9"/></linearGradient></defs>']
    p.append(f'<rect x="20" y="{y0 - 2}" width="{W - 40}" height="4" rx="2" fill="#1b2d55"/><polygon points="{W - 8},{y0} {W - 24},{y0 - 8} {W - 24},{y0 + 8}" fill="#1b2d55"/>')
    for t in range(6):
        p.append(f'<circle cx="{X(t)}" cy="{y0}" r="6" fill="#fff" stroke="#1b2d55" stroke-width="2.5"/>' + T(X(t) - 26, y0 + 28, t, 19, '#1b2d55', 700))
    p.append(T(X(0), y0 + 52, 'תקופה', 17, '#5d6a86', 600))
    bars = ''
    for t, v in cf.items():
        h = hgt(v)
        bars += f'<rect class="bar" x="{X(t) - 30}" y="{y0 - 8 - h}" width="60" height="{h}" rx="9" fill="url(#lg-cf)"/>' + T(X(t), y0 - 18 - h, f'CF{t}', 19, '#0b6f66', 800)
    p.append(GS(1, bars, 'grow'))
    # step 2: payments 1 and 2 are gone; the range starts at 3; NPV goes back one period, from 3 to 2, under the axis
    gone = ''.join(f'<rect x="{X(t) - 31}" y="{y0 - 9 - hgt(cf[t])}" width="62" height="{hgt(cf[t]) + 2}" rx="9" fill="url(#lg-pd)"/>'
                   f'<path d="M{X(t) - 15} {y0 - 40} L{X(t) + 15} {y0 - 16} M{X(t) + 15} {y0 - 40} L{X(t) - 15} {y0 - 16}" stroke="#e0454f" stroke-width="4.5" stroke-linecap="round"/>' for t in (1, 2))
    p.append(GS(2, gone + T((X(1) + X(2)) / 2, y0 - 66, 'כבר שולמו', 19, '#c22f3a', 800), 'pop'))
    p.append(GS(2, f'<path d="M{X(3) - 36} 64 V48 H{X(5) + 36} V64" fill="none" stroke="#1b2d55" stroke-width="3" pathLength="1"/>'
                   + BADGE((X(3) + X(5)) / 2, 38, 'הטווח של NPV: מהתשלום הבא ועד הסוף', '#1b2d55', fs=18), 'draw', .15))
    p.append(GS(2, ARW(X(3) - 8, y0 + 14, X(2) + 8, y0 + 14, '#ff6a4d', 5, curve=62) + T((X(2) + X(3)) / 2, y0 + 82, 'תקופה אחת אחורה', 19, '#c4421f', 800)
                   + f'<circle class="ring" cx="{X(2)}" cy="{y0}" r="18" fill="none" stroke="#ff6a4d" stroke-width="4"/>' + BADGE(X(2), y0 + 128, 'שווי מיד אחרי תשלום 2', '#ff6a4d', fs=17), 'draw', .4))
    # step 3: right before payment 3, one period forward, above the axis
    p.append(GS(3, ARW(X(2) + 36, y0 - 56, X(3) - 36, y0 - 56, '#6d4df2', 4.5, curve=-46) + T((X(2) + X(3)) / 2, y0 - 104, '×(1+r)', 21, '#6d4df2', 800)
                   + f'<circle class="ring" cx="{X(3)}" cy="{y0}" r="18" fill="none" stroke="#6d4df2" stroke-width="4"/>' + BADGE(X(3) + 70, y0 + 128, 'רגע לפני תשלום 3', '#6d4df2', fs=17), 'draw'))
    # step 4: today, two months after payment 2
    xt = X(2) + 200 * 2 / 6
    p.append(GS(4, f'<circle class="ring" cx="{xt:.1f}" cy="{y0}" r="12" fill="#e8960c" stroke="#fff" stroke-width="3"/>'
                   + f'<line x1="{xt:.1f}" y1="{y0 + 14}" x2="{xt:.1f}" y2="{y0 + 160}" stroke="#e8960c" stroke-width="2.5" stroke-dasharray="6 5"/>'
                   + BADGE(xt, y0 + 178, 'היום', '#a86703', fs=17) + T(xt + 44, y0 + 184, '×(1+r)^(2/12)', 20, '#a86703', 800, 'start'), 'draw'))
    return DIAG(''.join(p), W, H, 'לאיזה מועד NPV מחזיר ערך, ואיך עוברים ממנו לכל רגע אחר')

_LIFE_STEPS = ['<b>הלוח.</b> אג״ח עם חמישה תשלומים חצי שנתיים, CF1 עד CF5. הלוח זהה ללוח של יום ההנפקה.',
               '<b>מיד אחרי תשלום 2.</b> CF1 ו-CF2 כבר שולמו. NPV על CF3 עד CF5 חוזר תקופה אחת אחורה, לתקופה 2.',
               '<b>רגע לפני תשלום 3.</b> CF3 עוד מגיע למחזיק: את השווי של תקופה 2 כופלים ב-' + XL('(1+r)') + ', כאשר r התשואה לתקופה.',
               '<b>היום, חודשיים אחרי תשלום 2.</b> את אותו NPV דוחפים קדימה חודשיים: כופלים ב-' + XL('(1+r)^(2/12)') + ', כאשר r התשואה השנתית.']
S('s-life-tl', 'העיקרון: לאן NPV חוזר', 'העיקרון לפני הגיליון: NPV חוזר תקופה אחת לפני התזרים הראשון',
  '<div class="card diagw">' + _life_chart() + '</div><div class="lsteps">' + ''.join(ST(i + 1, TX(x), cls='lstep') for i, x in enumerate(_LIFE_STEPS)) + '</div>',
  kick=f'חלק {CUR[0]} · העיקרון')

# ---------------------------------------------------------------- question 3 of the lesson 2 file: Catalina
Q3 = ['חברת ״קטלינה״ הנפיקה ב-1.1.2021 אג״ח שערכה הנקוב 100 ש״ח. אגרת החוב תיפדה ב-5 תשלומים שנתיים שווים. הריבית הנקובה השנתית היא 8%, והיא משולמת פעמיים בשנה. שיעור התשואה לפדיון הוא 6.09% לשנה, והוא אינו משתנה.',
      '<b>נדרש:</b> א. מחיר האג״ח ביום ההנפקה. ב. המחיר בחלוף 6 חודשים, ובחלוף 9 חודשים מיום ההנפקה.']
_dates = ['1.1.21', '30.6.21', '31.12.21', '30.6.22', '31.12.22', '30.6.23', '31.12.23', '30.6.24', '31.12.24', '30.6.25', '31.12.25']
_d = {'A76': 'ערך נקוב', 'D76': 100, 'A77': 'ריבית נקובה שנתית', 'C77': 'Rc_year', 'D77': 0.08, 'A78': 'ריבית נקובה חצי שנתית', 'C78': 'Rc_half',
      'A79': 'תשואה שנתית לפדיון', 'C79': 'rate_year', 'D79': 0.0609, 'A80': 'תשואה לחצי שנה', 'C80': 'rate_half',
      'A82': 'תקופה', 'B82': 'תאריך', 'C82': 'קופון', 'D82': 'ערך נקוב', 'E82': 'סך הכל', 'F82': 'יתרת ערך נקוב',
      **{f'A{83 + t}': t for t in range(11)}, **{f'B{83 + t}': _dates[t] for t in range(11)},
      'A96': 'א. מחיר בהנפקה', 'A98': 'ב. מחיר אחרי 6 חודשים', 'A99': 'ב. מחיר אחרי 9 חודשים'}
_s = {'D78': '=D77/2', 'D80': '=(1+D79)^(1/2)-1', 'F83': '=D76', **{f'D{r}': '=$D$76/5' for r in range(85, 94, 2)}}
for r in range(84, 94):
    _s[f'C{r}'] = f'=F{r - 1}*$D$78'; _s[f'E{r}'] = f'=C{r}+D{r}'; _s[f'F{r}'] = f'=F{r - 1}-D{r}'
_s.update({'D96': '=NPV(D80,E84:E93)', 'D98': '=NPV(D80,E85:E93)', 'D99': '=D98*(1+D79)^(3/12)'})
QX('q-5', '', 'שאלה 3 מקובץ השיעור: ״קטלינה״, ביום ההנפקה ואחריו', Q3,
   'באותן כתובות כמו בקובץ השיעור. הזינו את הנתונים ואת מספרי התקופות. D78 ו-D80: לחצי שנה. אחר כך לוח הסילוקין, ובסוף סעיפים א ו-ב, D96 עד D99.',
   _d, _s, [150, 62, 60, 70, 64, 92], [82], r0=76, maxh=300,
   fmt={'D77': 'pct0', 'D78': 'pct2', 'D79': 'pct2', 'D80': 'pct2', **{a: 'num2' for a in ('D96', 'D98', 'D99')}},
   hints=['פירעונות של ¤D¤76/5 בתקופות 2, 4, 6, 8 ו-10: בכל 31.12. הקופון: היתרה הקודמת כפול ¤D¤78.', 'אחרי 6 חודשים קופון 1 כבר שולם: הטווח מתחיל בתקופה 2. אחרי 9 חודשים: דוחפים את התוצאה 3 חודשים קדימה.'],
   remind='=NPV(D80,E85:E93)*(1+D79)^(3/12)', partial=['D78', 'D80', 'F83', 'C84'],
   traps={'D99': [('=D98*(1+D80)^(3/12)', 'דחפתם קדימה בתשואה לחצי שנה. בחזקה של חודשים חלקי 12 משתמשים בתשואה השנתית, D79.'), ('=D96*(1+D79)^(9/12)', 'דחפתם את שווי ההנפקה 9 חודשים, אבל בדרך שולם קופון 1. מתחילים מהשווי אחרי 6 חודשים, D98.')],
          **{f'C{r}': [('=$D$76*$D$78', 'קופון על הערך הנקוב המקורי. הקופון מחושב על היתרה: F של השורה הקודמת.')] for r in range(86, 94)}},
   steps=[dict(cells={'D78': '=D77/2', 'D80': '=(1+D79)^(1/2)-1'}, note='לחצי שנה: נקובה =D77/2 (4%), ותשואה =(1+D79)^(1/2)-1 (3%).', sel='D80'),
          dict(cells={'F83': '=D76', **{f'D{r}': '=$D$76/5' for r in range(85, 94, 2)}}, note='היתרה ההתחלתית =D76. חמישה פירעונות של =¤D¤76/5, כלומר 20, בכל 31.12.', sel='D85', sel2='D93'),
          dict(cells={**{f'C{r}': _s[f'C{r}'] for r in range(84, 94)}, **{f'F{r}': _s[f'F{r}'] for r in range(84, 94)}}, note='קופון על היתרה הקודמת, =F83*¤D¤78, ויתרה חדשה, =F83-D84. גוררים עד תקופה 10.', sel='C84', sel2='C93'),
          dict(cells={f'E{r}': _s[f'E{r}'] for r in range(84, 94)}, note='סך הכל: =C84+D84, וגוררים.', sel='E84', sel2='E93'),
          dict(cells={'D96': '=NPV(D80,E84:E93)'}, note='א. ביום ההנפקה: =NPV(D80,E84:E93), כלומר 105.32.'),
          dict(cells={'D98': '=NPV(D80,E85:E93)'}, note='ב. אחרי 6 חודשים, מיד אחרי קופון 1: הטווח מתחיל בתקופה 2. =NPV(D80,E85:E93), כלומר 104.48.'),
          dict(cells={'D99': '=D98*(1+D79)^(3/12)'}, note='אחרי 9 חודשים: מהשווי ב-30.6.21 דוחפים 3 חודשים קדימה, =D98*(1+D79)^(3/12), כלומר 106.03.')],
   note=[('tip', 'בכל סעיף שאלו: מהו התשלום הבא שעוד לא שולם? ממנו מתחיל הטווח של NPV.', 1)],
   done='א. 105.32. ב. 104.48 אחרי 6 חודשים, 106.03 אחרי 9 חודשים.', xtitle='שאלה 5: שאלה 3 בקובץ שיעור 2', kicktag='מסבירים יחד')

