"""Write review/<lang>.txt from the I18N object in js/i18n.js (one file per language, key: text). --check fails if they differ."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
NAMES = {"en": "English", "be": "Беларуская", "bel": "Łacinka", "pl": "Polski", "it": "Italiano", "lt": "Lietuvių"}
s = (ROOT / "js" / "i18n.js").read_text(encoding="utf-8")
i = s.index("const I18N=") + len("const I18N=")
data, _ = json.JSONDecoder().raw_decode(s[i:])
bad = []
for code, texts in data.items():
    body = f"Plyń landing page – {NAMES[code]} ({code})\n\n" + "".join(f"{k}: {v}\n" for k, v in texts.items())
    p = ROOT / "review" / f"{code}.txt"
    if not p.exists() or p.read_text(encoding="utf-8") != body:
        bad.append(p.name)
        if "--check" not in sys.argv: p.write_text(body, encoding="utf-8")
if "--check" in sys.argv and bad: print("review/ out of sync with I18N: " + ", ".join(bad)); sys.exit(1)
print(("Updated: " + ", ".join(bad)) if bad and "--check" not in sys.argv else "review/ matches I18N")
