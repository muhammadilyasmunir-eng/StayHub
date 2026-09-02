(() => {
  const originalLoadData = window.loadData;
  const q = (id) => document.getElementById(id);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
  const token = () => localStorage.getItem('stayhub_token') || '';
  const hotel = () => localStorage.getItem('stayhub_hotel_id') || '';
  let reservationRows = [];

  async function api(url, options = {}) {
    const headers = {...(options.headers || {}), Authorization: `Bearer ${token()}`};
    if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
    const r = await fetch(url, {...options, headers});
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.detail || 'Request failed');
    return d;
  }

  function toast(message, error = false) {
    let el = q('opsToast');
    if (!el) { el = document.createElement('div'); el.id = 'opsToast'; el.style.cssText = 'position:fixed;right:24px;bottom:24px;z-index:9999;padding:13px 16px;border-radius:12px;background:#172033;color:white;box-shadow:0 10px 30px #0003;font-weight:600'; document.body.appendChild(el); }
    el.textContent = message; el.style.background = error ? '#991b1b' : '#172033';
    clearTimeout(el._t); el._t = setTimeout(() => el.remove(), 3200);
  }

  function modal(title, body, onSubmit) {
    const old = q('opsModal'); if (old) old.remove();
    const wrap = document.createElement('div');
    wrap.id = 'opsModal'; wrap.style.cssText = 'position:fixed;inset:0;background:#07111dcc;display:grid;place-items:center;z-index:10000;padding:20px;overflow:auto';
    wrap.innerHTML = `<div style="width:min(760px,100%);max-height:90vh;overflow:auto;background:white;border-radius:18px;padding:24px;box-shadow:0 30px 80px #0005"><div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">${esc(title)}</h2><button id="opsClose" style="border:0;background:#eef2f7;border-radius:9px;padding:8px 11px">✕</button></div><form id="opsForm" style="display:grid;gap:12px;margin-top:18px">${body}<div style="display:flex;justify-content:flex-end;gap:10px;margin-top:8px"><button type="button" id="opsCancel" class="ghost">Cancel</button><button type="submit" class="primary">Save</button></div></form></div>`;
    document.body.appendChild(wrap);
    const close = () => wrap.remove(); q('opsClose').onclick = close; q('opsCancel').onclick = close;
    q('opsForm').onsubmit = async e => { e.preventDefault(); try { await onSubmit(new FormData(e.target)); close(); toast('Saved successfully'); if (originalLoadData) await originalLoadData(); } catch (err) { toast(err.message, true); } };
  }

  const field = (label, name, value = '', type = 'text', extra = '') => `<label style="display:grid;gap:6px"><span style="font-size:13px;font-weight:700;color:#475569">${esc(label)}</span><input class="input full" name="${name}" type="${type}" value="${esc(value)}" ${extra}></label>`;

  async function enhancedLoadData() {
    if (!hotel()) return originalLoadData?.();
    try {
      const h = (window.hotels || []).find(x => String(x.id) === String(hotel()));
      if (h) {
        if (q('welcome')) q('welcome').textContent = 'Welcome, ' + h.name;
        if (q('hotelStatus')) q('hotelStatus').textContent = `${h.city}, ${h.country} · ${h.property_type} · ${h.status}`;
        if (q('propertyData')) q('propertyData').innerHTML = Object.entries({Name:h.name,Type:h.property_type,Status:h.status,Address:h.address,City:h.city,Country:h.country,PostalCode:h.postal_code,Phone:h.phone,Website:h.website,TotalRooms:h.total_rooms,CheckIn:h.check_in_time,CheckOut:h.check_out_time}).map(([k,v])=>`<div class="kv" style="margin:8px 0"><b>${k}</b>${esc(v??'—')}</div>`).join('');
      }
      const [res, guests, rooms, types] = await Promise.all([
        api(`/reservations/hotel/${hotel()}`),
        api(`/guests/hotel/${hotel()}`),
        api(`/rooms/hotel/${hotel()}`),
        api(`/room-types/hotel/${hotel()}`)
      ]);
      reservationRows = res || [];
      window.data = {res:reservationRows, guests, rooms, types};
      if (q('reservationCount')) q('reservationCount').textContent = reservationRows.length;
      if (q('guestCount')) q('guestCount').textContent = guests.length;
      if (q('roomCount')) q('roomCount').textContent = rooms.length;
      if (q('roomTypeCount')) q('roomTypeCount').textContent = types.length;
      renderReservationList(reservationRows, guests, rooms, types);
      if (q('guestTable')) q('guestTable').innerHTML = simpleTable(guests,['id','first_name','last_name','phone','email']);
      if (q('roomTable')) q('roomTable').innerHTML = simpleTable(rooms,['id','room_number','room_type_id','status']);
      if (q('roomTypeTable')) q('roomTypeTable').innerHTML = simpleTable(types,['id','name','max_adults','max_children','base_price']);
      if (q('rateTable')) q('rateTable').innerHTML = simpleTable(types,['name','base_price','max_adults','max_children']);
      if (q('revenue')) q('revenue').textContent = reservationRows.filter(x => !isCancelled(x)).reduce((n,x)=>n+Number(x.total_amount||0),0).toLocaleString();
      if (q('paidCount')) q('paidCount').textContent = reservationRows.filter(x => !isCancelled(x)).length;
      if (q('calendarTable')) q('calendarTable').innerHTML = reservationRows.length ? `<table class="table"><thead><tr><th>Guest / Booking</th><th>Check-in</th><th>Check-out</th><th>Status</th><th>Amount</th></tr></thead><tbody>${reservationRows.map(x=>`<tr><td>#${esc(x.confirmation_no || x.id)}</td><td>${esc(x.check_in)}</td><td>${esc(x.check_out)}</td><td>${statusBadge(x.status)}</td><td>PKR ${money(x.total_amount)}</td></tr>`).join('')}</tbody></table>` : '<div class="empty">No reservations to display.</div>';
    } catch (e) { toast(e.message, true); }
  }

  function isCancelled(r) { return String(r.status || '').toLowerCase().includes('cancel'); }
  function money(v) { return Number(v || 0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}); }
  function statusBadge(s) { const v=String(s||'').replaceAll('_',' '); return `<span style="display:inline-flex;padding:5px 9px;border-radius:999px;background:${v.toLowerCase().includes('cancel')?'#fee2e2':v.toLowerCase().includes('check')?'#dcfce7':'#e0f2fe'};color:${v.toLowerCase().includes('cancel')?'#991b1b':'#075985'};font-weight:700;font-size:12px">${esc(v)}</span>`; }

  function renderReservationList(rows, guests, rooms, types) {
    const host=q('reservationTable'); if(!host) return;
    const guestMap=new Map((guests||[]).map(g=>[g.id,g]));
    const roomMap=new Map((rooms||[]).map(r=>[r.id,r]));
    const typeMap=new Map((types||[]).map(t=>[t.id,t]));
    host.innerHTML=`<div class="reservation-tools" style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr auto;gap:10px;margin-bottom:16px">
      <input id="resSearch" class="input full" placeholder="Search guest or booking number">
      <input id="resFrom" class="input full" type="date" title="Check-in from">
      <input id="resUntil" class="input full" type="date" title="Check-in until">
      <select id="resStatus" class="select full"><option value="">All statuses</option><option>Pending</option><option>Confirmed</option><option>Checked In</option><option>Checked Out</option><option>Cancelled</option><option>No Show</option></select>
      <button class="ghost" id="resPrint">Print</button></div>
      <div id="resSummary" style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px"></div>
      <div class="table-wrap" style="overflow:auto"><table class="table"><thead><tr><th>Guest</th><th>Check-in</th><th>Check-out</th><th>Rooms</th><th>Booked on</th><th>Status</th><th>Price</th><th>Commission</th><th>Booking number</th></tr></thead><tbody id="resBody"></tbody></table></div>`;
    const render=()=>{
      const search=(q('resSearch').value||'').trim().toLowerCase(); const from=q('resFrom').value; const until=q('resUntil').value; const status=q('resStatus').value;
      const filtered=rows.filter(r=>{const g=guestMap.get(r.guest_id)||{};const name=`${g.first_name||''} ${g.last_name||''}`.toLowerCase();if(search&&!name.includes(search)&&!String(r.confirmation_no||r.id).toLowerCase().includes(search))return false;if(from&&r.check_in<from)return false;if(until&&r.check_in>until)return false;if(status&&String(r.status).replaceAll('_',' ')!==status)return false;return true;});
      const total=filtered.filter(r=>!isCancelled(r)).reduce((n,r)=>n+Number(r.total_amount||0),0);
      const commission=filtered.filter(r=>!isCancelled(r)).reduce((n,r)=>n+Number(r.commission_amount ?? 0),0);
      q('resSummary').innerHTML=`<span class="notice">${filtered.length} reservation${filtered.length===1?'':'s'}</span><span class="notice">Total Price: <b>PKR ${money(total)}</b></span><span class="notice">Est. Commission: <b>PKR ${money(commission)}</b></span>`;
      q('resBody').innerHTML=filtered.length?filtered.map(r=>{const g=guestMap.get(r.guest_id)||{};const room=roomMap.get(r.room_id)||{};const type=typeMap.get(room.room_type_id)||{};const guestsText=`${Number(r.adults||0)} adults${Number(r.children||0)?`, ${r.children} children`:''}`;return `<tr data-res-id="${esc(r.id)}" style="cursor:pointer"><td><b>${esc(`${g.first_name||''} ${g.last_name||''}`.trim()||'Guest')}</b><br><small>${esc(guestsText)}</small></td><td>${esc(r.check_in)}</td><td>${esc(r.check_out)}</td><td>${esc(type.name||room.room_number||'—')}</td><td>${esc((r.created_at||'').slice(0,10)||'—')}</td><td>${statusBadge(r.status)}</td><td><b>PKR ${money(r.total_amount)}</b></td><td>PKR ${money(isCancelled(r)?0:Number(r.commission_amount ?? 0))}</td><td><b>${esc(r.confirmation_no||r.id)}</b><br><small>${esc(String(r.booking_source||'').replaceAll('_',' '))}</small></td></tr>`}).join(''):'<tr><td colspan="9"><div class="empty">No reservations match these filters.</div></td></tr>';
      q('resBody').querySelectorAll('tr[data-res-id]').forEach(tr=>tr.onclick=()=>showReservationDetail(Number(tr.dataset.resId),guestMap.get(Number(tr.dataset.resId))));
    };
    ['resSearch','resFrom','resUntil','resStatus'].forEach(id=>q(id).addEventListener('input',render));
    q('resPrint').onclick=()=>window.print();
    render();
  }

  function simpleTable(a,keys){if(!a.length)return'<div class="empty">No records found.</div>';return'<table class="table"><thead><tr>'+keys.map(k=>`<th>${esc(k.replaceAll('_',' '))}</th>`).join('')+'</tr></thead><tbody>'+a.map(x=>'<tr>'+keys.map(k=>`<td>${esc(x[k]??'—')}</td>`).join('')+'</tr>').join('')+'</tbody></table>'}

  async function showReservationDetail(id, guestHint) {
    try {
      const r=await api(`/reservations/${id}`); const guests=(window.data&&window.data.guests)||[]; const rooms=(window.data&&window.data.rooms)||[]; const types=(window.data&&window.data.types)||[];
      const g=guests.find(x=>x.id===r.guest_id)||guestHint||{}; const room=rooms.find(x=>x.id===r.room_id)||{}; const type=types.find(x=>x.id===room.room_type_id)||{};
      const nights=Math.max(0,Math.round((new Date(r.check_out)-new Date(r.check_in))/86400000)); const commission=isCancelled(r)?0:Number(r.commission_amount ?? 0);
      const body=`<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:18px">${[['Check-in',r.check_in],['Check-out',r.check_out],['Length',`${nights} night${nights===1?'':'s'}`],['Guests',`${r.adults||0} adults${r.children?`, ${r.children} children`:''}`]].map(([a,b])=>`<div style="background:#f8fafc;border-radius:12px;padding:12px"><small>${esc(a)}</small><br><b>${esc(b)}</b></div>`).join('')}</div>
      <div class="notice" style="margin-bottom:14px"><b>${esc(`${g.first_name||''} ${g.last_name||''}`.trim()||'Guest')}</b> · ${esc(g.email||'')} · ${esc(g.phone||'')}<br>Channel: <b>${esc(String(r.booking_source||'').replaceAll('_',' '))}</b> · Booking number: <b>${esc(r.confirmation_no||r.id)}</b><br>Booked: ${esc((r.created_at||'').slice(0,10)||'—')}</div>
      <h3>Room & Rate</h3><div class="card" style="box-shadow:none;border:1px solid #e2e8f0"><b>${esc(type.name||room.room_number||'Room')}</b><p>${esc(`${r.adults||0} adults${r.children?`, ${r.children} children`:''}`)}</p><div style="display:flex;justify-content:space-between"><span>Room rate</span><b>PKR ${money(r.room_rate)}</b></div><div style="display:flex;justify-content:space-between"><span>Discount</span><b>PKR ${money(r.discount)}</b></div><div style="display:flex;justify-content:space-between"><span>Tax</span><b>PKR ${money(r.tax)}</b></div><hr><div style="display:flex;justify-content:space-between;font-size:18px"><b>Total</b><b>PKR ${money(r.total_amount)}</b></div></div>
      <h3>Commission & Notes</h3><div class="notice">Estimated commission: <b>PKR ${money(commission)}</b><br>${esc(r.remarks||'No internal note added.')}</div>
      <h3>Reservation Actions</h3><div style="display:flex;gap:8px;flex-wrap:wrap"><button type="button" class="ghost" onclick="window.stayhubChangeReservation(${r.id})">Change dates / prices</button><button type="button" class="ghost" onclick="window.stayhubNoShow(${r.id})">Mark no-show</button><button type="button" class="ghost" onclick="window.stayhubCancelReservation(${r.id})">Cancel reservation</button></div>`;
      modal(`Reservation ${r.confirmation_no||r.id}`,body,async()=>{}); const form=q('opsForm'); form.querySelector('.primary').style.display='none';
    } catch(e){toast(e.message,true)}
  }

  window.stayhubCancelReservation=async id=>{try{await api(`/reservations/${id}`,{method:'PUT',body:JSON.stringify({status:'CANCELLED'})});q('opsModal')?.remove();toast('Reservation cancelled');enhancedLoadData()}catch(e){toast(e.message,true)}};
  window.stayhubNoShow=async id=>{try{await api(`/reservations/${id}`,{method:'PUT',body:JSON.stringify({status:'NO_SHOW'})});q('opsModal')?.remove();toast('Reservation marked as no-show');enhancedLoadData()}catch(e){toast(e.message,true)}};
  window.stayhubChangeReservation=async id=>{const r=await api(`/reservations/${id}`);q('opsModal')?.remove();modal('Change reservation',field('Check-in','check_in',r.check_in,'date','required')+field('Check-out','check_out',r.check_out,'date','required')+field('Room Rate','room_rate',r.room_rate,'number','min="0" step="0.01"')+field('Discount','discount',r.discount,'number','min="0" step="0.01"')+field('Tax','tax',r.tax,'number','min="0" step="0.01"')+field('Remarks','remarks',r.remarks||''),async f=>{await api(`/reservations/${id}`,{method:'PUT',body:JSON.stringify({check_in:f.get('check_in'),check_out:f.get('check_out'),room_rate:Number(f.get('room_rate')),discount:Number(f.get('discount')),tax:Number(f.get('tax')),remarks:f.get('remarks')||null})})})};

  async function addRoomType() {
    modal('Add Room Type', field('Name','name') + field('Max Adults','max_adults',2,'number','min="1"') + field('Max Children','max_children',0,'number','min="0"') + field('Base Price','base_price',0,'number','min="0" step="0.01"'), async f => { await api(`/room-types/hotel/${hotel()}`, {method:'POST', body:JSON.stringify({name:f.get('name'), max_adults:Number(f.get('max_adults')), max_children:Number(f.get('max_children')), base_price:Number(f.get('base_price'))})}); });
  }
  async function addRoom() {
    const types=await api(`/room-types/hotel/${hotel()}`); if(!types.length)return toast('Create a room type first.',true); const options=types.map(t=>`<option value="${t.id}">${esc(t.name)}</option>`).join('');
    modal('Add Room',`<label style="display:grid;gap:6px"><span style="font-size:13px;font-weight:700;color:#475569">Room Type</span><select class="select full" name="room_type_id">${options}</select></label>`+field('Room Number','room_number')+field('Floor','floor',0,'number','min="0"')+`<label style="display:flex;gap:8px;align-items:center"><input type="checkbox" name="smoking"> Smoking</label>`,async f=>{await api(`/rooms/room-type/${f.get('room_type_id')}`,{method:'POST',body:JSON.stringify({room_number:f.get('room_number'),floor:Number(f.get('floor')),smoking:f.get('smoking')==='on',active:true,status:'Available'})})});
  }
  async function addReservation() {
    const [guests,rooms]=await Promise.all([api(`/guests/hotel/${hotel()}`),api(`/rooms/hotel/${hotel()}`)]); if(!guests.length||!rooms.length)return toast('You need at least one guest and one room.',true);
    const guestOptions=guests.map(g=>`<option value="${g.id}">${esc(g.first_name+' '+g.last_name)} · ${esc(g.phone)}</option>`).join(''); const roomOptions=rooms.map(r=>`<option value="${r.id}">${esc(r.room_number)} · ${esc(r.status)}</option>`).join('');
    modal('New Reservation',`<label style="display:grid;gap:6px"><span style="font-size:13px;font-weight:700;color:#475569">Guest</span><select class="select full" name="guest_id">${guestOptions}</select></label><label style="display:grid;gap:6px"><span style="font-size:13px;font-weight:700;color:#475569">Room</span><select class="select full" name="room_id">${roomOptions}</select></label>`+field('Check-in','check_in','','date','required')+field('Check-out','check_out','','date','required')+field('Adults','adults',1,'number','min="1"')+field('Children','children',0,'number','min="0"')+field('Room Rate','room_rate',0,'number','min="0" step="0.01"')+field('Discount','discount',0,'number','min="0" step="0.01"')+field('Tax','tax',0,'number','min="0" step="0.01"')+field('Remarks','remarks'),async f=>{await api(`/reservations/hotel/${hotel()}`,{method:'POST',body:JSON.stringify({guest_id:Number(f.get('guest_id')),room_id:Number(f.get('room_id')),booking_source:'WALK_IN',check_in:f.get('check_in'),check_out:f.get('check_out'),adults:Number(f.get('adults')),children:Number(f.get('children')),room_rate:Number(f.get('room_rate')),discount:Number(f.get('discount')),tax:Number(f.get('tax')),remarks:f.get('remarks')||null})})});
  }

  function injectActions(){[['roomtypes','Add Room Type',addRoomType],['rooms','Add Room',addRoom],['reservations','New Reservation',addReservation]].forEach(([id,label,fn])=>{const head=document.querySelector(`#${id} .page-head`);if(!head||head.querySelector('.ops-action'))return;const b=document.createElement('button');b.className='primary ops-action';b.textContent=label;b.onclick=fn;head.appendChild(b)});const rates=document.querySelector('#rates .page-head');if(rates&&!rates.querySelector('.ops-action')){const b=document.createElement('button');b.className='primary ops-action';b.textContent='Refresh Rates';b.onclick=()=>enhancedLoadData();rates.appendChild(b)}}
  function addTableActions(){const style=document.createElement('style');style.textContent='.ops-action{margin-left:auto}.reservation-tools .input,.reservation-tools .select{min-width:0}.ops-row-actions{display:flex;gap:6px;flex-wrap:wrap}@media(max-width:900px){.reservation-tools{grid-template-columns:1fr!important}}';document.head.appendChild(style)}
  window.loadData=enhancedLoadData;
  const boot=()=>{addTableActions();injectActions();setTimeout(enhancedLoadData,200)};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>setTimeout(boot,150));else setTimeout(boot,150);
})();
