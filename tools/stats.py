"""Summary of the anonymous statistics in D1 plyn-stats. Needs CLOUDFLARE_API_TOKEN.  python tools/stats.py [days, default 7]
Visitors = page views of the language pages by non-bots; bounce = left within 10 s without a click or key."""
import json, os, sys, urllib.request
ACCOUNT, DB = "6d36b6422447adf3e863d95c4f0a4dfb", "bcacb88d-3f97-4f17-a517-0e61e4d44f79"
TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN") or sys.exit("CLOUDFLARE_API_TOKEN is not set")
days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
since = f"datetime('now', '-{days} days')"

def q(sql):
    req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/d1/database/{DB}/query", method="POST",
        data=json.dumps({"sql": sql}).encode(), headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["result"][0]["results"]

def table(title, sql):
    rows = q(sql); print(f"\n{title}")
    for r in rows: print("  " + "  ".join(str(v) for v in r.values()))
    if not rows: print("  –")

w = f"at >= {since}"
table(f"Last {days} days: views (people / bots)", f"SELECT sum(bot = 0), sum(bot = 1) FROM hits WHERE kind = 'view' AND {w}")
table("Views by language", f"SELECT lang, count(*) FROM hits WHERE kind = 'view' AND bot = 0 AND {w} GROUP BY lang ORDER BY 2 DESC")
table("Referring sites (search engines appear as their domain)", f"SELECT coalesce(referrer, '(direct)'), count(*) FROM hits WHERE kind = 'view' AND bot = 0 AND {w} GROUP BY 1 ORDER BY 2 DESC LIMIT 15")
table("Campaigns (utm)", f"SELECT utm, count(*) FROM hits WHERE kind = 'view' AND bot = 0 AND utm IS NOT NULL AND {w} GROUP BY 1 ORDER BY 2 DESC LIMIT 10")
table("Countries", f"SELECT coalesce(country, '?'), count(*) FROM hits WHERE kind = 'view' AND bot = 0 AND {w} GROUP BY 1 ORDER BY 2 DESC LIMIT 15")
table("Devices", f"SELECT device, count(*) FROM hits WHERE kind = 'view' AND bot = 0 AND {w} GROUP BY 1 ORDER BY 2 DESC")
table("Time on page: leaves, median-ish (avg of middle half) seconds, bounce %",
      f"WITH l AS (SELECT ms, interacted, row_number() OVER (ORDER BY ms) r, count(*) OVER () n FROM hits WHERE kind = 'leave' AND bot = 0 AND {w}) "
      f"SELECT count(*), round(avg(CASE WHEN r BETWEEN n / 4.0 AND n * 3 / 4.0 THEN ms END) / 1000.0, 1), round(100.0 * sum(interacted = 0 AND ms < 10000) / count(*), 1) FROM l")
table("Form: opened, sent, sent % of opened", f"SELECT sum(kind = 'open'), sum(kind = 'submit'), round(100.0 * sum(kind = 'submit') / max(1, sum(kind = 'open')), 1) FROM hits WHERE bot = 0 AND {w}")
