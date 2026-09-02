(() => {
  const p = new URLSearchParams(location.search);
  const slug = p.get('hotel');
  const roomTypeId = Number(p.get('room_type'));
  const checkIn = p.get('check_in');
  const checkOut = p.get('check_out');
  const money = v => `PKR ${Number(v || 0).toLocaleString('en-PK', {minimumFractionDigits: 0, maximumFractionDigits: 2})}`;
  const dateLabel = v => new Date(`${v}T00:00:00`).toLocaleDateString('en-GB', {weekday:'short', day:'2-digit', month:'short', year:'numeric'});
  const esc = v => String(v ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));

  async function apply() {
    if (!slug || !roomTypeId || !checkIn || !checkOut) return;
    try {
      const response = await fetch(`/public/hotels/${encodeURIComponent(slug)}?check_in=${encodeURIComponent(checkIn)}&check_out=${encodeURIComponent(checkOut)}`);
      if (!response.ok) return;
      const hotel = await response.json();
      const room = (hotel.rooms || []).find(x => Number(x.id) === roomTypeId);
      if (!room || !Array.isArray(room.calendar) || !room.calendar.length) return;

      const summary = document.getElementById('bookingSummary');
      if (!summary || document.getElementById('stayhubDailyRates')) return;

      // Remove the old first-night-times-nights summary so the customer never sees
      // a misleading total when calendar rates differ between nights.
      const headings = [...summary.querySelectorAll('h3')];
      const priceHeading = headings.find(h => h.textContent.trim() === 'Your price summary');
      if (priceHeading) {
        let node = priceHeading.nextElementSibling;
        priceHeading.remove();
        while (node) {
          const next = node.nextElementSibling;
          node.remove();
          node = next;
        }
      }

      const rows = room.calendar.map(day => `
        <div style="display:grid;grid-template-columns:1.5fr repeat(4,1fr);gap:8px;padding:9px 0;border-bottom:1px solid #edf0f4;font-size:12px;align-items:center">
          <div><b>${esc(dateLabel(day.date))}</b></div>
          <div><span style="color:#697386">Original</span><br><b>${money(day.base_price)}</b></div>
          <div><span style="color:#697386">Discount</span><br><b>- ${money(day.discount_amount)}</b></div>
          <div><span style="color:#697386">After discount</span><br><b>${money(day.selling_price)}</b></div>
          <div><span style="color:#697386">Tax</span><br><b>${money(day.tax_amount)}</b></div>
        </div>`).join('');

      const baseTotal = room.calendar.reduce((sum, day) => sum + Number(day.base_price || 0), 0);
      const discountTotal = room.calendar.reduce((sum, day) => sum + Number(day.discount_amount || 0), 0);
      const sellingTotal = room.calendar.reduce((sum, day) => sum + Number(day.selling_price || 0), 0);
      const taxTotal = room.calendar.reduce((sum, day) => sum + Number(day.tax_amount || 0), 0);
      const dailyTotal = room.calendar.reduce((sum, day) => sum + Number(day.total_price || 0), 0);

      const block = document.createElement('div');
      block.id = 'stayhubDailyRates';
      block.style.cssText = 'margin-top:18px;padding-top:8px;border-top:1px solid #e5e7eb';
      block.innerHTML = `<h3>Your price summary</h3><div style="display:flex;justify-content:space-between;padding:6px 0"><span>Original room price</span><b>${money(baseTotal)}</b></div><div style="display:flex;justify-content:space-between;padding:6px 0"><span>Total discount</span><b>- ${money(discountTotal)}</b></div><div style="display:flex;justify-content:space-between;padding:6px 0"><span>Room price after discount</span><b>${money(sellingTotal)}</b></div><div style="display:flex;justify-content:space-between;padding:6px 0"><span>Total taxes</span><b>${money(taxTotal)}</b></div><h4 style="margin:14px 0 8px">Nightly price breakdown</h4>${rows}<div style="display:flex;justify-content:space-between;padding-top:12px;font-size:15px"><b>Total including tax</b><b>${money(dailyTotal)}</b></div>`;
      summary.appendChild(block);
    } catch (_) {
      // The main booking flow remains usable if the optional breakdown cannot load.
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => setTimeout(apply, 250));
  else setTimeout(apply, 250);
})();
