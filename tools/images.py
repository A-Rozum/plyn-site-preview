"""Raster images from the brand files in A-Rozum/plyn-brand (assets/): og.png (1200×630, the mark large in the centre in Ink on Orange,
eyes and kreska white as the brand requires on orange – messengers such as WhatsApp crop the middle square and shrink it, where a wordmark blurs) and apple-touch-icon.png (180×180), icon-48.png and icon-192.png (plyn-icon-orange.svg; the PNG icons are what Google and
other services read as the site icon).
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
    word = (Path(a.brand) / "assets/plyn-mark.svg").read_text(encoding="utf-8")
    word = word.replace('fill="#E0662E"', 'fill="#FFFFFF"')
    word = re.sub(r'width="\d+" height="\d+"', 'width="1200" height="630" preserveAspectRatio="xMidYMid meet"', word, count=1)
    # frame the mark whatever its viewBox: 72% of the height, centred
    x, y, w, h = (float(v) for v in re.search(r'viewBox="([^"]*)"', word).group(1).split())
    H = h / 0.72; W = H * 1200 / 630
    word = re.sub(r'viewBox="[^"]*"', f'viewBox="{x + w / 2 - W / 2:.2f} {y + h / 2 - H / 2:.2f} {W:.2f} {H:.2f}"', word, count=1)
    icon = (Path(a.brand) / "assets/plyn-icon-orange.svg").read_text(encoding="utf-8")
    icon = re.sub(r'width="\d+" height="\d+"', 'width="180" height="180"', icon, count=1)
    asyncio.run(shot(word, 1200, 630, ROOT / "og.png"))
    for size, name in ((180, "apple-touch-icon.png"), (48, "icon-48.png"), (192, "icon-192.png")):
        asyncio.run(shot(re.sub(r'width="\d+" height="\d+"', f'width="{size}" height="{size}"', icon, count=1), size, size, ROOT / name))
    print("og.png, apple-touch-icon.png, icon-48.png, icon-192.png")

if __name__ == "__main__":
    main()
