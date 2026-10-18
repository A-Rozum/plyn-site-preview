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
STATIC = ["favicon.svg", "apple-touch-icon.png", "og.png", "css", "js", "fonts"]
LOCALE = {"en": "en_GB", "be": "be_BY", "be-latn": "be_BY", "pl": "pl_PL", "it": "it_IT", "lt": "lt_LT"}

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
    meta = [f'<meta property="og:type" content="website"><meta property="og:site_name" content="Plyń">',
            f'<meta property="og:url" content="{SITE}/{code}/"><meta property="og:title" content="{a(t["title"])}"><meta property="og:description" content="{a(t["desc"])}">',
            f'<meta property="og:locale" content="{LOCALE[code]}"><meta property="og:image" content="{SITE}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Plyń">',
            '<meta name="twitter:card" content="summary_large_image">',
            '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@type": "WebSite", "name": "Plyń", "url": f"{SITE}/{code}/",
                "inLanguage": TAG.get(code, code), "description": t["desc"], "creator": {"@type": "Person", "name": "Andrey Rozum"}}, ensure_ascii=False) + "</script>"]
    links = meta + [f'<link rel="canonical" href="{SITE}/{code}/">'] + [f'<link rel="alternate" hreflang="{TAG.get(c, c)}" href="{SITE}/{c}/">' for c in codes] + [f'<link rel="alternate" hreflang="x-default" href="{SITE}/">']
    out = out.replace("<!--inscription-->", (ROOT / "inscription" / "tengwar.txt").read_text(encoding="utf-8"), 1)
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
    # rotating launch lines: each line shows for a time from its length plus a fixed jitter, so the rhythm is uneven
    import hashlib
    css = ["/* Built by tools/build.py: timing of the launch lines (.ticker) per language. */", "@layer page {"]
    for code, t in texts.items():
        lines = [t[k] for k in sorted(k for k in t if k.startswith("line"))]
        durs = []
        for s in lines:
            jitter = int(hashlib.sha1((code + s).encode()).hexdigest()[:4], 16) / 65535 * 1.6 - 0.8
            durs.append(round(min(10.0, max(5.0, 3.5 + 0.045 * len(s) + jitter)), 2))
        fade, total = 0.6, sum(durs) - 0.6 * (len(durs) - 1)
        start, name = 0.0, re.sub(r"[^a-z]", "", code)
        for i, dur in enumerate(durs, 1):
            p = lambda x: f"{max(0.0, min(100.0, x / total * 100)):.2f}%"
            if i == 1:
                frames = f"0% {{ opacity: 0; }} {p(fade)} {{ opacity: 1; }} {p(dur - fade)} {{ opacity: 1; }} {p(dur)} {{ opacity: 0; }} {p(total - fade)} {{ opacity: 0; }} 100% {{ opacity: 0; }}"
            else:
                frames = f"0% {{ opacity: 0; }} {p(start)} {{ opacity: 0; }} {p(start + fade)} {{ opacity: 1; }} {p(start + dur - fade)} {{ opacity: 1; }} {p(min(start + dur, total))} {{ opacity: 0; }} 100% {{ opacity: 0; }}"
            frames = frames.replace("{ opacity: 0; }", "{ opacity: 0; filter: blur(.25rem); }").replace("{ opacity: 1; }", "{ opacity: 1; filter: blur(0); }")  # lines develop
            css.append(f"  @keyframes tick-{name}-{i} {{ {frames} }}")
            css.append(f'  :root[lang="{TAG.get(code, code)}"] .ticker > :nth-child({i}) {{ animation: tick-{name}-{i} {total:.2f}s linear infinite; }}')
            start += dur - fade
    css.append("}")
    (DIST / "css" / "ticker.css").write_text("\n".join(css) + "\n", encoding="utf-8")
    # one stylesheet for the page, composed by Prastora's release tool from the modules in css/ (methods/css-delivery.md)
    plan = DIST / "styles-plan.json"
    plan.write_text(json.dumps({"format": 1, "bundles": {"/css/site.css": ["/css/core.css", "/css/themes/plyn.css", "/css/pages/landing.css", "/css/ticker.css"]}}), encoding="utf-8")
    import subprocess, sys
    r = subprocess.run([sys.executable, str(ROOT / "tools/styles.py"), str(plan), "--root", str(DIST)], capture_output=True, text=True)
    if r.returncode: raise SystemExit("styles.py: " + r.stderr)
    plan.unlink()
    alts = "".join(f'<xhtml:link rel="alternate" hreflang="{TAG.get(c, c)}" href="{SITE}/{c}/"/>' for c in texts) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/"/>'
    urls = "".join(f"<url><loc>{SITE}/{c}/</loc>{alts}</url>" for c in texts)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{urls}</urlset>\n', encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print("Built: " + ", ".join(f"/{c}/" for c in texts))

if __name__ == "__main__":
    main()
