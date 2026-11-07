# HSK Vokabeltrainer

Chinesisch-Vokabeln nach dem HSK-3.0-Lehrplan (Fassung 2025), mit deutschen Bedeutungen, Beispielsätzen,
Aussprache, Wiederholung nach Abständen und täglichen Lesetexten. Jede Person hat ein eigenes Konto.

App: https://kdeutschendorf-rgb.github.io/HSK-Vokabeltrainer/

- `app/` – die App (wird bei jedem Push auf `main` über `.github/workflows/pages.yml` veröffentlicht)
  - `index.html`, `words.json`, `sw.js` (offline), `manifest.json`, `icons/`, `vendor/supabase.js`
  - `lesetexte/<user_id>/` – Lesetexte pro Konto, `index.json` ist die Liste
- `daten/hsk30_2025_vocabulary.csv` – offizielle HSK-3.0-Wortliste (Quelle: github.com/ofou/hsk, MIT)
- `daten/de_hsk*.txt` – deutsche Bedeutungen und Beispielsätze (Nr|Deutsch|Beispiel|Beispiel Deutsch)
- `unterricht/unterricht_*.txt` – Wörter aus dem Einzelunterricht (Wort|Pinyin|Deutsch|Beispiel|Beispiel Deutsch)
- `werkzeuge/build_words.py` – baut `app/words.json` (braucht pypinyin)
- `werkzeuge/pruefe_lesetext.py`, `lesetext_index.py`, `stats_holen.sh` – für die Lesetexte
- `supabase_hsk.sql` – Tabellen `hsk_progress` und `hsk_stats`
