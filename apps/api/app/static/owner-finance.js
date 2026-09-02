(() => {
  const money=v=>Number(v||0).toLocaleString('en-PK',{minimumFractionDigits:2,maximumFractionDigits:2});
  const hotel=()=>localStorage.getItem('stayhub_hotel_id')||'';
  const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
  async function load(){
    const id=hotel(); if(!id)return;
    const section=document.querySelector('#finance, [data-section="finance"]'); if(!section)return;
    try{
      const r=await fetch(`/finance/owner/${id}`); const d=await r.json(); if(!r.ok)throw Error(d.detail||'Finance unavailable');
      section.innerHTML=`<div class="section-heading"><div><span class="eyebrow">FINANCE</span><h2>Reservation Finance</h2><p>Confirmed stays count every night for commission. A charged no-show counts one night; a waived no-show counts zero.</p></div></div><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px"><div class="card"><small>Total Sales</small><h2>PKR ${money(d.total_sales)}</h2></div><div class="card"><small>StayHub Commission</small><h2>PKR ${money(d.total_commission)}</h2></div><div class="card"><small>Commission Count</small><h2>${esc(d.commission_count||0)}</h2></div><div class="card"><small>Owner Earnings</small><h2>PKR ${money(d.owner_earnings)}</h2></div></div><div class="card" style="overflow:auto"><table class="table"><thead><tr><th>Booking</th><th>Stay</th><th>Room Price</th><th>Discount</th><th>After Discount</th><th>Tax</th><th>Total</th><th>StayHub Commission</th><th>Commission Count</th><th>Owner Amount</th></tr></thead><tbody>${d.reservations.map(x=>`<tr><td><b>${esc(x.confirmation_no)}</b><br><small>${esc(x.booking_source)}</small></td><td>${esc(x.check_in)} → ${esc(x.check_out)}<br><small>${esc(x.status)}</small></td><td>PKR ${money(x.base_price)}</td><td>PKR ${money(x.discount_amount)}</td><td>PKR ${money(x.selling_price)}</td><td>PKR ${money(x.tax_amount)}</td><td><b>PKR ${money(x.total_amount)}</b></td><td>PKR ${money(x.commission_amount)} (${money(x.commission_percent)}%)</td><td>${esc(x.commission_count||0)}</td><td><b>PKR ${money(x.owner_amount)}</b></td></tr>`).join('')||'<tr><td colspan="10">No reservations yet.</td></tr>'}</tbody></table></div>`;
    }catch(e){section.innerHTML=`<div class="empty">Finance could not be loaded: ${esc(e.message)}</div>`}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(load,700));else setTimeout(load,700);
})();
