// plyn.one: static page from assets, www → apex, beta form at POST /api/beta.
import { EmailMessage } from "cloudflare:email";

const APEX = "plyn.one";
const LANGS = ["en", "be", "be-latn", "pl", "it", "lt"]; // path codes; be-latn is Belarusian in Łacinka
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "www." + APEX) {
      url.hostname = APEX;
      return Response.redirect(url.toString(), 301);
    }
    if (url.pathname === "/api/beta") {
      if (request.method !== "POST") return json({ ok: false, error: "method" }, 405);
      return beta(request, env);
    }
    if (url.pathname === "/") return chooseLanguage(request, url);
    return env.ASSETS.fetch(request);
  },
};

// plyn.one/ → /<code>/: the visitor's own choice (cookie plyn-lang, or ?lang= from older links), then the browser's
// languages in order of preference, then English.
function chooseLanguage(request, url) {
  const pick = (c) => {
    c = (c || "").trim().toLowerCase();
    if (c === "bel" || c.startsWith("be-latn")) return "be-latn";
    if (LANGS.includes(c)) return c;
    const base = c.split("-")[0];
    return LANGS.includes(base) ? base : null;
  };
  const cookie = (request.headers.get("cookie") || "").match(/(?:^|;\s*)plyn-lang=([^;]+)/);
  let code = pick(url.searchParams.get("lang")) || (cookie && pick(cookie[1]));
  if (!code) {
    const prefs = (request.headers.get("accept-language") || "").split(",")
      .map((p) => { const [tag, q] = p.trim().split(";q="); return { tag, q: q === undefined ? 1 : parseFloat(q) || 0 }; })
      .filter((p) => p.tag && p.q > 0).sort((a, b) => b.q - a.q);
    for (const p of prefs) { code = pick(p.tag); if (code) break; }
  }
  return new Response(null, { status: 302, headers: { location: "/" + (code || "en") + "/", vary: "Accept-Language, Cookie", "cache-control": "private, no-store" } });
}

async function beta(request, env) {
  const ip = request.headers.get("cf-connecting-ip") || "unknown";
  if (env.RL) {
    const { success } = await env.RL.limit({ key: ip });
    if (!success) return json({ ok: false, error: "rate" }, 429);
  }
  let data;
  try { data = await request.json(); } catch { return json({ ok: false, error: "input" }, 400); }
  // Honeypot: people never see this field; a filled one is answered as success and dropped.
  if (typeof data.website === "string" && data.website.trim() !== "") return json({ ok: true });

  const email = String(data.email || "").trim().toLowerCase();
  const note = String(data.note || "").trim().slice(0, 2000);
  const lang = LANGS.includes(data.lang) ? data.lang : "en";
  if (email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ ok: false, error: "email" }, 400);

  const verify = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    body: new URLSearchParams({ secret: env.TURNSTILE_SECRET || "", response: String(data.token || ""), remoteip: ip }),
  }).then((r) => r.json()).catch(() => ({ success: false }));
  if (!verify.success) return json({ ok: false, error: "check" }, 403);

  const now = new Date().toISOString();
  const existing = await env.DB.prepare("SELECT email FROM signups WHERE email = ?").bind(email).first();
  if (existing) {
    await env.DB.prepare("UPDATE signups SET note = COALESCE(NULLIF(?, ''), note), lang = ?, updated_at = ? WHERE email = ?").bind(note, lang, now, email).run();
  } else {
    await env.DB.prepare("INSERT INTO signups (email, note, lang, created_at) VALUES (?, ?, ?, ?)").bind(email, note, lang, now).run();
  }
  if (env.MAIL) {
    try { await notify(env, { email, note, lang, now, repeat: !!existing }); } catch (e) { console.log("notify failed", String(e)); }
  }
  return json({ ok: true });
}

function b64(s) {
  const bytes = new TextEncoder().encode(s);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}

async function notify(env, s) {
  const from = "noreply@beta." + APEX; // beta-related mail comes from beta.plyn.one; Email Routing runs on that subdomain
  const to = env.NOTIFY_TO;
  const subject = (s.repeat ? "Plyń beta: repeated sign-up " : "Plyń beta: new sign-up ") + s.email;
  const body = `Email: ${s.email}\nLanguage: ${s.lang}\nTime (UTC): ${s.now}\n${s.repeat ? "Already on the list; note updated if given.\n" : ""}\nNote:\n${s.note || "(none)"}\n`;
  const raw = [
    `From: Plyn beta <${from}>`,
    `To: ${to}`,
    `Subject: =?UTF-8?B?${b64(subject)}?=`,
    `Date: ${new Date().toUTCString()}`,
    `Message-ID: <${crypto.randomUUID()}@${APEX}>`,
    `Reply-To: ${s.email}`,
    "MIME-Version: 1.0",
    "Content-Type: text/plain; charset=utf-8",
    "Content-Transfer-Encoding: base64",
    "",
    b64(body).replace(/.{76}/g, "$&\r\n"),
  ].join("\r\n");
  await env.MAIL.send(new EmailMessage(from, to, raw));
}
