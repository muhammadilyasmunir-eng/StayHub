(() => {
  'use strict';

  // Prevent duplicate execution if the owner page injects this script more than once.
  if (window.__stayhubNoShowDetailUI) return;
  window.__stayhubNoShowDetailUI = true;

  const token = () => localStorage.getItem('stayhub_token') || '';
  const api = async (url, options = {}) => {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token()}`,
        ...(options.headers || {})
      }
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || 'Request failed');
    return data;
  };

  const esc = value => String(value ?? '').replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[m]));

  const closePopup = () => document.getElementById('shNoShowDetailPopup')?.remove();

  function showPopup(reservation) {
    closePopup();
    const overlay = document.createElement('div');
    overlay.id = 'shNoShowDetailPopup';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(15,23,42,.62);z-index:50000;display:flex;align-items:center;justify-content:center;padding:20px';
    overlay.innerHTML = `<div style="width:min(560px,100%);background:#fff;border-radius:16px;padding:24px;box-shadow:0 25px 80px rgba(0,0,0,.3)">
      <h2 style="margin:0 0 14px">Mark as no-show</h2>
      <p><b>${esc(reservation.room_type_name || 'Room')}</b></p>
      <p>Do you want to waive the no-show fee for this reservation?</p>
      <div style="display:grid;gap:10px;margin-top:16px">
        <button type="button" id="shNsWaive" class="sh-btn" style="height:auto;text-align:left;padding:12px"><b>Yes, waive fee</b><br><small>StayHub commission will be 0.</small></button>
        <button type="button" id="shNsCharge" class="sh-btn" style="height:auto;text-align:left;padding:12px"><b>No, charge fee</b><br><small>Applicable commission will be charged.</small></button>
      </div>
      <p style="font-size:12px;color:#667085;border-top:1px solid #e5e7eb;padding-top:12px;margin-top:16px">No-show is available only from check-out time until 48 hours after check-out.</p>
      <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:20px">
        <button type="button" id="shNsCancel" class="sh-btn">Cancel</button>
        <button type="button" id="shNsMark" class="sh-btn primary" disabled>Mark as no-show</button>
      </div>
    </div>`;
    document.body.appendChild(overlay);

    let waive = null;
    const mark = overlay.querySelector('#shNsMark');
    overlay.querySelector('#shNsWaive').onclick = () => {
      waive = true;
      mark.disabled = false;
      overlay.querySelector('#shNsWaive').style.borderColor = '#2563eb';
      overlay.querySelector('#shNsCharge').style.borderColor = '#d7dce5';
    };
    overlay.querySelector('#shNsCharge').onclick = () => {
      waive = false;
      mark.disabled = false;
      overlay.querySelector('#shNsCharge').style.borderColor = '#2563eb';
      overlay.querySelector('#shNsWaive').style.borderColor = '#d7dce5';
    };
    overlay.querySelector('#shNsCancel').onclick = closePopup;
    overlay.addEventListener('click', event => { if (event.target === overlay) closePopup(); });

    mark.onclick = async () => {
      if (waive === null) return;
      try {
        mark.disabled = true;
        await api(`/reservations/${reservation.id}/owner/no-show`, {
          method: 'POST',
          body: JSON.stringify({ waive_fee: waive })
        });
        closePopup();
        window.location.reload();
      } catch (error) {
        mark.disabled = false;
        alert(error.message);
      }
    };
  }

  async function findReservation() {
    const modal = document.getElementById('stayhubReservationDetailFix');
    const hotelId = document.getElementById('hotelSelect')?.value;
    if (!modal || !hotelId) return null;
    const text = modal.textContent || '';
    const match = text.match(/Booking #\s*([0-9]+)/i);
    if (!match) return null;
    const bookingNo = match[1];

    try {
      const rows = await api(`/reservations/hotel/${hotelId}`);
      return (Array.isArray(rows) ? rows : []).find(row => String(row.confirmation_no || row.id) === bookingNo) || null;
    } catch (_) {
      return null;
    }
  }

  async function attach() {
    const modal = document.getElementById('stayhubReservationDetailFix');
    if (!modal) return;

    // Lock this modal before the async API call so multiple MutationObserver events
    // cannot append the same No-Show action several times.
    if (modal.dataset.shNoShowAttachStarted === '1') return;
    modal.dataset.shNoShowAttachStarted = '1';

    try {
      const reservation = await findReservation();
      if (!reservation) {
        delete modal.dataset.shNoShowAttachStarted;
        return;
      }

      const status = String(reservation.status || '').toLowerCase().replace(/[_-]/g, '');
      if (!['confirmed', 'checkedin', 'checkedout'].includes(status)) return;

      const body = modal.querySelector('.sh-rd-body');
      if (!body) {
        delete modal.dataset.shNoShowAttachStarted;
        return;
      }

      // Remove any duplicate fallback actions left by an older loaded version.
      const fallbacks = body.querySelectorAll('.sh-no-show-detail-fallback');
      fallbacks.forEach((node, index) => { if (index > 0) node.remove(); });
      if (body.querySelector('.sh-no-show-detail-fallback')) return;

      const allowed = reservation.no_show_allowed === true;
      const bar = document.createElement('div');
      bar.className = 'sh-no-show-detail-fallback';
      bar.style.cssText = 'background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:18px;display:flex;align-items:center;justify-content:space-between;gap:12px';
      bar.innerHTML = `<div><b>Guest didn't show up?</b><div style="font-size:12px;color:#667085;margin-top:4px">${allowed ? 'No-show is currently available.' : 'No-show becomes available from check-out time until 48 hours after check-out.'}</div></div><button type="button" class="sh-btn" ${allowed ? '' : 'disabled'} style="color:#b45309;border-color:#f0c36a">No-Show</button>`;
      body.appendChild(bar);

      const button = bar.querySelector('button');
      if (allowed) button.onclick = () => showPopup(reservation);
    } catch (_) {
      delete modal.dataset.shNoShowAttachStarted;
    }
  }

  const observer = new MutationObserver(() => {
    const modal = document.getElementById('stayhubReservationDetailFix');
    if (modal) setTimeout(attach, 50);
  });

  function init() {
    observer.observe(document.body, { childList: true, subtree: true });
    setTimeout(attach, 100);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
