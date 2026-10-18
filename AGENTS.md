# plyn-site-preview

Landing page for Plyń. Single index.html (texts for all languages in the I18N object), favicon.svg, review/<lang>.txt for translation review (generated from I18N by tools/review.py). Built with Prastora CSS.

The mark, the wordmark and the favicon are copies of files in A-Rozum/plyn-brand (the only source). The page inlines them so the creature can blink and wave and the line can follow the theme.

## Hosting: plyn.one on Cloudflare

Decided by the owner (Andrey Rozum): Cloudflare hosts the page and handles the beta form; plyn.one stays registered at Porkbun with Cloudflare nameservers. The Cloudflare API token and Porkbun API keys are in the owner's preferences; mask them in any output.

- Deploy: `CLOUDFLARE_API_TOKEN=… GH_TOKEN=… python tools/deploy.py` from this environment (GitHub Actions minutes are out until about 1 November). It syncs the drawings from plyn-brand (`tools/sync_brand.py`, then `--check`), rebuilds review/ from I18N (`tools/review.py`, then `--check`), uploads index.html and favicon.svg as static assets and worker/worker.js as Worker `plyn-site` on plyn.one and www.plyn.one (www redirects to the apex). IDs of the account, zone and database are at the top of the script.
- Beta form: POST /api/beta to the same Worker. Stored in D1 `plyn-beta` (EU jurisdiction, schema in worker/schema.sql): email (key), note, language, time. Silent protection: invisible Turnstile (sitekey in index.html, secret only as the Worker secret TURNSTILE_SECRET; a deploy keeps it), hidden honeypot field `website`, 5 requests per minute per IP. Each sign-up is mailed from beta@plyn.one to plyn.one@proton.me through Email Routing.
- Read sign-ups: D1 query API, `SELECT * FROM signups ORDER BY created_at`.

## Current task: finish the move

Done on 2026-10-18: zone added (Free plan), nameservers switched at Porkbun, Worker deployed, D1, Turnstile and rate limit in place, data notice names Cloudflare in all languages, demo line replaced by sending/success/error messages, drawing and review sync run on each deploy. Porkbun had only its parking records (ALIAS and wildcard CNAME to pixie.porkbun.com), no email forwarding and no DNSSEC, so no records were carried over.

Then the zone became active the same day: Email Routing is on (plyn.one@proton.me verified), DNSSEC is on with the DS record at Porkbun, and https://plyn.one serves the page.

Remaining:
1. A real sign-up through the page (Turnstile cannot be passed from the agent environment, which also cannot reach plyn.one): check that its row is in D1 and the mail reached plyn.one@proton.me; delete the test row afterwards.
2. Remove noindex only when the owner says the page is public.

Already on the page: browser language with English fallback, system theme with a remembered choice, rounded system font, controller Andrey Rozum with contact Plyn.one@proton.me.
Later: year in the eyebrow set automatically; per-language wordplay instead of a translated "learning to wave".
