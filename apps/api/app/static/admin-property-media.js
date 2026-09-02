(() => {
  const attachUploader = () => {
    const detail = document.getElementById('detail');
    if (!detail || detail.dataset.mediaReady === '1' || typeof window.renderDetail !== 'function') return;
    detail.dataset.mediaReady = '1';
  };

  const originalRenderDetail = window.renderDetail;
  if (typeof originalRenderDetail === 'function') {
    window.renderDetail = function (edit) {
      originalRenderDetail(edit);
      const detail = document.getElementById('detail');
      if (!detail || edit || typeof selected === 'undefined' || !selected) return;
      if (detail.querySelector('[data-building-upload]')) return;

      const section = document.createElement('div');
      section.setAttribute('data-building-upload', '1');
      section.style.cssText = 'margin-top:18px;padding:16px;border:1px solid #d9e0e7;border-radius:12px;background:#f8fafc';
      section.innerHTML = `
        <h3 class="section-title" style="margin-top:0">Building Photo</h3>
        <p class="muted" style="margin:0 0 10px">Upload the property's real building image. JPG, PNG, WEBP or GIF, maximum 10 MB.</p>
        <input id="buildingPhotoFile" type="file" accept="image/jpeg,image/png,image/webp,image/gif" class="input full">
        <button id="buildingPhotoUpload" class="primary" style="margin-top:10px">Upload Building Photo</button>
        <div id="buildingPhotoMessage" class="muted" style="margin-top:8px"></div>`;
      detail.appendChild(section);

      document.getElementById('buildingPhotoUpload').onclick = async () => {
        const file = document.getElementById('buildingPhotoFile').files[0];
        const message = document.getElementById('buildingPhotoMessage');
        if (!file) { message.textContent = 'Please select an image first.'; return; }
        const token = localStorage.getItem('stayhub_admin_token');
        const body = new FormData();
        body.append('file', file);
        message.textContent = 'Uploading...';
        try {
          const response = await fetch(`/uploads/hotel/${selected}/building`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            body,
          });
          const data = await response.json().catch(() => ({}));
          if (!response.ok) throw new Error(data.detail || 'Upload failed');
          message.textContent = 'Building photo uploaded successfully.';
          if (typeof inspect === 'function') await inspect(selected);
        } catch (error) {
          message.textContent = error.message;
        }
      };
    };
  }

  attachUploader();
})();
