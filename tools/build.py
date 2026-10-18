"""Build the language pages: dist/<code>/index.html for every language in i18n.json, from the template index.html.
Elements marked data-i18n get their text, data-i18n-ph a placeholder, data-i18n-aria an aria-label; the beta-form
messages go to data-* on #notice; each page links its language versions (hreflang, x-default = https://plyn.one/).
Static files are copied beside the pages. Run: python tools/build.py (tools/deploy.py runs it)."""
import html, json, re, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SITE = "https://plyn.one"
TAG = {"be-latn": "be-Latn"}  # BCP 47 tag where it differs from the path code
STATIC = ["favicon.svg", "css", "js"]

def page(tpl, code, t, codes):
    e = lambda v: html.escape(v, quote=False)
    a = lambda v: html.escape(v, quote=True)
    out = re.sub(r'(<(\w+)\b[^>]*\bdata-i18n="(\w+)"[^>]*>)(.*?)(</\2>)', lambda m: m.group(1) + e(t[m.group(3)]) + m.group(5), tpl, flags=re.S)
    out = re.sub(r'(<[^>]*\bdata-i18n-ph="(\w+)"[^>]*?)\bplaceholder="[^"]*"', lambda m: m.group(1) + f'placeholder="{a(t[m.group(2)])}"', out)
    out = re.sub(r'\bplaceholder="[^"]*"([^>]*\bdata-i18n-ph="(\w+)")', lambda m: f'placeholder="{a(t[m.group(2)])}"' + m.group(1), out)
    out = re.sub(r'(<[^>]*\bdata-i18n-aria="(\w+)")', lambda m: m.group(1) + f' aria-label="{a(t[m.group(2)])}"', out)
    out = re.sub(r'(data-i18n-aria="\w+" aria-label="[^"]*") aria-label="[^"]*"', r"\1", out)
    for k in ("sending", "ok", "err"):
        out = re.sub(f'data-{k}="[^"]*"', f'data-{k}="{a(t[k])}"', out, count=1)
    out = out.replace('<html lang="en">', f'<html lang="{TAG.get(code, code)}">', 1)
    out = re.sub(r"<title>.*?</title>", f"<title>{e(t['title'])}</title>", out, count=1)
    out = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + a(t["desc"]), out, count=1)
    out = out.replace(f'<option value="{code}" ', f'<option value="{code}" selected ', 1)
    links = [f'<link rel="canonical" href="{SITE}/{code}/">'] + [f'<link rel="alternate" hreflang="{TAG.get(c, c)}" href="{SITE}/{c}/">' for c in codes] + [f'<link rel="alternate" hreflang="x-default" href="{SITE}/">']
    return out.replace("<!--alternates-->", "".join(links), 1)

def main():
    texts = json.loads((ROOT / "i18n.json").read_text(encoding="utf-8"))
    tpl = (ROOT / "index.html").read_text(encoding="utf-8")
    shutil.rmtree(DIST, ignore_errors=True)
    for code, t in texts.items():
        (DIST / code).mkdir(parents=True)
        (DIST / code / "index.html").write_text(page(tpl, code, t, list(texts)), encoding="utf-8")
    for s in STATIC:
        src = ROOT / s
        shutil.copytree(src, DIST / s) if src.is_dir() else shutil.copy(src, DIST / s)
    print("Built: " + ", ".join(f"/{c}/" for c in texts))

if __name__ == "__main__":
    main()
