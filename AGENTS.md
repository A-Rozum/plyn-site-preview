# plyn-site-preview

Landing page for Plyń, one page per language at plyn.one/<code>/ (en, be, be-latn for Belarusian in Łacinka, pl, it, lt). index.html is the template; i18n.json holds the texts of every language; tools/build.py builds dist/<code>/index.html with the texts, lang, canonical and hreflang links (x-default plyn.one/). The Worker sends plyn.one/ to the visitor's chosen language (cookie plyn-lang set by the switcher, or ?lang=), else the first supported browser language, else English. css/ (core.css copied from A-Rozum/prastora at fa54c1e, themes/plyn.css with the brand colours, pages/landing.css), js/site.js (behaviour), favicon.svg, review/<code>.txt for translation review (generated from i18n.json by tools/review.py).

The mark, the wordmark and the favicon are copies of files in A-Rozum/plyn-brand (the only source). The page inlines them so the creature can blink and wave and the line can follow the theme.

## Hosting: plyn.one on Cloudflare

Decided by the owner (Andrey Rozum): Cloudflare hosts the page and handles the beta form; plyn.one stays registered at Porkbun with Cloudflare nameservers. The Cloudflare API token and Porkbun API keys are in the owner's preferences; mask them in any output.

- Deploy: `CLOUDFLARE_API_TOKEN=… GH_TOKEN=… python tools/deploy.py` from this environment (GitHub Actions minutes are out until about 1 November). It sets the house dash in i18n.json, index.html, js/site.js and the Worker (spaced en dash, `tools/typography.py`), syncs the drawings from plyn-brand (`tools/sync_brand.py`, then `--check`), rebuilds review/ from I18N (`tools/review.py`, then `--check`), builds and uploads dist/ as static assets and worker/worker.js as Worker `plyn-site` on plyn.one and www.plyn.one (www redirects to the apex). IDs of the account, zone and database are at the top of the script.
- Beta form: POST /api/beta to the same Worker. Stored in D1 `plyn-beta` (EU jurisdiction, schema in worker/schema.sql): email (key), note, language, time. Silent protection: invisible Turnstile (sitekey in index.html, secret only as the Worker secret TURNSTILE_SECRET; a deploy keeps it), hidden honeypot field `website`, 5 requests per minute per IP. Each sign-up is mailed from noreply@beta.plyn.one to plyn.one@proton.me through Email Routing on the subdomain beta.plyn.one (beta-related mail comes from it; the future beta can live there too).
- Read sign-ups: D1 query API, `SELECT * FROM signups ORDER BY created_at`.

## Current task: finish the move

Done on 2026-10-18: zone added (Free plan), nameservers switched at Porkbun, Worker deployed, D1, Turnstile and rate limit in place, data notice names Cloudflare in all languages, demo line replaced by sending/success/error messages, drawing and review sync run on each deploy. Porkbun had only its parking records (ALIAS and wildcard CNAME to pixie.porkbun.com), no email forwarding and no DNSSEC, so no records were carried over.

Then the zone became active the same day: Email Routing and DNSSEC are on (DS record at Porkbun), https://plyn.one serves the page, and the owner's test sign-up arrived in D1 and by mail (test row deleted).

Remaining:
1. Project mail: being decided with the owner (agents first: incoming mail to a Worker and storage, important items forwarded to people; sending to anyone needs the Workers Paid plan). After the next real sign-up confirms mail from noreply@beta.plyn.one, remove Email Routing from notify.plyn.one.
2. Remove noindex only when the owner says the page is public; remove the dev plate (css/dev/plate.css, js/dev-plate.js and their two tags) at the same time.

Already on the page: browser language with English fallback, system theme with a remembered choice, rounded system font, controller Andrey Rozum with contact Plyn.one@proton.me.
The eyebrow states the start year; the footer shows 2026 or 2026–<current year>.
Later: per-language wordplay instead of a translated "learning to wave".
