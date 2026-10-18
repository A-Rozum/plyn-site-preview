"""Copy the geometry of the mark and the wordmark from A-Rozum/plyn-brand into index.html and favicon.svg.

The page inlines both drawings (classes for theme and animation), and the favicon draws the line and eyes
heavier for small sizes, so only geometry is synced: viewBox, path d, circle cx/cy, and on the page the
stroke widths and eye radius. --check reports any difference and changes nothing.

Brand files come from --brand <dir with assets/> or, by default, from GitHub (GH_TOKEN for private access).
"""
import argparse, base64, json, os, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NUM = re.compile(r"-?\d+(?:\.\d+)?")

def brand_file(name, local):
    if local:
        return (Path(local) / "assets" / name).read_text(encoding="utf-8")
    req = urllib.request.Request(f"https://api.github.com/repos/A-Rozum/plyn-brand/contents/assets/{name}")
    if os.environ.get("GH_TOKEN"): req.add_header("Authorization", "token " + os.environ["GH_TOKEN"])
    return base64.b64decode(json.load(urllib.request.urlopen(req))["content"]).decode()

def shapes(svg):
    """Ordered drawing elements of an SVG as (tag, attrs-text, start, end)."""
    return [(m.group(1), m.group(2), m.start(), m.end()) for m in re.finditer(r"<(path|circle)\b([^>]*?)/?>(?:</\1>)?", svg)]

def attr(text, name):
    m = re.search(r'\s' + name + r'="([^"]*)"', text)
    return m.group(1) if m else None

def set_attr(text, name, value):
    if attr(text, name) is None: return text
    return re.sub(r'(\s' + name + r'=")[^"]*(")', lambda m: m.group(1) + value + m.group(2), text, count=1)

def nums(v): return [round(float(x), 3) for x in NUM.findall(v or "")]

def fmt_d(d):  # compact form used on the page: 151.20 → 151.2
    return NUM.sub(lambda m: ("%g" % float(m.group(0))), d)

def apply(svg_text, brand_svg, keys):
    """Return svg_text with geometry from brand_svg; keys: attributes to take from brand shapes."""
    out = svg_text
    vb = attr(brand_svg, "viewBox")
    if "viewBox" in keys and vb: out = re.sub(r'viewBox="[^"]*"', f'viewBox="{vb}"', out, count=1)
    mine, theirs = shapes(out), shapes(brand_svg)
    if [t for t, *_ in mine] != [t for t, *_ in theirs]:
        raise SystemExit(f"element order differs from the brand file: {[t for t,*_ in mine]} vs {[t for t,*_ in theirs]}")
    for (tag, a, s, e), (_, b, _, _) in reversed(list(zip(mine, theirs))):
        new = a
        for k in keys:
            if k == "viewBox": continue
            v = attr(b, k)
            if v is not None: new = set_attr(new, k, fmt_d(v) if k == "d" else v)
        out = out[:s] + out[s:e].replace(a, new, 1) + out[e:]
    return out

def same(a, b, keys):
    if "viewBox" in keys and nums(attr(a, "viewBox")) != nums(attr(b, "viewBox")): return False
    sa, sb = shapes(a), shapes(b)
    if [t for t, *_ in sa] != [t for t, *_ in sb]: return False
    for (_, x, *_), (_, y, *_) in zip(sa, sb):
        for k in keys:
            if k != "viewBox" and attr(y, k) is not None and nums(attr(x, k)) != nums(attr(y, k)): return False
    return True

def inline(html, cls):
    m = re.search(r'<svg class="' + cls + r'"[\s\S]*?</svg>', html)
    if not m: raise SystemExit(f"svg.{cls} not found in index.html")
    return m

PAGE = ["viewBox", "d", "cx", "cy", "r", "stroke-width"]
FAV = ["d", "cx", "cy"]  # favicon keeps its own viewBox crop and heavier small-size line and eyes

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); ap.add_argument("--brand")
    a = ap.parse_args()
    mark, word = brand_file("plyn-mark.svg", a.brand), brand_file("plyn-wordmark.svg", a.brand)
    html_p, fav_p = ROOT / "index.html", ROOT / "favicon.svg"
    html, fav = html_p.read_text(encoding="utf-8"), fav_p.read_text(encoding="utf-8")
    pairs = [("svg.wordmark in index.html", inline(html, "wordmark"), word, PAGE),
             ("svg.creature in index.html", inline(html, "creature"), mark, PAGE)]
    bad = [n for n, m, b, k in pairs if not same(m.group(0), b, k)]
    if not same(fav, mark, FAV): bad.append("favicon.svg")
    if a.check:
        if bad: print("Differs from plyn-brand: " + ", ".join(bad)); sys.exit(1)
        print("Mark, wordmark and favicon match plyn-brand."); return
    for n, m, b, k in sorted(pairs, key=lambda p: -p[1].start()):
        if n in bad: html = html[:m.start()] + apply(m.group(0), b, k) + html[m.end():]
    if "favicon.svg" in bad: fav = apply(fav, mark, FAV)
    if bad: html_p.write_text(html, encoding="utf-8"); fav_p.write_text(fav, encoding="utf-8")
    print("Synced: " + (", ".join(bad) if bad else "nothing changed"))

if __name__ == "__main__":
    main()
