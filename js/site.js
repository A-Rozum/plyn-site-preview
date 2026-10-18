// Page behaviour: language switch (goes to /<code>/ and remembers the choice in a cookie that plyn.one/ follows),
// theme, years in the footer, beta form (Turnstile, POST /api/beta). Texts are in the page, built per language.
{const y=new Date().getFullYear();if(y>2026)document.getElementById('years').textContent='2026–'+y}
const sel=document.getElementById('lang'),R=document.documentElement;
sel.addEventListener('change',()=>{document.cookie='plyn-lang='+sel.value+';path=/;max-age=31536000;samesite=lax;secure';location.href='/'+sel.value+'/'});
try{const v=localStorage.getItem('plyn-theme');if(v)R.dataset.scheme=v}catch(e){}
document.getElementById('theme').addEventListener('click',()=>{const dark=R.dataset.scheme?R.dataset.scheme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;R.dataset.scheme=dark?'light':'dark';try{localStorage.setItem('plyn-theme',R.dataset.scheme)}catch(e){}});
const modal=document.getElementById('interest');document.getElementById('open').onclick=()=>modal.showModal();document.getElementById('close').onclick=()=>modal.close();
const form=document.getElementById('beta'),notice=document.getElementById('notice'),SITEKEY='0x4AAAAAAFZ4GQJpHoVa8fZ8';let tsId=null,tsWait=null;
function token(){return new Promise((ok,no)=>{if(!window.turnstile)return no(new Error('turnstile'));tsWait={ok,no};
if(tsId===null)tsId=turnstile.render('#ts',{sitekey:SITEKEY,execution:'execute',appearance:'interaction-only',callback:t=>{tsWait&&tsWait.ok(t);tsWait=null},'error-callback':()=>{tsWait&&tsWait.no(new Error('turnstile'));tsWait=null},'expired-callback':()=>turnstile.reset(tsId)});
else turnstile.reset(tsId);turnstile.execute(tsId)})}
function say(key,err){notice.textContent=notice.dataset[key];notice.classList.toggle('err',!!err)}
form.onsubmit=async e=>{e.preventDefault();const btn=form.querySelector('[type=submit]');btn.disabled=true;say('sending');
try{const t=await token();const r=await fetch('/api/beta',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({email:form.email.value,note:form.usecase.value,website:form.website.value,lang:sel.value,token:t})});
const j=await r.json().catch(()=>({}));if(!r.ok||!j.ok)throw new Error(j.error||r.status);say('ok');form.reset()}catch(x){say('err',true)}finally{btn.disabled=false}};
