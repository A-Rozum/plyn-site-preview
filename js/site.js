// Page behaviour: language switch (goes to /<code>/ and remembers the choice in a cookie that plyn.one/ follows),
// theme, years in the footer, beta form (Turnstile, POST /api/beta). Texts are in the page, built per language.
{const y=new Date().getFullYear();if(y>2026)document.getElementById('years').textContent='2026–'+y}
const sel=document.getElementById('lang'),R=document.documentElement;
sel.addEventListener('change',()=>{document.cookie='plyn-lang='+sel.value+';path=/;max-age=31536000;samesite=lax;secure';location.href='/'+sel.value+'/'});
try{const v=localStorage.getItem('plyn-theme');if(v)R.dataset.scheme=v}catch(e){}
document.getElementById('theme').addEventListener('click',()=>{const dark=R.dataset.scheme?R.dataset.scheme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;R.dataset.scheme=dark?'light':'dark';try{localStorage.setItem('plyn-theme',R.dataset.scheme)}catch(e){}});
// Turnstile loads when the form opens, so the page itself needs nothing from other servers.
let tsLoad=null;const loadTs=()=>tsLoad||(tsLoad=new Promise((ok,no)=>{const s=document.createElement('script');s.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';s.async=true;s.onload=ok;s.onerror=()=>{tsLoad=null;no(new Error('turnstile'))};document.head.append(s)}));
// Anonymous statistics: form opened and sent, and on leaving the time on the page and whether anything was touched.
let touched=false,left=false;const hit=(k,x)=>{try{navigator.sendBeacon('/api/hit',JSON.stringify(Object.assign({kind:k,lang:sel.value},x||{})))}catch(e){}};
addEventListener('pointerdown',()=>{touched=true},{once:true,capture:true});addEventListener('keydown',()=>{touched=true},{once:true,capture:true});
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden'&&!left){left=true;hit('leave',{ms:Math.round(performance.now()),interacted:touched})}});
const modal=document.getElementById('interest');document.getElementById('open').onclick=()=>{modal.showModal();loadTs().catch(()=>{});hit('open')};document.getElementById('close').onclick=()=>modal.close();
const form=document.getElementById('beta'),notice=document.getElementById('notice'),SITEKEY='0x4AAAAAAFZ4GQJpHoVa8fZ8';let tsId=null,tsWait=null;
async function token(){await loadTs();return new Promise((ok,no)=>{tsWait={ok,no};
if(tsId===null)tsId=turnstile.render('#ts',{sitekey:SITEKEY,execution:'execute',appearance:'interaction-only',callback:t=>{tsWait&&tsWait.ok(t);tsWait=null},'error-callback':()=>{tsWait&&tsWait.no(new Error('turnstile'));tsWait=null},'expired-callback':()=>turnstile.reset(tsId)});
else turnstile.reset(tsId);turnstile.execute(tsId)})}
function say(key,err){notice.textContent=notice.dataset[key];notice.classList.remove('dev');void notice.offsetWidth;notice.classList.add('dev');notice.classList.toggle('err',!!err)}
form.onsubmit=async e=>{e.preventDefault();const btn=form.querySelector('[type=submit]');btn.disabled=true;say('sending');
try{const t=await token();const r=await fetch('/api/beta',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({email:form.email.value,note:form.usecase.value,website:form.website.value,lang:sel.value,token:t})});
const j=await r.json().catch(()=>({}));if(!r.ok||!j.ok)throw new Error(j.error||r.status);say('ok');form.reset();hit('submit')}catch(x){say('err',true)}finally{btn.disabled=false}};
/* Silver bullet in the footer: a tap shows its line for a few seconds; pointer users see it on hover. */
(()=>{const o=document.querySelector('.bullet');if(!o)return;let t;o.addEventListener('click',()=>{o.classList.add('lit');clearTimeout(t);t=setTimeout(()=>o.classList.remove('lit'),4500)});
console.log('%cSilver bullets aren’t found. They’re cast.','color:#9aa4ad;font-style:italic')})();
