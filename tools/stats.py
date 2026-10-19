"""Summary of the anonymous statistics in D1 plyn-stats. Needs CLOUDFLARE_API_TOKEN.  python tools/stats.py [days, default 7]
Visitors = page views of the language pages by non-bots; bounce = left within 10 s without a click or key."""
import json, os, sys, urllib.parse, urllib.request
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
table("Consent: allowed, declined, allowed %", f"SELECT sum(kind = 'consent-yes'), sum(kind = 'consent-no'), round(100.0 * sum(kind = 'consent-yes') / max(1, sum(kind IN ('consent-yes', 'consent-no'))), 1) FROM hits WHERE bot = 0 AND {w}")
table("Visitors who allowed it: unique, returning (seen on more than one day)", f"WITH v AS (SELECT vid, count(DISTINCT substr(at, 1, 10)) d FROM hits WHERE kind = 'view' AND bot = 0 AND vid IS NOT NULL AND {w} GROUP BY vid) SELECT count(*), sum(d > 1) FROM v")
table("Form: opened, sent, sent % of opened", f"SELECT sum(kind = 'open'), sum(kind = 'submit'), round(100.0 * sum(kind = 'submit') / max(1, sum(kind = 'open')), 1) FROM hits WHERE bot = 0 AND {w}")

# Search phrases. Bing: BING_WEBMASTER_KEY (API key of the agents' Microsoft account). Google: GOOGLE_SA_JSON, the path to
# the key of service account plyn-agent@plyn-agents (owner of the Search Console property sc-domain:plyn.one).
import datetime, time
SITE = "https://plyn.one/"

def get(url, data=None, headers={}):
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try: return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e: return {"error": f"{e.code} {e.read()[:200].decode(errors='replace')}"}

def show(title, rows):
    print(f"\n{title}")
    for r in rows: print("  " + "  ".join(str(v) for v in r))
    if not rows: print("  –")

if os.environ.get("BING_WEBMASTER_KEY"):
    out = get("https://ssl.bing.com/webmaster/api.svc/json/GetQueryStats?apikey=" + os.environ["BING_WEBMASTER_KEY"] + "&siteUrl=" + SITE)
    if "error" in out: show("Bing search phrases", [[out["error"]]])
    else:
        cut = (time.time() - days * 86400) * 1000
        rows = {}
        for r in out.get("d") or []:
            if int(r["Date"][6:-2].split("+")[0].split("-")[0] or 0) < cut: continue
            a = rows.setdefault(r["Query"], [0, 0]); a[0] += r["Impressions"]; a[1] += r["Clicks"]
        show("Bing search phrases: impressions, clicks", sorted([[q, *v] for q, v in rows.items()], key=lambda x: -x[1])[:20])
else: show("Bing search phrases", [["BING_WEBMASTER_KEY is not set"]])

if os.environ.get("GOOGLE_SA_JSON"):
    import jwt
    sa = json.load(open(os.environ["GOOGLE_SA_JSON"]))
    now = int(time.time())
    assertion = jwt.encode({"iss": sa["client_email"], "scope": "https://www.googleapis.com/auth/webmasters.readonly",
                            "aud": sa["token_uri"], "iat": now, "exp": now + 600}, sa["private_key"], algorithm="RS256")
    tok = get(sa["token_uri"], urllib.parse.urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion}).encode())["access_token"]
    end = datetime.date.today(); start = end - datetime.timedelta(days=days)
    out = get("https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Aplyn.one/searchAnalytics/query",
              json.dumps({"startDate": str(start), "endDate": str(end), "dimensions": ["query"], "rowLimit": 20}).encode(),
              {"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    if "error" in out: show("Google search phrases", [[str(out["error"])[:200]]])
    else: show("Google search phrases: impressions, clicks", [[r["keys"][0], r["impressions"], r["clicks"]] for r in out.get("rows", [])])
else: show("Google search phrases", [["GOOGLE_SA_JSON is not set"]])
