(() => {
  'use strict';

  const fix = () => {
    const select = document.getElementById('shStatus');
    if (select) {
      [...select.options].forEach(option => {
        if (option.value === 'ok' || option.textContent.trim().toLowerCase() === 'ok') {
          if (option.textContent !== 'Confirm') option.textContent = 'Confirm';
        }
      });
    }

    const reservationDate = document.getElementById('reservationDate');
    if (reservationDate) reservationDate.style.display = 'none';
  };

  const loadNoShowDetailFallback = () => {
    if (document.querySelector('script[data-sh-no-show-detail-fallback]')) return;
    const script = document.createElement('script');
    script.src = '/static/owner-no-show-detail-ui.js?v=1';
    script.dataset.shNoShowDetailFallback = '1';
    document.head.appendChild(script);
  };

  const init = () => {
    fix();
    loadNoShowDetailFallback();
    const observer = new MutationObserver(() => {
      observer.disconnect();
      fix();
      loadNoShowDetailFallback();
      observer.observe(document.body, { childList: true, subtree: true });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
