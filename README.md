# מימון מתקדם לחשבונאים

אתר הקורס: https://shaytsaban.github.io/advanced-finance-for-accountants/

- `index.html`: דף הבית.
- `lectures/lecture-N/` (שיעורים 1 עד 3): מצגת, סיכום PDF, ותרגילי הבית של השיעור עם הפתרונות (`exercises-N.pdf`, `solutions-N.pdf`, `solutions-N.xlsx`).
- `materials/`: סילבוס, קובץ התרגילים המלא וחוברת הפתרונות (PDF ו-Excel), ואקסל תרגילי השיעור (`lesson-N-appendix.xlsx`).
- קובץ התרגילים נפרס מחדש אחרי כל שיעור, לפי ההספק בפועל, כך שפרק N הוא בדיוק תרגילי הבית של שיעור N.
- `_build/`: מקורות הבנייה.
  - `python3 build_deck.py N`: המצגת. גיליונות ה-Excel החיים רצים על `xl.js`.
  - `python3 test_deck.py`: בדיקה בדפדפן ללא ממשק: גלישה, שקפים שחורגים, כיוון מספרים, וכל גיליון: דוחה תשובה שגויה, מקבל נוסחה נכונה בכמה כתיבים, ומחזיר משוב ייעודי לכל טעות מוגדרת.
  - `python3 build_booklet.py`: קובץ התרגילים, חוברת הפתרונות וקובץ הפתרונות ב-Excel, בפריסה לפי השיעורים כפי שנלמדו (`booklet_plan.py`): פרק N הוא בדיוק תרגילי הבית של שיעור N, במספור N.1, N.2. המקור ב-`src/`. לכל שיעור נגזר הפרק שלו כקובץ נפרד. אחרי כל שיעור מעדכנים את `booklet_plan.py` ובונים מחדש.
  - `python3 build_appendix.py N`: אקסל תרגילי השיעור, שני גיליונות (ללא פתרון ועם פתרון).
  - `python3 build_xlsx.py N`: בדיקה בלבד (לא מתפרסם): כל תשובה נבדקת שלוש פעמים, `fin.py`, המנוע של המצגת, וחישוב מחדש ב-LibreOffice.
  - `python3 tests/fin_ref.py`: פונקציות המימון של המנוע (PV, FV, PMT, NPER, RATE, NPV, IRR, XNPV, XIRR ועוד) מול LibreOffice.
  - `python3 build_summary.py N`, `python3 build_syllabus.py`, `python3 build_hub.py`.
  - פונטי David נטענים מ-`../iit-build/fonts` ואינם נשמרים כאן.
