# plyn-site-preview

Landing page for Plyń. Single index.html (texts for all languages in the I18N object), favicon.svg, review/<lang>.txt for translation review (keep them in sync with I18N). Built with Prastora CSS.

The mark, the wordmark and the favicon are copies of files in A-Rozum/plyn-brand (the only source). The page inlines them so the creature can blink and wave and the line can follow the theme.

## Current task: move the page to plyn.one on Cloudflare

Decided by the owner (Andrey Rozum): Cloudflare hosts the page and handles the beta form; plyn.one stays registered at Porkbun. Cloudflare API token and Porkbun API keys are in the owner's preferences; mask them in any output. api.cloudflare.com, api.porkbun.com and porkbun.com are allowed in the network.

1. Add plyn.one to Cloudflare (Free plan). Copy every DNS record Porkbun currently has for plyn.one, including email forwarding, before switching nameservers. If DNSSEC is on at Porkbun, remove it first; enable it again from Cloudflare once the zone is active.
2. Switch plyn.one nameservers at Porkbun to the ones Cloudflare assigns, through the Porkbun API.
3. Serve the page from a Worker with static assets on plyn.one (www redirects to the apex). Deploy from this environment through the Cloudflare API; GitHub Actions is out of minutes until about 1 November.
4. Beta form: POST to the same Worker; store email, optional note, language and time in a D1 database. Silent bot protection only, no visible captcha: Turnstile in invisible mode, a hidden honeypot field, a per-IP rate limit. Notify Plyn.one@proton.me of each sign-up through Email Routing (the owner clicks the verification email).
5. Data notice: add Cloudflare as hosting provider processing the form, in all languages; replace the demo line and notice with real success and error messages.
6. Sync the inlined mark, wordmark and favicon from plyn-brand with a script plus a check that they match, run as part of deployment.
7. Remove noindex only when the owner says the page is public.

Already on the page: browser language with English fallback, system theme with a remembered choice, rounded system font, controller Andrey Rozum with contact Plyn.one@proton.me.
Later: year in the eyebrow set automatically; per-language wordplay instead of a translated "learning to wave".
