(function(){
  function token(){return localStorage.getItem('stayhub_admin_token')||'';}
  function esc(v){return String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));}
  function applyLivePropertiesUI(){
    const dashboard=document.getElementById('dashboard');
    const grid=dashboard?.querySelector('#opsDashboardCards .grid4');
    if(grid){
      const oldActive=grid.querySelector('[data-dashboard-target="property-status-active"]');
      if(oldActive) oldActive.remove();
      const liveCard=grid.querySelector('[data-dashboard-target="property-status-live"]');
      if(liveCard) liveCard.remove();
    }
    const nav=document.querySelector('[data-stayhub-nav="property-status-active"]');
    if(nav) nav.remove();
    const page=document.getElementById('property-status-active');
    if(page) page.remove();
    const activeCount=document.getElementById('dashActive');
    if(activeCount){const activeCard=activeCount.closest('[data-dashboard-target="property-status-active"]');if(activeCard) activeCard.remove();}
  }

  function ensureReservationsUI(){
    if(document.getElementById('stayhubAdminReservations')) return;
    const sidebar=document.querySelector('.sidebar');
    const main=document.querySelector('main.content');
    if(!sidebar||!main) return;
    const navTitle=document.createElement('div');navTitle.className='nav-title';navTitle.textContent='Operations';
    const nav=document.createElement('button');nav.className='nav-btn';nav.innerHTML='▤ <span class="nav-label">Reservations</span>';
    nav.onclick=()=>showReservations();
    sidebar.appendChild(navTitle);sidebar.appendChild(nav);
    const section=document.createElement('section');section.id='stayhubAdminReservations';section.className='hidden';
    section.innerHTML=`<div class="page-head"><div><span class="eyebrow">BOOKINGS</span><h1>Reservations</h1><p class="muted">Live reservations from the StayHub marketplace.</p></div><button class="ghost" id="adminReservationRefresh">Refresh</button></div><div class="card"><div class="table-wrap"><table class="table"><thead><tr><th>Confirmation</th><th>Guest</th><th>Hotel</th><th>Room</th><th>Check-in</th><th>Check-out</th><th>Status</th><th>Payment</th><th>Total</th></tr></thead><tbody id="adminReservationRows"><tr><td colspan="9" class="empty">Loading reservations...</td></tr></tbody></table></div></div>`;
    main.appendChild(section);
    document.getElementById('adminReservationRefresh').onclick=loadReservations;
    loadReservations();
  }

  function showReservations(){
    document.querySelectorAll('main section').forEach(s=>s.classList.add('hidden'));
    const section=document.getElementById('stayhubAdminReservations');if(section)section.classList.remove('hidden');
    document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));
    const btn=[...document.querySelectorAll('.nav-btn')].find(b=>b.textContent.includes('Reservations'));if(btn)btn.classList.add('active');
    loadReservations();
  }

  async function loadReservations(){
    const tbody=document.getElementById('adminReservationRows');if(!tbody)return;
    try{
      const r=await fetch('/admin/reservations/',{headers:{Authorization:'Bearer '+token(),Accept:'application/json'}});
      const data=await r.json().catch(()=>({detail:'Unable to read reservations'}));
      if(!r.ok)throw Error(data.detail||'Unable to load reservations');
      tbody.innerHTML=data.length?data.map(x=>`<tr><td><b>${esc(x.confirmation_no)}</b></td><td><b>${esc(x.guest_name||'—')}</b><br><small>${esc(x.guest_phone||x.guest_email||'')}</small></td><td>${esc(x.hotel_name||'—')}</td><td>${esc(x.room_type_name||'—')}<br><small>${esc(x.room_number||'')}</small></td><td>${esc(x.check_in||'—')}</td><td>${esc(x.check_out||'—')}</td><td><span class="badge ${String(x.status||'').toLowerCase().replaceAll(' ','-')}">${esc(x.status)}</span></td><td>${esc(x.payment_method||'—')}<br><small>${esc(x.payment_status||'')}</small></td><td><b>PKR ${Number(x.total_amount||0).toLocaleString('en-PK')}</b></td></tr>`).join(''):'<tr><td colspan="9" class="empty">No reservations found.</td></tr>';
    }catch(e){tbody.innerHTML=`<tr><td colspan="9" class="empty">${esc(e.message)}</td></tr>`;}
  }

  document.addEventListener('DOMContentLoaded',()=>{setTimeout(()=>{applyLivePropertiesUI();ensureReservationsUI()},700)});
  setTimeout(()=>{applyLivePropertiesUI();ensureReservationsUI()},1500);
  setInterval(()=>{applyLivePropertiesUI();ensureReservationsUI();if(!document.getElementById('stayhubAdminReservations')?.classList.contains('hidden'))loadReservations()},15000);
})();