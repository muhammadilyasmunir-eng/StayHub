(()=>{
'use strict';
const $=id=>document.getElementById(id);
function init(){
 const form=$('form'),prev=$('prev'),next=$('next'),submit=$('submit'),error=$('error'),review=$('review');
 if(!form||!prev||!next||!submit) return;
 const panes=()=>[...document.querySelectorAll('.pane')];
 const current=()=>panes().find(p=>p.classList.contains('active'));
 const step=()=>Number(current()?.dataset.step||1);
 const setError=(msg,el)=>{ if(error) error.innerHTML='<div class="error">'+msg+'</div>'; if(el&&typeof el.focus==='function') el.focus(); };
 const clearError=()=>{if(error)error.innerHTML='';};
 function validatePane(){
   const pane=current(); if(!pane) return false;
   for(const el of pane.querySelectorAll('[required]')){
     if(el.disabled) continue;
     if(el.type==='checkbox'||el.type==='radio'){ if(el.type==='checkbox'&&!el.checked){setError('Please complete all required fields in this step.',el);return false;} }
     else if(!String(el.value??'').trim()){setError('Please complete all required fields in this step.',el);return false;}
   }
   if(step()===1){const a=form.querySelector('[name="password"]'),b=form.querySelector('[name="password_confirm"]');if(a&&b&&a.value!==b.value){setError('Password and confirmation do not match.',b);return false;}}
   if(step()===3&&!pane.querySelector('.facility:checked')){setError('Select at least one property facility.');return false;}
   if(step()===4){const photos=[...pane.querySelectorAll('.property-photo')];if(!photos.length){setError('Upload at least one property photo.');return false;}if(photos.some(p=>!p.querySelector('.photo-name')?.value.trim())){setError('Every property photo must have a photo name.');return false;}if(photos.some(p=>!p.querySelector('.photo-category')?.value)){setError('Select a category for every property photo.');return false;}if(photos.filter(p=>p.querySelector('.primary-property')?.checked).length!==1){setError('Select exactly one Main / Primary property photo.');return false;}}
   if(step()===5){const rooms=[...pane.querySelectorAll('.room')];if(!rooms.length){setError('Add at least one room category.');return false;}for(const r of rooms){if(!r.querySelector('.room-facility:checked')){setError('Every room category needs at least one facility.');return false;}const photos=[...r.querySelectorAll('.room-photo')];if(!photos.length){setError('Every room category needs at least one photo.');return false;}if(photos.some(p=>!p.querySelector('.photo-name')?.value.trim())){setError('Every room photo must have a photo name.');return false;}if(photos.filter(p=>p.querySelector('.primary-room')?.checked).length!==1){setError('Select exactly one primary photo for each room category.');return false;}}}
   if(step()===6&&!pane.querySelector('.doc')){setError('Add at least one verification document.');return false;}
   return true;
 }
 function go(target){
   if(target<1||target>7) return;
   panes().forEach(p=>p.classList.toggle('active',Number(p.dataset.step)===target));
   prev.style.visibility=target===1?'hidden':'visible';
   next.style.display=target===7?'none':'inline-block';
   submit.style.display=target===7?'inline-block':'none';
   clearError();
   if(target===7){try{if(typeof window.buildReview==='function')window.buildReview();else if(review)review.innerHTML='<p>Please review all entered information before submitting.</p>';}catch(e){if(review)review.innerHTML='<p>Review is ready. Please verify your entered information.</p>';}}
   document.querySelectorAll('.step').forEach((el,i)=>{el.classList.toggle('active',i+1===target);el.classList.toggle('done',i+1<target);});
   window.scrollTo({top:0,behavior:'smooth'});
 }
 next.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();if(validatePane())go(step()+1);},true);
 prev.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();go(step()-1);},true);
 form.addEventListener('submit',e=>{if(step()!==7){e.preventDefault();return;}},true);
 go(step());
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();