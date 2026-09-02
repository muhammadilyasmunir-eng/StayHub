(() => {
  const token = () => localStorage.getItem('stayhub_token') || '';
  const esc = v => String(v ?? '').replace(/[&<>\"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#039;'}[m]));
  const api = async (url, options = {}) => {
    const headers = {...(options.headers || {}), Authorization: `Bearer ${token()}`};
    if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
    const r = await fetch(url, {...options, headers});
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.detail || 'Request failed');
    return d;
  };

  function renderRejected(hotels) {
    let box = document.getElementById('stayhubRejectionNotice');
    if (!box) {
      box = document.createElement('div'); box.id = 'stayhubRejectionNotice';
      const main = document.querySelector('main') || document.body; main.insertBefore(box, main.firstChild);
    }
    const rejected = (hotels || []).filter(h => String(h.status || '').toUpperCase() === 'REJECTED');
    box.innerHTML = rejected.map(h => `<div style="background:#fff1f2;border:1px solid #fecdd3;border-left:5px solid #e11d48;border-radius:14px;padding:18px;margin-bottom:18px;color:#881337">
      <div style="font-size:18px;font-weight:800">Property Rejected — Action Required</div>
      <div style="margin-top:7px"><b>${esc(h.name)}</b> · Property ID ${esc(h.property_id || '—')}</div>
      <div style="margin-top:9px;background:#fff;border-radius:10px;padding:12px"><b>Admin rejection message:</b><br>${esc(h.rejection_reason || 'Please review your property details and correct the required information.')}</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:13px"><button class="btn" data-reject-edit="${esc(h.id)}" type="button">Edit Property</button><button class="btn" data-reject-submit="${esc(h.id)}" type="button" style="background:#059669">Submit Again for Review</button></div>
      <div style="font-size:12px;margin-top:9px;color:#9f1239">After correcting the requested information, submit again. The property will return to Pending and will not be public until approved.</div>
    </div>`).join('');
    box.querySelectorAll('[data-reject-edit]').forEach(b => b.onclick = () => {
      const id = b.dataset.rejectEdit;
      localStorage.setItem('stayhub_hotel_id', id);
      location.href = `/list-your-property?edit_hotel_id=${encodeURIComponent(id)}`;
    });
    box.querySelectorAll('[data-reject-submit]').forEach(b => b.onclick = async () => {
      if (!confirm('Submit this property again for Admin review?')) return;
      try { await api(`/hotels/${b.dataset.rejectSubmit}/resubmit`, {method:'POST'}); alert('Property submitted successfully. It is now Pending Admin review.'); location.reload(); }
      catch(e) { alert(e.message); }
    });
  }

  async function refresh() {
    if (!token()) return;
    try { renderRejected(await api('/hotels/')); } catch (_) {}
  }
  setTimeout(refresh, 1000);
  window.addEventListener('load', () => setTimeout(refresh, 600));
})();
