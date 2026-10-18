"""Raster images from the brand files in A-Rozum/plyn-brand (assets/): og.png (1200×630, the wordmark in Ink on Orange,
eyes and tuft white as the brand requires on orange) and apple-touch-icon.png (180×180, plyn-icon-orange.svg).
Run when the brand changes: python tools/images.py --brand <plyn-brand checkout>  (needs Playwright with Chromium)."""
import argparse, asyncio, re
from pathlib import Path
from playwright.async_api import async_playwright
ROOT = Path(__file__).resolve().parent.parent

async def shot(svg, w, h, out):
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": w, "height": h})
        await pg.set_content(f'<html><body style="margin:0;background:#E0662E">{svg}</body></html>'); await pg.screenshot(path=str(out)); await b.close()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--brand", required=True); a = ap.parse_args()
    word = (Path(a.brand) / "assets/plyn-wordmark.svg").read_text(encoding="utf-8")
    word = word.replace('fill="#E0662E"', 'fill="#FFFFFF"')
    word = re.sub(r'width="\d+" height="\d+"', 'width="1200" height="630" preserveAspectRatio="xMidYMid meet"', word, count=1)
    word = word.replace('viewBox="-2 0 177 103"', 'viewBox="-140 -75 453 238"')
    icon = (Path(a.brand) / "assets/plyn-icon-orange.svg").read_text(encoding="utf-8")
    icon = re.sub(r'width="\d+" height="\d+"', 'width="180" height="180"', icon, count=1)
    asyncio.run(shot(word, 1200, 630, ROOT / "og.png")); asyncio.run(shot(icon, 180, 180, ROOT / "apple-touch-icon.png"))
    print("og.png, apple-touch-icon.png")

if __name__ == "__main__":
    main()
