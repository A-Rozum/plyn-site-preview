"""House typography for page texts: the dash is a spaced en dash (U+2013), as in "Plyń – a project".
Rewrites index.html, review/ and the Worker's messages; --check reports and changes nothing.
A long dash (U+2014, U+2015) becomes an en dash; a long dash written without spaces between words gets spaces."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FILES = ["index.html", "worker/worker.js", *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "review").glob("*.txt"))]
LONG = "\u2014\u2015"

def house(text):
    text = re.sub(r"(?<=\w)[" + LONG + r"](?=\w)", " \u2013 ", text)  # word—word → word – word
    return re.sub("[" + LONG + "]", "\u2013", text)

bad = []
for name in FILES:
    p = ROOT / name
    t = p.read_text(encoding="utf-8")
    n = house(t)
    if n != t:
        bad.append(name)
        if "--check" not in sys.argv: p.write_text(n, encoding="utf-8")
if "--check" in sys.argv and bad: print("Long dashes in: " + ", ".join(bad)); sys.exit(1)
print(("Dashes set in: " + ", ".join(bad)) if bad and "--check" not in sys.argv else "Dashes: house style")
