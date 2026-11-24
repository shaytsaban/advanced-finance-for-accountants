# The layout of the exercise booklet by lessons as they were actually taught (Shay, 2026-11-10: chapter N of the booklet must be
# exactly the homework of lesson N, renumbered N.1, N.2, ...). Keys are the numbers of the original booklet in src/: '1.3' is
# exercise 1.3, '1E1' is exam-style exercise 1 of chapter 1. When a lesson ends early, move keys between chapters here and rebuild.
RELAID = {
 1: dict(title='אג״ח שקליות: שווי, ריבית נקובה ותשואה לפדיון, פרמיה ונכיון, קופון חצי שנתי ורבעוני',
         groups=[('שווי אג״ח, פרמיה ונכיון', ['1.1', '1.2', '1.5', '1.8']), ('קופון חצי שנתי ורבעוני', ['1.4', '1.6', '1.9', '1.17', '1.18'])], exams=[]),
 2: dict(title='אג״ח לשיעורין, שווי מיד אחרי תשלום ושווי בין מועדי תשלום',
         groups=[('אג״ח לשיעורין: לוח סילוקין וקופון על היתרה', ['1.3', '1.7', '2.1', '2.3', '2.4', '1.10', '1.11', '2.6', '1.13', '2.9', '2.17']),
                 ('שווי מיד אחרי תשלום', ['1.14', '2.8']), ('שווי בין מועדי תשלום', ['1.12', '2.11', '1.15', '1.16', '2.15'])], exams=['1E1', '1E2']),
 3: dict(title='שווי רגע לפני תשלום, וחילוץ תשואה לפדיון, גם בין מועדי תשלום',
         groups=[('שווי רגע לפני תשלום', ['2.7', '2.13']), ('חילוץ תשואה לפדיון: IRR ו-RATE', ['2.2', '2.5', '2.10', '2.12']), ('חילוץ תשואה בין מועדי תשלום', ['2.14', '2.16'])], exams=['2E1', '2E2']),
 # Shay, 2026-11-24: lesson 4 covered complex yield questions, partial periods and HPR. It stopped at slide 19, before duration: 4.9 moved to lesson 5.
 4: dict(title='תרגילים מורכבים בחילוץ תשואה, תקופות חלקיות ותשואה לתקופת החזקה (HPR)',
         groups=[('חילוץ תשואה לפדיון: חזרה ותרגילים מורכבים', ['3.1', '3.2', '3.3', '3.4', '3.5', '3.6', '3.9', '3.11', '3.12', '3.19', '4.14']),
                 ('תקופות חלקיות ושורות 0', ['3.10', '3.13', '3.14', '3.15', '3.18', '4.13', '4.16', '4.18']),
                 ('תשואה לתקופת החזקה (HPR)', ['3.7', '3.8', '3.16', '3.17', '4.8', '4.11', '4.15', '4.19'])], exams=['3E1', '3E2', '4E2']),
 5: dict(title='מק״מ, אג״ח צמיתה, ומח״מ ורגישות המחיר לריבית',
         groups=[('מק״מ', ['4.1', '4.3', '4.4', '4.6']), ('אג״ח צמיתה', ['4.2', '4.5', '4.7', '4.17']), ('מח״מ: המשמעות, החישוב ורגישות המחיר לריבית', ['4.9', '4.10', '4.12'])], exams=['4E1']),
}
# the chapters after them keep their content and move one lesson forward: old label -> new label
SHIFT = [('5', '6'), ('5א', '6א'), ('6', '7'), ('7', '8'), ('9', '10')]

NEW = {}        # old key -> new label ('2.5', or 'בחינה 1' inside its chapter) ; CH[old key] -> new chapter
CH = {}
for c, P in RELAID.items():
    n = 0
    for _, items in P['groups']:
        for k in items:
            n += 1; NEW[k] = f'{c}.{n}'; CH[k] = c
    for j, k in enumerate(P['exams'], 1):
        NEW[k] = str(j); CH[k] = c
assert len(NEW) == sum(len(i) for P in RELAID.values() for _, i in P['groups']) + sum(len(P['exams']) for P in RELAID.values())


def EXN(old):
    """The new number of an exercise of the original booklet, for the decks: EXN('1.6') -> '1.6' or '2.3'."""
    return NEW[old]


def span(c, group=None):
    """'2.1 עד 2.11' for a whole chapter or one of its groups."""
    P = RELAID[c]; items = [k for g, it in P['groups'] for k in it if group is None or g == group]
    a, b = NEW[items[0]], NEW[items[-1]]
    return a if a == b else (f'{a} ו-{b}' if len(items) == 2 else f'{a} עד {b}')
