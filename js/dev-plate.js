// Dev plate: window size in CSS pixels, zoom (devicePixelRatio), active regime, 1rem in pixels, load time.
// A prototyping aid; removed together with noindex.
(() => {
  const plate = document.createElement('div');
  plate.className = 'dev-plate'; plate.setAttribute('aria-hidden', 'true');
  document.body.append(plate);
  let load = '';
  const regime = () => matchMedia('(width <= 50em)').matches ? 'phone'
    : matchMedia('(width >= 125em)').matches ? 'large' : 'desktop';
  const update = () => {
    const rem = parseFloat(getComputedStyle(document.documentElement).fontSize);
    plate.textContent = `${innerWidth}×${innerHeight} · ${Math.round(devicePixelRatio * 100)}% · ${regime()} · 1rem=${rem.toFixed(2)}px${load}`;
  };
  addEventListener('resize', update, { passive: true });
  const done = () => setTimeout(() => {
    const n = performance.getEntriesByType('navigation')[0];
    if (n && n.loadEventEnd > 0) load = ` · ${((n.loadEventEnd - n.startTime) / 1000).toFixed(2)}s`;
    update();
  }, 0);
  if (document.readyState === 'complete') done(); else addEventListener('load', done, { once: true });
  update();
})();
