(() => {
  const token = () => localStorage.getItem('stayhub_admin_token') || '';
  const esc = x => String(x ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
  const req = async (url, opt = {}) => {
    opt.headers = {...(opt.headers || {}), Authorization: 'Bearer ' + token()};
    const r = await fetch(url, opt);
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw Error(d.detail || 'Request failed');
    return d;
  };
  const isImage = url => /\.(jpg|jpeg|png|gif|webp|bmp|svg)(\?|#|$)/i.test(String(url || ''));

  function mediaPreview(url, title) {
    if (!url) return '<div class="muted">Not uploaded</div>';
    const safe = esc(url);
    return `<div style="margin-top:8px"><a href="${safe}" target="_blank" rel="noopener">${isImage(url) ? `<img src="${safe}" alt="${esc(title)}" style="display:block;max-width:520px;max-height:320px;width:auto;height:auto;object-fit:contain;border:1px solid #d9e0e7;border-radius:10px;background:#fff">` : esc(title)}</a><div style="margin-top:7px"><a href="${safe}" target="_blank" rel="noopener">View / Open</a></div></div>`;
  }

  function fileControl(label, endpoint, accept, messageId) {
    return `<div style="margin-top:10px"><label style="display:block;font-weight:600;margin-bottom:6px">${esc(label)}</label><input data-upload-file="${esc(messageId)}" type="file" accept="${accept}" class="input full"><button type="button" class="ghost" data-upload-endpoint="${esc(endpoint)}" data-upload-message="${esc(messageId)}" style="margin-top:8px">Replace / Upload</button><span data-upload-status="${esc(messageId)}" class="muted" style="margin-left:10px"></span></div>`;
  }

  async function upload(endpoint, file, statusEl, after) {
    if (!file) { statusEl.textContent = 'Select a file first.'; return; }
    const body = new FormData(); body.append('file', file);
    statusEl.textContent = 'Uploading...';
    try {
      await req(endpoint, {method:'POST', body});
      statusEl.textContent = 'Updated successfully.';
      if (after) await after();
    } catch (e) { statusEl.textContent = e.message; }
  }

  function getSection(root, title) {
    const h = [...root.querySelectorAll('.section-title')].find(x => String(x.textContent || '').trim().toLowerCase() === title.toLowerCase());
    return h ? h.nextElementSibling : null;
  }

  function buildDocumentCard(doc, hotelId, index) {
    const title = doc.type || 'Registration Document';
    const endpoint = `/uploads/hotel/${hotelId}/document/${doc.id}`;
    const id = `reg-${hotelId}-${doc.id || index}`;
    const wrap = document.createElement('div');
    wrap.className = 'kv';
    wrap.style.cssText = 'display:block;padding:14px';
    wrap.innerHTML = `<b>${esc(title)}</b>${mediaPreview(doc.url, title)}${fileControl('Replace document', endpoint, 'image/*,.pdf,.doc,.docx,.xls,.xlsx', id)}`;
    return wrap;
  }

  function buildOwnerCard(title, url, endpoint, id) {
    const wrap = document.createElement('div');
    wrap.className = 'kv';
    wrap.style.cssText = 'display:block;padding:14px';
    wrap.innerHTML = `<b>${esc(title)}</b>${mediaPreview(url, title)}${fileControl('Replace document', endpoint, 'image/*,.pdf,.doc,.docx,.xls,.xlsx', id)}`;
    return wrap;
  }

  function buildPhotoCard(photo, hotelId, index) {
    const wrap = document.createElement('div');
    wrap.className = 'kv';
    wrap.style.cssText = 'display:block;padding:14px';
    const title = photo.caption || photo.category || `Property Photo ${index + 1}`;
    const replace = photo.id ? fileControl('Replace photo', `/uploads/hotel/${hotelId}/photo/${photo.id}`, 'image/jpeg,image/png,image/webp,image/gif', `photo-${hotelId}-${photo.id}`) : '';
    wrap.innerHTML = `<b>${esc(title)}</b>${mediaPreview(photo.url, title)}${replace}`;
    return wrap;
  }

  function addNewPhotoControl(grid, hotelId) {
    if (grid.querySelector('[data-add-property-photo]')) return;
    const box = document.createElement('div');
    box.dataset.addPropertyPhoto = '1';
    box.style.cssText = 'grid-column:1/-1;margin-top:4px;padding:14px;border:1px dashed #cbd5e1;border-radius:12px;background:#f8fafc';
    box.innerHTML = `<b>Add Property Photo</b><p class="muted" style="margin:5px 0 8px">Upload an additional building/property photo. JPG, PNG, WEBP or GIF, maximum 10 MB.</p>${fileControl('New property photo', `/uploads/hotel/${hotelId}/building`, 'image/jpeg,image/png,image/webp,image/gif', `new-photo-${hotelId}`)}`;
    grid.appendChild(box);
  }

  function wireUploads(root) {
    root.querySelectorAll('[data-upload-endpoint]').forEach(btn => {
      if (btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';
      btn.addEventListener('click', async () => {
        const id = btn.dataset.uploadMessage;
        const input = root.querySelector(`[data-upload-file="${CSS.escape(id)}"]`);
        const status = root.querySelector(`[data-upload-status="${CSS.escape(id)}"]`);
        const endpoint = btn.dataset.uploadEndpoint;
        await upload(endpoint, input?.files?.[0], status, async () => {
          if (typeof window.stayhubOpenProperty === 'function' && root.dataset.mediaRefresh !== '1') {
            root.dataset.mediaRefresh = '1';
            try { await window.stayhubOpenProperty(Number(root.dataset.hotelId)); } finally { root.dataset.mediaRefresh = '0'; }
          }
        });
      });
    });
  }

  function enhance(h) {
    const root = document.getElementById('finalReviewDetail');
    if (!root || !h || root.dataset.mediaEnhanced === String(h.id)) return;
    root.dataset.hotelId = String(h.id);
    root.dataset.mediaEnhanced = String(h.id);

    const reg = getSection(root, 'Registration Documents');
    if (reg) {
      reg.innerHTML = '';
      (h.documents || []).forEach((doc, i) => reg.appendChild(buildDocumentCard(doc, h.id, i)));
      if (!(h.documents || []).length) reg.innerHTML = '<span class="muted">None provided</span>';
    }

    const owner = getSection(root, 'Owner Verification Documents');
    if (owner) {
      owner.innerHTML = '';
      owner.appendChild(buildOwnerCard('CNIC / Passport Front', h.owner_cnic_front_url, `/uploads/hotel/${h.id}/owner-document/cnic_front`, `cnic-front-${h.id}`));
      owner.appendChild(buildOwnerCard('CNIC / Passport Back', h.owner_cnic_back_url, `/uploads/hotel/${h.id}/owner-document/cnic_back`, `cnic-back-${h.id}`));
      owner.appendChild(buildOwnerCard('Signed Agreement', h.signed_agreement_url, `/uploads/hotel/${h.id}/owner-document/signed_agreement`, `agreement-${h.id}`));
    }

    const photos = getSection(root, 'Property Photos');
    if (photos) {
      photos.innerHTML = '';
      (h.photos || []).forEach((photo, i) => photos.appendChild(buildPhotoCard(photo, h.id, i)));
      addNewPhotoControl(photos, h.id);
      if (!(h.photos || []).length) photos.insertAdjacentHTML('afterbegin','<span class="muted">No property photos provided.</span>');
    }
    wireUploads(root);
  }

  const original = window.stayhubOpenProperty;
  if (typeof original !== 'function') return;
  window.stayhubOpenProperty = async id => {
    await original(id);
    try {
      const h = await req('/admin/hotels/' + id);
      const root = document.getElementById('finalReviewDetail');
      if (root) root.dataset.mediaEnhanced = '';
      enhance(h);
    } catch (e) { console.warn('Admin property media enhancement failed:', e); }
  };

  const observer = new MutationObserver(() => {
    const root = document.getElementById('finalReviewDetail');
    if (!root || !root.dataset.hotelId) return;
    if (root.dataset.mediaEnhanced === root.dataset.hotelId && root.querySelector('[data-upload-endpoint]')) return;
    const id = Number(root.dataset.hotelId);
    if (!Number.isFinite(id)) return;
    req('/admin/hotels/' + id).then(enhance).catch(() => {});
  });

  function init() {
    const root = document.getElementById('finalReviewDetail');
    if (root) observer.observe(root, {childList:true, subtree:true});
  }
  document.addEventListener('DOMContentLoaded', init);
  setTimeout(init, 1000);
})();
