(() => {
  'use strict';
  const normalize = v => String(v || '').replace(/\s+/g, ' ').trim().toLowerCase();

  function clean() {
    // Remove the duplicate room-creation controls only.
    // Room categories continue to be created through the existing Add Room Category workflow.
    document.querySelectorAll('button, a, [role="button"]').forEach(el => {
      const text = normalize(el.textContent);
      if (/^(?:[+＋]\s*)?add room(?: type)?$/.test(text)) el.remove();
    });

    // Also remove dynamically-rendered controls inside the Room Types section.
    const section = document.getElementById('roomtypes');
    if (section) {
      section.querySelectorAll('button, a, [role="button"]').forEach(el => {
        const text = normalize(el.textContent);
        if (/^(?:[+＋]\s*)?add room(?: type)?$/.test(text)) el.remove();
      });
    }

    // Calendar controls are intentionally untouched.
  }

  const run = () => {
    clean();
    setTimeout(clean, 100);
    setTimeout(clean, 500);
    setTimeout(clean, 1500);
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run, { once: true });
  else run();

  new MutationObserver(clean).observe(document.documentElement, { childList: true, subtree: true });
})();
