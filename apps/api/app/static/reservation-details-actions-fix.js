(() => {
  const token = () => localStorage.getItem('stayhub_token') || '';
  const adminToken = () => localStorage.getItem('stayhub_admin_token') || '';
  const api = async (url, options = {}, admin = false) => {
    const r = await fetch(url, { ...options, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${admin ? adminToken() : token()}`, ...(options.headers || {}) } });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.detail || 'Request failed');
    return d;
  };
  const esc = v => String(v ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
  let lastReservationId = null;
  let lastReservation = null;
  const isAdmin = () => !!document.getElementById('portal');

  function style() {
    if (document.getElementById('shDetailActionFixStyle')) return;
    const s = document.createElement('style'); s.id='shDetailActionFixStyle';
    s.textContent = `.sh-detail-actions-fix{margin:20px 24px;padding:16px;border:1px solid #e2e8f0;border-radius:12px;background:#f8fafc;display:flex;gap:10px;flex-wrap:wrap}.sh-detail-actions-fix .shd-title{width:100%;font-weight:800;font-size:13px}.shd-btn{height:40px;border:1px solid #d0d5dd;background:#fff;border-radius:8px;padding:0 14px;font-weight:750;cursor:pointer}.shd-btn.primary{background:#2563eb;color:#fff;border-color:#2563eb}.shd-btn.danger{color:#b91c1c}.shd-btn.disabled{opacity:.42;cursor:not-allowed}.sh-no-show-window{width:100%;font-size:12px;color:#667085}`;
    document.head.appendChild(s);
  }

  function popup(title, body, buttons) {
    document.getElementById('shDetailActionPopup')?.remove();
    const o=document.createElement('div'); o.id='shDetailActionPopup'; o.style.cssText='position:fixed;inset:0;background:rgba(15,23,42,.62);z-index:50000;display:flex;align-items:center;justify-content:center;padding:20px';
    o.innerHTML=`<div style="width:min(560px,100%);background:#fff;border-radius:16px;padding:24px;box-shadow:0 25px 80px rgba(0,0,0,.3)"><h2 style="margin:0 0 14px">${esc(title)}</h2><div>${body}</div><div style="display:flex;justify-content:flex-end;gap:8px;margin-top:22px">${buttons}</div></div>`;
    document.body.appendChild(o); return o;
  }
  const closePopup=()=>document.getElementById('shDetailActionPopup')?.remove();

  async function refresh(){ closePopup(); document.getElementById('shManageModal')?.remove(); window.location.reload(); }

  function openNoShow(res, admin=false){
    const p=popup('Mark as no-show',`<p><b>${esc(res.room_type_name||'Room')}</b></p><p>Do you want to waive the no-show fee for this reservation?</p><div style="display:grid;gap:10px"><button id="nsw" class="shd-btn" style="height:auto;text-align:left;padding:12px"><b>Yes, waive fee</b><br><small>No commission will be charged.</small></button><button id="nsc" class="shd-btn" style="height:auto;text-align:left;padding:12px"><b>No, charge fee</b><br><small>Only the first night's commission will be charged.</small></button></div><p style="font-size:12px;color:#667085;border-top:1px solid #e5e7eb;padding-top:12px">We'll let the guests know accordingly.</p><p style="font-size:12px;color:#667085">If you charge a cancellation or no-show fee for any reservation, StayHub will charge commission on this fee.</p>`,`<button id="nscancel" class="shd-btn">Cancel</button><button id="nsmark" class="shd-btn primary" disabled>Mark as no-show</button>`);
    let waive=null; const mark=p.querySelector('#nsmark');
    p.querySelector('#nsw').onclick=()=>{waive=true;mark.disabled=false;p.querySelector('#nsw').style.borderColor='#2563eb'};
    p.querySelector('#nsc').onclick=()=>{waive=false;mark.disabled=false;p.querySelector('#nsc').style.borderColor='#2563eb'};
    p.querySelector('#nscancel').onclick=closePopup;
    mark.onclick=async()=>{if(waive===null)return;try{await api(admin?`/admin/reservations/${res.id}/no-show`:`/reservations/${res.id}/owner/no-show`,{method:'POST',body:JSON.stringify({waive_fee:waive})},admin);refresh()}catch(e){alert(e.message)}};
  }

  function openModify(res, admin=false){
    const p=popup('Reservation modification',`<p style="color:#475467">${admin?'Admin can change the reservation dates.':'Owner can change the dates only while the stay is active.'}</p><div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><label>Check-in<input id="mdci" type="date" value="${esc(String(res.check_in).slice(0,10))}" style="display:block;width:100%;box-sizing:border-box;height:42px;margin-top:5px;padding:8px"></label><label>Check-out<input id="mdco" type="date" value="${esc(String(res.check_out).slice(0,10))}" style="display:block;width:100%;box-sizing:border-box;height:42px;margin-top:5px"></label></div>`,`<button id="mdc" class="shd-btn">Cancel</button><button id="mds" class="shd-btn primary">Save changes</button>`);
    p.querySelector('#mdc').onclick=closePopup;
    p.querySelector('#mds').onclick=async()=>{try{await api(admin?`/admin/reservations/${res.id}/modify`:`/reservations/${res.id}/owner/modify`,{method:'POST',body:JSON.stringify({check_in:p.querySelector('#mdci').value,check_out:p.querySelector('#mdco').value})},admin);refresh()}catch(e){alert(e.message)}};
  }

  async function addOwnerDetailActions(res){
    const modal=document.getElementById('stayhubReservationDetailFix'); if(!modal)return;
    document.querySelector('.sh-detail-actions-fix')?.remove();
    const bar=document.createElement('div'); bar.className='sh-detail-actions-fix';
    const mod=!!res.modification_allowed, ns=!!res.no_show_allowed;
    bar.innerHTML=`<div class="shd-title">Reservation actions</div><button id="dmod" class="shd-btn primary ${mod?'':'disabled'}" ${mod?'':'disabled'}>Modify reservation</button><button id="dns" class="shd-btn ${ns?'':'disabled'}" ${ns?'':'disabled'}>No-Show</button><button id="dcan" class="shd-btn danger">Cancel reservation</button><div class="sh-no-show-window">No-Show is available only from checkout at 12:00 PM until 48 hours after checkout.</div>`;
    modal.appendChild(bar);
    bar.querySelector('#dmod').onclick=()=>openModify(res,false); bar.querySelector('#dns').onclick=()=>openNoShow(res,false);
    bar.querySelector('#dcan').onclick=async()=>{if(!confirm('Cancel this reservation?'))return;try{await api(`/reservations/${res.id}`,{method:'DELETE'});refresh()}catch(e){alert(e.message)}};
  }

  function removeOwnerListActions(){ document.querySelectorAll('#reservationTable .sh-actions-cell,.sh-actions-head').forEach(x=>x.remove()); }

  async function captureReservation(e){
    const row=e.target.closest?.('#resBody tr[data-res-id]'); if(!row)return;
    lastReservationId=Number(row.dataset.resId);
    try{lastReservation=await api(`/reservations/${lastReservationId}`)}catch(_){lastReservation=null}
    setTimeout(()=>{if(lastReservation)addOwnerDetailActions(lastReservation)},150);
  }

  async function adminRow(e){
    const row=e.target.closest?.('#shAdminRows tr[data-id]'); if(!row)return;
    const id=Number(row.dataset.id); setTimeout(async()=>{try{const res=await api(`/admin/reservations/${id}`,{},true); addAdminDetailActions(res)}catch(err){console.error(err)}},100);
  }

  function addAdminDetailActions(res){
    const modal=document.getElementById('shManageModal'); if(!modal)return;
    document.querySelector('.sh-detail-actions-fix')?.remove();
    const old=modal.querySelector('#shAdminActionBar'); if(old)old.remove();
    const bar=document.createElement('div');bar.className='sh-detail-actions-fix';
    const isNo=String(res.status||'').toUpperCase()==='NO_SHOW';
    bar.innerHTML=`<div class="shd-title">Reservation actions</div><button id="adm" class="shd-btn primary">Modify reservation</button><button id="adns" class="shd-btn">No-Show</button><button id="adcf" class="shd-btn ${isNo?'':'disabled'}" ${isNo?'':'disabled'}>Confirm reservation</button><button id="adcan" class="shd-btn danger">Cancel reservation</button>`;
    modal.appendChild(bar);
    bar.querySelector('#adm').onclick=()=>openModify(res,true); bar.querySelector('#adns').onclick=()=>openNoShow(res,true);
    bar.querySelector('#adcf').onclick=async()=>{try{await api(`/admin/reservations/${res.id}/confirm`,{method:'POST'},true);refresh()}catch(e){alert(e.message)}};
    bar.querySelector('#adcan').onclick=async()=>{if(!confirm('Cancel this reservation?'))return;try{await api(`/admin/reservations/${res.id}/cancel`,{method:'POST'},true);refresh()}catch(e){alert(e.message)}};
  }

  function init(){style();removeOwnerListActions();new MutationObserver(removeOwnerListActions).observe(document.body,{childList:true,subtree:true});}
  document.addEventListener('click',e=>{captureReservation(e);adminRow(e)},true);
  document.addEventListener('DOMContentLoaded',init);setTimeout(init,300);
})();