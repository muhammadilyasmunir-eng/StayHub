(function(){
  'use strict';
  const css=`.room-pricing-fields{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}.room-pricing-fields label{display:flex;flex-direction:column;gap:6px;font-weight:700;font-size:13px}.room-pricing-fields input{box-sizing:border-box;width:100%;padding:11px;border:1px solid #d1d5db;border-radius:8px}@media(max-width:800px){.room-pricing-fields{grid-template-columns:1fr}}`;
  const s=document.createElement('style');s.textContent=css;document.head.appendChild(s);
  function installRoom(room){
    if(!room||room.dataset.pricingInstalled==='1')return;
    room.dataset.pricingInstalled='1';
    const base=room.querySelector('.base-price');
    if(!base)return;
    const wrap=document.createElement('div');wrap.className='room-pricing-fields';
    const discount=document.createElement('label');discount.innerHTML='Discount (optional)<input class="discount-percent" type="number" min="0" max="100" step="0.01" value="0" placeholder="0">';
    const sell=document.createElement('label');sell.innerHTML='Selling Price <input class="selling-price-preview" type="text" readonly value="0.00">';
    wrap.append(discount,sell);
    base.closest('.group')?.parentElement?.appendChild(wrap);
    const update=()=>{const b=Number(base.value||0),d=Number(discount.querySelector('input').value||0);sell.querySelector('input').value=(b*(100-d)/100).toFixed(2)};
    base.addEventListener('input',update);discount.querySelector('input').addEventListener('input',update);update();
  }
  function scan(){document.querySelectorAll('.room').forEach(installRoom)}
  document.addEventListener('DOMContentLoaded',()=>{scan();new MutationObserver(scan).observe(document.body,{childList:true,subtree:true})});
  scan();
})();
