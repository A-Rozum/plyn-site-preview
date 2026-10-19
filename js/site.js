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
/* Consent: our own bar. Choice kept in localStorage plyn-consent (yes/no). With yes: cookie plyn-vid (random visit number, 1 year)
   for returning visitors, and Microsoft Clarity (project id in CLARITY; empty = not loaded). The choice is reported as an anonymous hit. */
(()=>{const bar=document.getElementById('consent');if(!bar)return;const CLARITY='';
const store={get:()=>{try{return localStorage.getItem('plyn-consent')}catch(e){return null}},set:v=>{try{localStorage.setItem('plyn-consent',v)}catch(e){}}};
const hit=k=>{try{navigator.sendBeacon('/api/hit',JSON.stringify({kind:k,lang:document.documentElement.lang}))}catch(e){}};
const clarity=on=>{if(!CLARITY)return;if(on&&!window.clarity){(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src='https://www.clarity.ms/tag/'+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y)})(window,document,'clarity','script',CLARITY)}
if(window.clarity)window.clarity('consentv2',{ad_Storage:'denied',analytics_Storage:on?'granted':'denied'});if(!on&&window.clarity)window.clarity('consent',false)};
const vid=on=>{if(on){if(!/plyn-vid=/.test(document.cookie)){const a=crypto.getRandomValues(new Uint8Array(12));document.cookie='plyn-vid='+Array.from(a,b=>b.toString(16).padStart(2,'0')).join('')+';path=/;max-age=31536000;samesite=lax;secure'}}else document.cookie='plyn-vid=;path=/;max-age=0'};
const apply=on=>{vid(on);clarity(on)};
const show=()=>{bar.hidden=false;bar.classList.remove('leave');bar.classList.remove('show');void bar.offsetWidth;bar.classList.add('show')};
const hide=()=>{bar.classList.add('leave');setTimeout(()=>{bar.hidden=true;bar.classList.remove('leave')},800)};
const choose=on=>{store.set(on?'yes':'no');apply(on);hit(on?'consent-yes':'consent-no');hide()};
bar.querySelector('.yes').addEventListener('click',()=>choose(true));bar.querySelector('.no').addEventListener('click',()=>choose(false));
bar.querySelector('.more').addEventListener('click',()=>{const i=bar.querySelector('.info');i.hidden=!i.hidden});
document.querySelectorAll('.privacy-link').forEach(b=>b.addEventListener('click',()=>{show();bar.querySelector('.info').hidden=false}));
const c=store.get();if(c){apply(c==='yes');return}
let t=setTimeout(show,10000);const early=()=>{clearTimeout(t);t=setTimeout(show,2500);removeEventListener('scroll',early);removeEventListener('pointerdown',early)};
addEventListener('scroll',early,{passive:true});addEventListener('pointerdown',early)})();
