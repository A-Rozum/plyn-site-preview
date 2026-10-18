"""Deploy plyn.one: sync and check the brand drawings and review files, upload the static assets and the Worker.

Needs CLOUDFLARE_API_TOKEN (and GH_TOKEN for reading plyn-brand). TURNSTILE_SECRET, if set, is stored as a Worker
secret; otherwise the stored secret is kept. Run from the repository root: python tools/deploy.py
"""
import base64, hashlib, json, mimetypes, os, subprocess, sys, urllib.request, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACCOUNT = "6d36b6422447adf3e863d95c4f0a4dfb"
ZONE = "0fc2b15c2ffa17c7cf6bff7d9f55a5d6"  # plyn.one
SCRIPT = "plyn-site"
D1 = "108f8d2b-a765-4ac4-b5e9-47bc8f01c375"  # plyn-beta, EU jurisdiction
NOTIFY_TO = "plyn.one@proton.me"
ASSETS = ["index.html", "favicon.svg", "css/core.css", "css/themes/plyn.css", "css/pages/landing.css", "css/dev/plate.css", "js/dev-plate.js", "js/i18n.js", "js/site.js"]
HOSTS = ["plyn.one", "www.plyn.one"]
TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN") or sys.exit("CLOUDFLARE_API_TOKEN is not set")
API = "https://api.cloudflare.com/client/v4"

def call(method, path, body=None, data=None, ctype=None, auth=None):
    h = {"Authorization": "Bearer " + (auth or TOKEN)}
    if body is not None: data, ctype = json.dumps(body).encode(), "application/json"
    if ctype: h["Content-Type"] = ctype
    req = urllib.request.Request(API + path, data=data, method=method, headers=h)
    try: out = json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e: out = json.loads(e.read() or b"{}")
    if not out.get("success", False): raise SystemExit(f"{method} {path}: {out.get('errors')}")
    return out.get("result")

def multipart(parts):
    b = "----plyn" + uuid.uuid4().hex
    out = b""
    for name, filename, ctype, content in parts:
        disp = f'form-data; name="{name}"' + (f'; filename="{filename}"' if filename else "")
        out += f"--{b}\r\nContent-Disposition: {disp}\r\nContent-Type: {ctype}\r\n\r\n".encode() + content + b"\r\n"
    return out + f"--{b}--\r\n".encode(), "multipart/form-data; boundary=" + b

def step(*cmd):
    r = subprocess.run([sys.executable, *cmd], cwd=ROOT)
    if r.returncode: sys.exit(r.returncode)

def main():
    step("tools/sync_brand.py"); step("tools/sync_brand.py", "--check")
    step("tools/typography.py"); step("tools/typography.py", "--check")
    step("tools/review.py"); step("tools/review.py", "--check")

    files = {"/" + n: (ROOT / n).read_bytes() for n in ASSETS}
    manifest = {p: {"hash": hashlib.sha256(c).hexdigest()[:32], "size": len(c)} for p, c in files.items()}
    sess = call("POST", f"/accounts/{ACCOUNT}/workers/scripts/{SCRIPT}/assets-upload-session", {"manifest": manifest})
    jwt = sess["jwt"]
    by_hash = {m["hash"]: p for p, m in manifest.items()}
    for bucket in sess.get("buckets") or []:
        parts = [(h, h, mimetypes.guess_type(by_hash[h])[0] or "application/octet-stream", base64.b64encode(files[by_hash[h]])) for h in bucket]
        data, ctype = multipart(parts)
        res = call("POST", f"/accounts/{ACCOUNT}/workers/assets/upload?base64=true", data=data, ctype=ctype, auth=sess["jwt"])
        if res and res.get("jwt"): jwt = res["jwt"]

    bindings = [
        {"type": "assets", "name": "ASSETS"},
        {"type": "d1", "name": "DB", "id": D1},
        {"type": "plain_text", "name": "NOTIFY_TO", "text": NOTIFY_TO},
        {"type": "ratelimit", "name": "RL", "namespace_id": "1001", "simple": {"limit": 5, "period": 60}},
    ]
    if os.environ.get("NO_MAIL") != "1":
        bindings.append({"type": "send_email", "name": "MAIL", "destination_address": NOTIFY_TO})
    meta = {"main_module": "worker.js", "compatibility_date": "2026-10-01", "bindings": bindings,
            "keep_bindings": ["secret_text"], "observability": {"enabled": True},
            "assets": {"jwt": jwt, "config": {"run_worker_first": True, "html_handling": "auto-trailing-slash", "not_found_handling": "none"}}}
    data, ctype = multipart([("metadata", None, "application/json", json.dumps(meta).encode()),
                             ("worker.js", "worker.js", "application/javascript+module", (ROOT / "worker" / "worker.js").read_bytes())])
    call("PUT", f"/accounts/{ACCOUNT}/workers/scripts/{SCRIPT}", data=data, ctype=ctype)
    if os.environ.get("TURNSTILE_SECRET"):
        call("PUT", f"/accounts/{ACCOUNT}/workers/scripts/{SCRIPT}/secrets", {"name": "TURNSTILE_SECRET", "text": os.environ["TURNSTILE_SECRET"], "type": "secret_text"})
    for host in HOSTS:
        call("PUT", f"/accounts/{ACCOUNT}/workers/domains", {"hostname": host, "service": SCRIPT, "zone_id": ZONE, "environment": "production"})
    print("Deployed " + SCRIPT + " to " + ", ".join(HOSTS))

if __name__ == "__main__":
    main()
