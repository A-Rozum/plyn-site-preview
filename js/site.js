// Page behaviour: language, theme, years in the footer, beta form (Turnstile, POST /api/beta).
const LANGS=[["en", "en"], ["be", "be"], ["bel", "be-Latn"], ["pl", "pl"], ["it", "it"], ["lt", "lt"]];
{const y=new Date().getFullYear();if(y>2026)document.getElementById('years').textContent='2026–'+y}
const sel=document.getElementById('lang');const theme=document.getElementById('theme');
function setLang(code){if(!I18N[code])code='en';const t=I18N[code];document.documentElement.lang=LANGS.find(x=>x[0]===code)[1];sel.value=code;
document.querySelectorAll('[data-i18n]').forEach(e=>{e.textContent=t[e.dataset.i18n]});
document.querySelectorAll('[data-i18n-ph]').forEach(e=>{e.placeholder=t[e.dataset.i18nPh]});
document.querySelectorAll('[data-i18n-aria]').forEach(e=>{e.setAttribute('aria-label',t[e.dataset.i18nAria])});
document.title=t.title;document.querySelector('meta[name=description]').content=t.desc}
function pickLang(){let q=new URLSearchParams(location.search).get('lang');if(q&&I18N[q])return q;
try{const v=localStorage.getItem('plyn-lang');if(v&&I18N[v])return v}catch(e){}
for(const l of navigator.languages||[navigator.language||'']){const t=l.toLowerCase();if(t.startsWith('be-latn'))return 'bel';const b=t.split('-')[0];if(I18N[b])return b}
return 'en'}
sel.addEventListener('change',()=>{setLang(sel.value);try{localStorage.setItem('plyn-lang',sel.value)}catch(e){}});
setLang(pickLang());
const R=document.documentElement;try{const v=localStorage.getItem('plyn-theme');if(v)R.dataset.scheme=v}catch(e){}
theme.addEventListener('click',()=>{const dark=R.dataset.scheme?R.dataset.scheme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;R.dataset.scheme=dark?'light':'dark';try{localStorage.setItem('plyn-theme',R.dataset.scheme)}catch(e){}});
const modal=document.getElementById('interest');document.getElementById('open').onclick=()=>modal.showModal();document.getElementById('close').onclick=()=>modal.close();const form=document.getElementById('beta'),notice=document.getElementById('notice'),SITEKEY='0x4AAAAAAFZ4GQJpHoVa8fZ8';let tsId=null,tsWait=null;
function token(){return new Promise((ok,no)=>{if(!window.turnstile)return no(new Error('turnstile'));tsWait={ok,no};
if(tsId===null)tsId=turnstile.render('#ts',{sitekey:SITEKEY,execution:'execute',appearance:'interaction-only',callback:t=>{tsWait&&tsWait.ok(t);tsWait=null},'error-callback':()=>{tsWait&&tsWait.no(new Error('turnstile'));tsWait=null},'expired-callback':()=>turnstile.reset(tsId)});
else turnstile.reset(tsId);turnstile.execute(tsId)})}
function say(key,err){notice.textContent=I18N[sel.value][key];notice.dataset.key=key;notice.classList.toggle('err',!!err)}
form.onsubmit=async e=>{e.preventDefault();const btn=form.querySelector('[type=submit]');btn.disabled=true;say('sending');
try{const t=await token();const r=await fetch('/api/beta',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({email:form.email.value,note:form.usecase.value,website:form.website.value,lang:sel.value,token:t})});
const j=await r.json().catch(()=>({}));if(!r.ok||!j.ok)throw new Error(j.error||r.status);say('ok');form.reset()}catch(x){say('err',true)}finally{btn.disabled=false}};
sel.addEventListener('change',()=>{if(notice.dataset.key)say(notice.dataset.key,notice.classList.contains('err'))});
