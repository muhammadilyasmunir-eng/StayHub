(() => {
  const rootId = 'finalReviewDetail';
  const isImage = url => /\.(jpg|jpeg|png|gif|webp|bmp|svg)(\?|#|$)/i.test(String(url || ''));
  const esc = x => String(x ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));

  function ensureModal() {
    let modal = document.getElementById('stayhubMediaModal');
    if (modal) return modal;
    modal = document.createElement('div');
    modal.id = 'stayhubMediaModal';
    modal.style.cssText = 'display:none;position:fixed;inset:0;z-index:99999;background:rgba(15,23,42,.82);align-items:center;justify-content:center;padding:24px;box-sizing:border-box';
    modal.innerHTML = '<div data-media-modal-panel style="position:relative;width:min(1000px,96vw);height:min(88vh,900px);background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.35)"><button type="button" data-media-close style="position:absolute;right:12px;top:10px;z-index:2;width:36px;height:36px;border:0;border-radius:50%;background:#0f172a;color:#fff;font-size:22px;cursor:pointer">×</button><div data-media-modal-body style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;padding:50px 18px 18px;box-sizing:border-box"></div></div>';
    document.body.appendChild(modal);
    const close = () => { modal.style.display='none'; modal.querySelector('[data-media-modal-body]').innerHTML=''; };
    modal.querySelector('[data-media-close]').onclick = close;
    modal.addEventListener('click', e => { if (e.target === modal) close(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    return modal;
  }

  function openMedia(url, title) {
    const modal = ensureModal();
    const body = modal.querySelector('[data-media-modal-body]');
    if (isImage(url)) {
      body.innerHTML = `<img src="${esc(url)}" alt="${esc(title)}" style="max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain;border-radius:8px">`;
    } else if (/\.pdf(\?|#|$)/i.test(url)) {
      body.innerHTML = `<iframe src="${esc(url)}" title="${esc(title)}" style="width:100%;height:100%;border:0"></iframe>`;
    } else {
      body.innerHTML = `<div style="text-align:center"><h3>${esc(title)}</h3><p class="muted">This document format cannot be previewed inside the page.</p></div>`;
    }
    modal.style.display = 'flex';
  }

  function wire() {
    const root = document.getElementById(rootId);
    if (!root) return;
    root.querySelectorAll('a[href]').forEach(a => {
      if (a.dataset.mediaModalBound === '1') return;
      const href = a.href;
      if (!/\/static\/uploads\//.test(href)) return;
      a.dataset.mediaModalBound = '1';
      a.removeAttribute('target');
      a.removeAttribute('rel');
      a.addEventListener('click', e => { e.preventDefault(); e.stopPropagation(); openMedia(href, a.closest('.kv')?.querySelector('b')?.textContent?.trim() || 'Uploaded file'); });
    });
  }

  const observer = new MutationObserver(wire);
  document.addEventListener('DOMContentLoaded', () => { const root=document.getElementById(rootId); if(root) observer.observe(root,{childList:true,subtree:true}); wire(); });
  setTimeout(wire, 1200);
})();
