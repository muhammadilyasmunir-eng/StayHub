(() => {
  const removeManualReservation = () => {
    document.querySelectorAll('#reservations button, #reservations .ops-action').forEach(button => {
      if (/new reservation|add reservation/i.test(button.textContent || '')) button.remove();
    });
    document.querySelectorAll('#reservations [onclick]').forEach(el => {
      if (/addReservation/i.test(el.getAttribute('onclick') || '')) el.remove();
    });
  };
  const boot = () => {
    removeManualReservation();
    new MutationObserver(removeManualReservation).observe(document.body, {childList:true,subtree:true});
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
