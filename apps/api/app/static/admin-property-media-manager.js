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
  const imageAccept = 'image/jpeg,image/png,image/webp,image/gif';

  function mediaPreview(url, title) {
    if (!url) return '<div class="muted">Not uploaded</div>';
    const safe = esc(url);
    return `<div style="margin-top:8px"><a href="${safe}" target="_blank" rel="noopener">${isImage(url) ? `<img src="${safe}" alt="${esc(title)}" style="display:block;max-width:520px;max-height:320px;width:auto;height:auto;object-fit:contain;border:1px solid #d9e0e7;border-radius:10px;background:#fff">` : esc(title)}</a><div style="margin-top:7px"><a href="${safe}" target="_blank" rel="noopener">View / Open</a></div></div>`;
  }

  function fileControl(label, endpoint, accept, messageId, buttonLabel = 'Replace / Upload') {
    return `<div style="margin-top:10px"><label style="display:block;font-weight:600;margin-bottom:6px">${esc(label)}</label><input data-upload-file="${esc(messageId)}" type="file" accept="${accept}" class="input full"><button type="button" class="ghost" data-upload-endpoint="${esc(endpoint)}" data-upload-message="${esc(messageId)}" style="margin-top:8px">${esc(buttonLabel)}</button><span data-upload-status="${esc(messageId)}" class="muted" style="margin-left:10px"></span></div>`;
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
    wrap.className = 'kv property-photo-card';
    wrap.style.cssText = 'display:block;padding:14px;position:relative';
    const title = photo.caption || photo.category || `Property Photo ${index + 1}`;
    const main = !!photo.is_primary;
    const replace = photo.id ? fileControl('Replace photo', `/uploads/hotel/${hotelId}/photo/${photo.id}`, imageAccept, `photo-${hotelId}-${photo.id}`) : '';
    const controls = photo.id ? `<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px"><button type="button" class="ghost" data-set-primary="${photo.id}">${main ? '✓ Building / Main Photo' : 'Set as Building / Main Photo'}</button><button type="button" class="ghost danger" data-delete-photo="${photo.id}">Remove</button></div>` : '';
    wrap.innerHTML = `<b>${esc(title)}</b>${main ? '<span class="badge approved" style="margin-left:8px">BUILDING / MAIN</span>' : ''}${mediaPreview(photo.url, title)}${replace}${controls}`;
    return wrap;
  }

  function addNewPhotoControl(grid, hotelId, photoCount) {
    if (grid.querySelector('[data-add-property-photo]')) return;
    const box = document.createElement('div');
    box.dataset.addPropertyPhoto = '1';
    box.style.cssText = 'grid-column:1/-1;margin-top:4px;padding:16px;border:1px dashed #9fc8c1;border-radius:14px;background:#f7faf9';
    box.innerHTML = `<b>Add Property Photo</b><p class="muted" style="margin:5px 0 8px">Upload additional building/property photos. JPG, PNG, WEBP or GIF, maximum 10 MB each. Maximum 50 photos total.</p><div class="muted" style="margin-bottom:8px"><strong>${photoCount}/50</strong> photos uploaded. Upload any number up to the 50-photo limit, then select one as Building / Main Photo.</div>${fileControl('New property photo', `/uploads/hotel/${hotelId}/photo`, imageAccept, `new-photo-${hotelId}`, 'Upload Photo')}`;
    grid.appendChild(box);
  }

  function addTabs(root) {
    if (root.querySelector('[data-property-tabs]')) return;
    const headings = [...root.querySelectorAll('.section-title')];
    if (!headings.length) return;
    const tabs = document.createElement('div');
    tabs.dataset.propertyTabs = '1';
    tabs.style.cssText = 'display:flex;gap:8px;flex-wrap:wrap;margin:0 0 18px;padding:6px;background:#edf6f4;border:1px solid #dbe7e5;border-radius:12px;position:sticky;top:8px;z-index:5';
    headings.forEach((heading, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'ghost';
      button.textContent = heading.textContent.trim();
      button.dataset.tabIndex = String(index);
      button.style.cssText = 'border-radius:9px;padding:9px 12px';
      button.onclick = () => {
        headings.forEach((h, i) => {
          const content = h.nextElementSibling;
          if (content) content.style.display = i === index ? '' : 'none';
          const b = tabs.querySelector(`[data-tab-index="${i}"]`);
          if (b) b.classList.toggle('primary', i === index);
          if (b) b.classList.toggle('ghost', i !== index);
        });
      };
      tabs.appendChild(button);
    });
    root.insertBefore(tabs, headings[0]);
    tabs.querySelector('[data-tab-index="0"]')?.click();
  }

  function wireUploads(root) {
    root.querySelectorAll('[data-upload-endpoint]').forEach(btn => {
      if (btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';
      btn.addEventListener('click', async () => {
        const id = btn.dataset.uploadMessage;
        const input = root.querySelector(`[data-upload-file="${CSS.escape(id)}"]`);
        const status = root.querySelector(`[data-upload-status="${CSS.escape(id)}"]`);
        await upload(btn.dataset.uploadEndpoint, input?.files?.[0], status, async () => {
          if (typeof window.stayhubOpenProperty === 'function' && root.dataset.mediaRefresh !== '1') {
            root.dataset.mediaRefresh = '1';
            try { await window.stayhubOpenProperty(Number(root.dataset.hotelId)); } finally { root.dataset.mediaRefresh = '0'; }
          }
        });
      });
    });

    root.querySelectorAll('[data-set-primary]').forEach(btn => {
      if (btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';
      btn.addEventListener('click', async () => {
        try {
          await req(`/uploads/hotel/${root.dataset.hotelId}/photo/${btn.dataset.setPrimary}/primary`, {method:'POST'});
          await window.stayhubOpenProperty(Number(root.dataset.hotelId));
        } catch (e) { alert(e.message); }
      });
    });

    root.querySelectorAll('[data-delete-photo]').forEach(btn => {
      if (btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';
      btn.addEventListener('click', async () => {
        if (!confirm('Remove this property photo?')) return;
        try {
          await req(`/uploads/hotel/${root.dataset.hotelId}/photo/${btn.dataset.deletePhoto}`, {method:'DELETE'});
          await window.stayhubOpenProperty(Number(root.dataset.hotelId));
        } catch (e) { alert(e.message); }
      });
    });
  }

  function enhance(h) {
    const root = document.getElementById('finalReviewDetail');
    if (!root || !h) return;
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
      const photoCount = Array.isArray(h.photos) ? h.photos.length : 0;
      (h.photos || []).sort((a,b) => Number(b.is_primary) - Number(a.is_primary) || Number(a.sort_order || 0) - Number(b.sort_order || 0)).forEach((photo, i) => photos.appendChild(buildPhotoCard(photo, h.id, i)));
      addNewPhotoControl(photos, h.id, photoCount);
      if (!photoCount) photos.insertAdjacentHTML('afterbegin','<span class="muted">No property photos provided.</span>');
    }
    addTabs(root);
    wireUploads(root);
  }

  const original = window.stayhubOpenProperty;
  if (typeof original !== 'function') return;
  window.stayhubOpenProperty = async id => {
    await original(id);
    try {
      const h = await req('/admin/hotels/' + id);
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
