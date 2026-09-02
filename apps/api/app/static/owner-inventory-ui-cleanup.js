(() => {
  'use strict';

  const normalize = v => String(v || '').replace(/\s+/g, ' ').trim().toLowerCase();

  function removeAddRoom() {
    document.querySelectorAll('button, a').forEach(el => {
      const text = normalize(el.textContent);
      if (text === 'add room' || text === '+ add room' || text === '＋ add room') {
        el.remove();
      }
    });
  }

  function removeCalendarInventoryLabels() {
    const targets = new Set(['selected dates', 'rooms to sell', 'rate (pkr)']);
    document.querySelectorAll('th, td, label, span, div, p, strong, b').forEach(el => {
      if (targets.has(normalize(el.textContent))) {
        // Only remove the label itself; do not remove a larger table/container.
        if (el.children.length === 0) el.remove();
      }
    });
  }

  function clean() {
    removeAddRoom();
    removeCalendarInventoryLabels();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', clean, { once: true });
  } else clean();

  const observer = new MutationObserver(clean);
  observer.observe(document.documentElement, { childList: true, subtree: true });
})();
