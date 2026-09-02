(() => {
  'use strict';

  const pad = n => String(n).padStart(2, '0');
  const localDate = (offsetDays = 0) => {
    const d = new Date();
    d.setHours(12, 0, 0, 0);
    d.setDate(d.getDate() + offsetDays);
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  };

  const isCheckout = input => {
    const text = [
      input.getAttribute('aria-label') || '',
      input.getAttribute('placeholder') || '',
      input.id || '',
      input.name || '',
      input.closest('label')?.textContent || ''
    ].join(' ').toLowerCase();
    return /check\s*[- ]?out|checkout|departure|end\s*date/.test(text);
  };

  const openPickerFromField = event => {
    const input = event.currentTarget;
    if (!input || input.disabled || input.readOnly) return;

    // Keep the native calendar icon from opening the picker by itself.
    // Clicking anywhere else in the date field opens the picker.
    const rect = input.getBoundingClientRect();
    const iconZone = Math.max(28, Math.min(44, rect.width * 0.15));
    if (event.clientX >= rect.right - iconZone) {
      event.preventDefault();
      event.stopPropagation();
      return;
    }

    if (typeof input.showPicker === 'function') {
      event.preventDefault();
      try { input.showPicker(); } catch (_) {}
    }
  };

  const setDefault = input => {
    if (!input || input.type !== 'date' || input.disabled || input.readOnly) return;
    if (!input.value) input.value = localDate(isCheckout(input) ? 1 : 0);
    if (input.dataset.shDateDefaultsBound === '1') return;
    input.dataset.shDateDefaultsBound = '1';
    input.addEventListener('click', openPickerFromField);
  };

  const scan = root => {
    (root || document).querySelectorAll?.('input[type="date"]').forEach(setDefault);
  };

  const init = () => {
    scan(document);
    const observer = new MutationObserver(records => {
      records.forEach(record => record.addedNodes.forEach(node => {
        if (node.nodeType === 1) {
          if (node.matches?.('input[type="date"]')) setDefault(node);
          scan(node);
        }
      }));
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
