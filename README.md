# מימון מתקדם לחשבונאים

אתר הקורס: https://shaytsaban.github.io/advanced-finance-for-accountants/

- `index.html`: דף הבית.
- `lectures/lecture-1/`: מצגת וסיכום PDF.
- `materials/`: סילבוס, קובץ תרגול וקובץ פתרונות לשיעור 1.
- `_build/`: מקורות הבנייה.
  - `python3 build_deck.py 1`: המצגת. גיליונות ה-Excel החיים רצים על `xl.js`.
  - `python3 test_deck.py`: בדיקה בדפדפן ללא ממשק: גלישה, שקפים שחורגים, כיוון מספרים, וכל גיליון: דוחה תשובה שגויה, מקבל נוסחה נכונה בכמה כתיבים, ומחזיר משוב ייעודי לכל טעות מוגדרת.
  - `python3 build_xlsx.py 1`: קובץ התרגול וקובץ הפתרונות, מאותם גיליונות ובאותן כתובות. כל תשובה נבדקת שלוש פעמים: `fin.py`, המנוע של המצגת, וחישוב מחדש ב-LibreOffice.
  - `python3 tests/fin_ref.py`: פונקציות המימון של המנוע (PV, FV, PMT, NPER, RATE, NPV, IRR, XNPV, XIRR ועוד) מול LibreOffice.
  - `python3 build_summary.py 1`, `python3 build_syllabus.py`, `python3 build_hub.py`.
  - פונטי David נטענים מ-`../iit-build/fonts` ואינם נשמרים כאן.
