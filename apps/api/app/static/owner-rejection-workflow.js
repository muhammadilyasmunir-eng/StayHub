(() => {
  const token = () => localStorage.getItem('stayhub_token') || '';
  const $ = (id) => document.getElementById(id);
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));

  async function api(url, options = {}) {
    const headers = {...(options.headers || {}), Authorization: `Bearer ${token()}`};
    if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
    const r = await fetch(url, {...options, headers});
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.detail || 'Request failed');
    return d;
  }

  function openEdit(hotel) {
    if (!hotel || !hotel.id) { alert('Property information is not available. Please refresh the page.'); return; }
    let modal = $('stayhubRejectEditModal');
    if (modal) modal.remove();
    modal = document.createElement('div');
    modal.id = 'stayhubRejectEditModal';
    modal.style.cssText = 'position:fixed;inset:0;background:#020617aa;z-index:100000;display:grid;place-items:center;padding:20px;overflow:auto';
    modal.innerHTML = `<div style="background:white;width:min(760px,100%);max-height:92vh;overflow:auto;border-radius:18px;padding:24px">
      <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">Edit & Resubmit Property</h2><button id="stayhubEditClose" type="button">✕</button></div>
      <p style="color:#64748b">Correct the information requested by Admin, save it, then use <b>Submit Again for Review</b>.</p>
      <form id="stayhubRejectEditForm" style="display:grid;gap:12px">
        <label>Name<input name="name" value="${esc(hotel.name)}" required style="width:100%;padding:10px"></label>
        <label>Slug<input name="slug" value="${esc(hotel.slug)}" required style="width:100%;padding:10px"></label>
        <label>Email<input name="email" type="email" value="${esc(hotel.email)}" required style="width:100%;padding:10px"></label>
        <label>Phone<input name="phone" value="${esc(hotel.phone)}" required style="width:100%;padding:10px"></label>
        <label>Country<input name="country" value="${esc(hotel.country)}" required style="width:100%;padding:10px"></label>
        <label>City<input name="city" value="${esc(hotel.city)}" required style="width:100%;padding:10px"></label>
        <label>Address<textarea name="address" required style="width:100%;padding:10px;min-height:80px">${esc(hotel.address)}</textarea></label>
        <label>Timezone<input name="timezone" value="${esc(hotel.timezone || 'Asia/Karachi')}" style="width:100%;padding:10px"></label>
        <label>Currency<input name="currency" value="${esc(hotel.currency || 'PKR')}" style="width:100%;padding:10px"></label>
        <div style="display:flex;justify-content:flex-end;gap:10px"><button id="stayhubEditCancel" type="button">Cancel</button><button type="submit" class="btn">Save Changes</button></div>
      </form>
    </div>`;
    document.body.appendChild(modal);
    const close = () => modal.remove();
    $('stayhubEditClose').onclick = close;
    $('stayhubEditCancel').onclick = close;
    $('stayhubRejectEditForm').onsubmit = async (e) => {
      e.preventDefault();
      const f = new FormData(e.target);
      const body = Object.fromEntries(f.entries());
      try {
        await api(`/hotels/${hotel.id}`, {method:'PUT', body:JSON.stringify(body)});
        modal.remove();
        alert('Changes saved. Now click Submit Again for Review.');
        await refresh();
      } catch (err) { alert(err.message); }
    };
  }

  window.stayhubOpenRejectedEdit = openEdit;

  function showNotice(hotel) {
    let box = $('stayhubRejectionNotice');
    if (!box) {
      box = document.createElement('div');
      box.id = 'stayhubRejectionNotice';
      const main = document.querySelector('main') || document.body;
      main.insertBefore(box, main.firstChild);
    }
    if (!hotel || String(hotel.status).toUpperCase() !== 'REJECTED') {
      box.innerHTML = '';
      return;
    }
    box.innerHTML = `<div style="background:#fff1f2;border:1px solid #fecdd3;border-left:5px solid #e11d48;border-radius:14px;padding:18px;margin-bottom:18px;color:#881337">
      <div style="font-size:18px;font-weight:800">Property Rejected — Action Required</div>
      <div style="margin-top:7px">StayHub Admin has requested changes to <b>${esc(hotel.name)}</b>.</div>
      <div style="margin-top:9px;background:white;border-radius:10px;padding:12px"><b>Admin reason:</b><br>${esc(hotel.rejection_reason || 'Please review your property details and correct the required information.')}</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:13px">
        <button id="stayhubEditRejected" class="btn" type="button">Edit Property</button>
        <button id="stayhubResubmit" class="btn" type="button" style="background:#059669">Submit Again for Review</button>
      </div>
      <div style="font-size:12px;margin-top:9px;color:#9f1239">After correcting the requested information, submit again. The property will return to Pending and will not be public until approved.</div>
    </div>`;

    const editButton = $('stayhubEditRejected');
    if (editButton) {
      editButton.onclick = (event) => {
        event.preventDefault();
        event.stopPropagation();
        openEdit(hotel);
      };
    }

    const resubmitButton = $('stayhubResubmit');
    if (resubmitButton) resubmitButton.onclick = async (event) => {
      event.preventDefault();
      if (!confirm('Have you reviewed and corrected the requested information? Submit this property again for Admin review?')) return;
      try {
        await api(`/hotels/${hotel.id}/resubmit`, {method:'POST'});
        alert('Property submitted successfully. It is now Pending Admin review.');
        location.reload();
      } catch (e) { alert(e.message); }
    };
  }

  async function refresh() {
    if (!token()) return;
    try {
      const hotels = await api('/hotels/');
      const selected = localStorage.getItem('stayhub_hotel_id');
      const hotel = hotels.find(h => String(h.id) === String(selected)) || hotels.find(h => String(h.status).toUpperCase() === 'REJECTED');
      showNotice(hotel);
    } catch (_) {}
  }

  window.setTimeout(refresh, 700);
  window.addEventListener('load', () => window.setTimeout(refresh, 500));
})();