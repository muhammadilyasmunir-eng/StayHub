"use strict";

/* Owner billing display is read-only. Billing values are controlled by platform admin. */
(function () {
    const moneyPercent = (value) => {
        if (value === null || value === undefined || value === "") return "Not Set";
        const n = Number(value);
        return Number.isFinite(n) ? `${n}%` : "Not Set";
    };

    const esc = (value) => String(value ?? "").replace(/[&<>\"']/g, (m) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#039;"
    }[m]));

    function renderBilling() {
        const target = document.getElementById("propertyBillingReadOnly");
        if (!target) return;
        const select = document.getElementById("hotelSelect");
        const id = select?.value || localStorage.getItem("stayhub_hotel_id");
        const hotels = Array.isArray(window.hotels) ? window.hotels : [];
        const hotel = hotels.find((h) => String(h.id) === String(id));
        if (!hotel) {
            target.innerHTML = '<div class="empty">Select a property.</div>';
            return;
        }
        target.innerHTML = `
            <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px">
              <div style="border:1px solid #e2e8f0;border-radius:14px;padding:16px;background:#f8fafc">
                <div style="font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase">Tax</div>
                <div style="font-size:22px;font-weight:800;margin-top:5px">${esc(moneyPercent(hotel.tax_percent))}</div>
              </div>
              <div style="border:1px solid #e2e8f0;border-radius:14px;padding:16px;background:#f8fafc">
                <div style="font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase">Commission</div>
                <div style="font-size:22px;font-weight:800;margin-top:5px">${esc(moneyPercent(hotel.commission_percent))}</div>
              </div>
            </div>
            <div class="notice" style="margin-top:14px">Tax and commission are set by StayHub administration and are read-only for property owners.</div>`;
    }

    function ensureTarget() {
        const propertyData = document.getElementById("propertyData");
        if (!propertyData || document.getElementById("propertyBillingReadOnly")) return;
        const section = document.createElement("div");
        section.id = "propertyBillingReadOnly";
        section.style.marginTop = "18px";
        propertyData.insertAdjacentElement("afterend", section);
    }

    function boot() {
        ensureTarget();
        renderBilling();
        const select = document.getElementById("hotelSelect");
        if (select && !select.dataset.billingBound) {
            select.dataset.billingBound = "1";
            select.addEventListener("change", () => setTimeout(renderBilling, 0));
        }
        const target = document.getElementById("propertyData") || document.body;
        new MutationObserver(() => {
            ensureTarget();
            renderBilling();
        }).observe(target, { childList: true, subtree: true });
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", () => setTimeout(boot, 300));
    else setTimeout(boot, 300);
})();
