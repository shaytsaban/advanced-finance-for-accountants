# מימון מתקדם לחשבונאים

אתר הקורס: https://shaytsaban.github.io/advanced-finance-for-accountants/

- `index.html`: דף הבית.
- `lectures/lecture-N/` (שיעורים 1 עד 3): מצגת, סיכום PDF, ותרגילי הבית של השיעור עם הפתרונות (`exercises-N.pdf`, `solutions-N.pdf`, `solutions-N.xlsx`).
- `materials/`: סילבוס, קובץ התרגילים המלא וחוברת הפתרונות (PDF ו-Excel), ואקסל תרגילי השיעור (`lesson-N-appendix.xlsx`).
- שיעור 1 הסתיים לפני אג״ח לשיעורין, ולכן הנושא פותח את שיעור 2. תרגילי הבית נחתכים מפרק 1 לפי מה שנלמד בכל שיעור.
- `_build/`: מקורות הבנייה.
  - `python3 build_deck.py N`: המצגת. גיליונות ה-Excel החיים רצים על `xl.js`.
  - `python3 test_deck.py`: בדיקה בדפדפן ללא ממשק: גלישה, שקפים שחורגים, כיוון מספרים, וכל גיליון: דוחה תשובה שגויה, מקבל נוסחה נכונה בכמה כתיבים, ומחזיר משוב ייעודי לכל טעות מוגדרת.
  - `python3 build_homework.py N`: תרגילי הבית של השיעור, תרגיל אחר תרגיל, מקובץ התרגילים, מחוברת הפתרונות ומקובץ הפתרונות ב-Excel (נבדק בחישוב מחדש ב-LibreOffice).
  - `python3 build_appendix.py N`: אקסל תרגילי השיעור, שני גיליונות (ללא פתרון ועם פתרון).
  - `python3 build_xlsx.py N`: בדיקה בלבד (לא מתפרסם): כל תשובה נבדקת שלוש פעמים, `fin.py`, המנוע של המצגת, וחישוב מחדש ב-LibreOffice.
  - `python3 tests/fin_ref.py`: פונקציות המימון של המנוע (PV, FV, PMT, NPER, RATE, NPV, IRR, XNPV, XIRR ועוד) מול LibreOffice.
  - `python3 build_summary.py N`, `python3 build_syllabus.py`, `python3 build_hub.py`.
  - פונטי David נטענים מ-`../iit-build/fonts` ואינם נשמרים כאן.
