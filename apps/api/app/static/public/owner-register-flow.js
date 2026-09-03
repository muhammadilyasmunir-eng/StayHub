(function(){
'use strict';
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)],F=window.fetch.bind(window);
let token=null,verifiedEmail='';
const esc=s=>String(s||'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]));
const error=(m,x)=>{const e=$('#error');if(e)e.innerHTML=m?'<div class="error">'+esc(m)+'</div>':'';if(m&&x)x.focus()};
const form=$('#reg'),panes=$$('.pane');
if(!form||!panes.length)return;

// owner-register-v5.html already contains the complete 7-step form.
// Do not inject another Property Type pane or renumber the existing panes.
const owner=panes.find(p=>p.dataset.step==='1');
const property=panes.find(p=>p.dataset.step==='2');
if(!owner||!property)return;

const emailInput=owner.querySelector('[name="owner_email"]');
const email=()=>emailInput?.value.trim()||'';
const ef=emailInput?.closest('.field');
if(ef&&!$('#ownerOtpBox')){
  const b=document.createElement('div');
  b.className='field full';
  b.id='ownerOtpBox';
  b.innerHTML='<label>Email Verification *</label><div style="display:flex;gap:8px;flex-wrap:wrap"><button type="button" class="btn" id="sendOwnerOtp">Send OTP</button><span id="otpStatus" class="hint">Verify your email before continuing.</span></div><div id="otpEntry" style="display:none;margin-top:10px"><div style="display:flex;gap:8px;flex-wrap:wrap"><input id="ownerOtp" inputmode="numeric" maxlength="6" placeholder="Enter 6-digit OTP" style="max-width:220px"><button type="button" class="btn add" id="verifyOwnerOtp">Verify OTP</button></div></div>';
  ef.after(b);
}
emailInput?.addEventListener('input',()=>{
  if(email()!==verifiedEmail){
    token=null;
    const entry=$('#otpEntry'),status=$('#otpStatus');
    if(entry)entry.style.display='none';
    if(status){status.textContent='Email changed. Please send a new OTP.';status.style.color='';}
  }
});
$('#sendOwnerOtp')?.addEventListener('click',async()=>{
  const v=email();
  if(!v||!v.includes('@'))return error('Please enter a valid owner email address.',emailInput);
  const b=$('#sendOwnerOtp');b.disabled=true;b.textContent='Sending...';
  try{
    const r=await F(location.origin+'/public/booking-otp/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:v})});
    const d=await r.json().catch(()=>({}));
    if(!r.ok)throw Error(d.detail||'Unable to send OTP.');
    verifiedEmail=v;token=null;
    $('#otpEntry').style.display='block';$('#otpStatus').textContent='OTP sent. Enter the 6-digit code below.';$('#otpStatus').style.color='';$('#ownerOtp').focus();error('');
  }catch(e){error(e.message)}finally{b.disabled=false;b.textContent='Resend OTP'}
});
$('#verifyOwnerOtp')?.addEventListener('click',async()=>{
  const code=$('#ownerOtp').value.trim();
  if(!/^\d{6}$/.test(code))return error('Please enter the 6-digit OTP.',$('#ownerOtp'));
  const b=$('#verifyOwnerOtp');b.disabled=true;b.textContent='Verifying...';
  try{
    const r=await F(location.origin+'/public/booking-otp/verify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:verifiedEmail,code})});
    const d=await r.json().catch(()=>({}));
    if(!r.ok)throw Error(d.detail||'Invalid OTP.');
    token=d.otp_token;$('#otpStatus').textContent='Email verified successfully ✓';$('#otpStatus').style.color='#15803d';b.textContent='Verified';error('');
  }catch(e){token=null;error(e.message);b.disabled=false;b.textContent='Verify OTP'}
});

const names=['Owner Account','Property Information','Facilities & Policies','Property Photos','Room Categories','Verification Documents','Final Review'];
$$('.pane').forEach((p,i)=>{
  p.dataset.step=String(i+1);
  const h=p.querySelector('h2');
  if(h)h.textContent=(i+1)+'. '+h.textContent.replace(/^\d+\.\s*/,'').replace(/^What type of property are you listing\?$/,'Property Information');
});
let step=1;
function steps(){
  const root=$('#steps');
  if(root)root.innerHTML=names.map((n,i)=>`<div class="step ${i+1===step?'active':i+1<step?'done':''}">${i+1} ${n}</div>`).join('');
}
function show(n){
  step=Math.max(1,Math.min(7,n));
  $$('.pane').forEach(p=>p.classList.toggle('active',+p.dataset.step===step));
  const prev=$('#prev'),next=$('#next'),submit=$('#submit');
  if(prev)prev.style.visibility=step===1?'hidden':'visible';
  if(next)next.style.display=step===7?'none':'inline-block';
  if(submit)submit.style.display=step===7?'inline-block':'none';
  error('');steps();
  if(step===7)buildReview();
  window.scrollTo(0,0);
}
function required(p){
  for(const x of p.querySelectorAll('[required]')){
    if(x.type==='checkbox'&&!x.checked)return error('Please complete the required confirmation in this step.',x),false;
    if(x.type!=='checkbox'&&x.type!=='file'&&!x.value.trim())return error('Please complete all required fields in this step.',x),false;
  }
  return true;
}
function validate(){
  const pane=$$('.pane').find(x=>+x.dataset.step===step);
  if(!pane)return false;
  if(step===1){
    if(!required(pane))return false;
    if(pane.querySelector('[name="password"]').value!==pane.querySelector('[name="password_confirm"]').value)return error('Password and confirmation do not match.'),false;
    if(!token||verifiedEmail!==email())return error('Please verify the owner email with OTP before continuing.'),false;
  }
  if(step===2&&!property.querySelector('[name="property_type"]')?.value.trim())return error('Please select the property type.',property.querySelector('[name="property_type"]')),false;
  if(step===3&&!required(pane))return false;
  if(step===4){
    if(!pane.querySelector('.property-photo'))return error('Add at least one property photo.'),false;
    if(!pane.querySelector('.property-photo .primary:checked'))return error('Select one Main / Primary property photo.'),false;
  }
  if(step===5){
    if(!pane.querySelector('.room'))return error('Add at least one room category.'),false;
    for(const r of pane.querySelectorAll('.room')){
      if(!r.querySelector('.room-facility:checked'))return error('Each room category needs at least one room facility.'),false;
      if(!r.querySelector('.room-photo'))return error('Each room category needs at least one photo.'),false;
      if(!r.querySelector('.room-photo .primary-room:checked'))return error('Select one primary photo for each room category.'),false;
    }
  }
  if(step===6&&!pane.querySelector('.doc'))return error('Add at least one verification document.'),false;
  return true;
}
function buildReview(){
  const r=$('#review');if(!r)return;
  const p=property.querySelector('[name="property_name"]')?.value||'';
  const c=property.querySelector('[name="city"]')?.value||'';
  const t=property.querySelector('[name="property_type"]')?.value||'';
  r.innerHTML='<div class="review"><h3>Ready to submit</h3><p><b>Property:</b> '+esc(p||'Not entered')+'</p><p><b>Type:</b> '+esc(t||'Not selected')+'</p><p><b>City:</b> '+esc(c||'Not entered')+'</p><p><b>Email:</b> '+esc(email())+' <span class="badge">Verified</span></p><p class="hint">Your property will remain pending until StayHub Admin approves it.</p></div>';
}
window.fetch=function(input,init){
  const u=typeof input==='string'?input:(input?.url||'');
  if(u.endsWith('/users/owner-register')&&token){const n={...(init||{})};n.headers=new Headers(n.headers||{});n.headers.set('X-Owner-OTP-Token',token);return F(input,n)}
  return F(input,init);
};
const next=$('#next'),prev=$('#prev');
if(next)next.onclick=()=>{if(validate())show(step+1)};
if(prev)prev.onclick=()=>show(step-1);
show(1);
})();
