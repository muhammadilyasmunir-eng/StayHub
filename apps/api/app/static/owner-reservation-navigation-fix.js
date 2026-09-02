(() => {
  'use strict';
  const pad = n => String(n).padStart(2, '0');
  const localToday = () => { const d = new Date(); d.setHours(12,0,0,0); return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`; };
  const normalize = value => String(value || '').slice(0, 10);
  const getSelected = () => window.reservationSelectedDate || localToday();

  function removeClearButton() {
    const section = document.getElementById('reservations');
    if (!section) return;
    const clear = [...section.querySelectorAll('button')].find(b => b.id === 'shClear' || b.textContent.trim() === 'Clear');
    if (clear) clear.remove();
  }

  function renderForDate(value) {
    const selected = normalize(value) || localToday();
    window.reservationSelectedDate = selected;
    const ci = document.getElementById('shCi');
    const co = document.getElementById('shCo');
    const status = document.getElementById('shStatus');
    const q = document.getElementById('shQ');
    const apply = document.getElementById('shApply');
    if (ci && apply) {
      ci.value = selected;
      if (co) co.value = '';
      if (status) status.value = '';
      if (q) q.value = '';
      apply.click();
      return;
    }
    const input = document.getElementById('reservationDate');
    if (input) input.value = selected;
    if (typeof window.loadData === 'function') window.loadData();
  }

  window.getReservationDate = getSelected;
  window.renderReservationDate = () => {
    const input = document.getElementById('reservationDate');
    if (input) input.value = getSelected();
  };
  window.setReservationDate = value => renderForDate(value);
  window.changeReservationDate = offset => {
    const d = new Date(`${getSelected()}T12:00:00`);
    if (Number.isNaN(d.getTime())) return renderForDate(localToday());
    d.setDate(d.getDate() + Number(offset || 0));
    renderForDate(`${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`);
  };

  function bind() {
    const section = document.getElementById('reservations');
    if (!section) return;
    removeClearButton();
    const buttons = [...section.querySelectorAll('button')];
    const previous = buttons.find(b => b.textContent.trim() === '‹ Previous');
    const next = buttons.find(b => b.textContent.trim() === 'Next ›');
    const today = buttons.find(b => b.textContent.trim() === 'Today');
    if (previous) previous.onclick = e => { e.preventDefault(); window.changeReservationDate(-1); };
    if (next) next.onclick = e => { e.preventDefault(); window.changeReservationDate(1); };
    if (today) today.onclick = e => { e.preventDefault(); window.setReservationDate(localToday()); };
  }

  const start = () => { bind(); setTimeout(bind,100); setTimeout(bind,500); setTimeout(bind,1000); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, {once:true}); else start();
  new MutationObserver(bind).observe(document.documentElement, {childList:true, subtree:true});
})();
