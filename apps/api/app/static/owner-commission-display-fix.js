"use strict";

/*
 * Owner reservation-list commission display fix.
 * Cancelled and waived no-show reservations are always commission-free.
 */
(function () {
    const money = (value) => Number(value || 0).toLocaleString("en-PK", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const normalizedStatus = (reservation) => String(reservation?.status || "").trim().toUpperCase();
    const normalizedCommissionStatus = (reservation) => String(reservation?.commission_status || "").trim().toUpperCase();

    const isCommissionFree = (reservation) => {
        const status = normalizedStatus(reservation);
        const commissionStatus = normalizedCommissionStatus(reservation);
        return status === "CANCELLED" || commissionStatus === "VOID" || commissionStatus === "NO_SHOW_WAIVED";
    };

    const commissionForDisplay = (reservation) => {
        if (!reservation || isCommissionFree(reservation)) return 0;
        const roomRate = Number(
            reservation.room_rate ??
            reservation.net_room_rate ??
            0
        );
        return roomRate * 0.05;
    };

    function patchReservationList() {
        const rows = document.querySelectorAll("#resBody tr[data-res-id]");
        if (!rows.length) return;

        const reservations = (window.data && Array.isArray(window.data.res))
            ? window.data.res
            : [];
        const byId = new Map(
            reservations.map((reservation) => [String(reservation.id), reservation])
        );

        rows.forEach((row) => {
            const reservation = byId.get(String(row.dataset.resId));
            if (!reservation) return;
            const cells = row.querySelectorAll("td");
            const commissionCell = cells[7];
            if (!commissionCell) return;
            const value = `PKR ${money(commissionForDisplay(reservation))}`;
            if (commissionCell.textContent.trim() !== value) {
                commissionCell.textContent = value;
            }
        });

        const summary = document.getElementById("resSummary");
        if (summary) {
            const visible = Array.from(rows)
                .map((row) => byId.get(String(row.dataset.resId)))
                .filter(Boolean);
            const totalCommission = visible.reduce(
                (sum, reservation) => sum + commissionForDisplay(reservation),
                0
            );
            const items = summary.querySelectorAll(".notice");
            if (items.length >= 3) {
                items[2].innerHTML = `Est. Commission: <b>PKR ${money(totalCommission)}</b>`;
            }
        }
    }

    const start = () => {
        patchReservationList();
        const target = document.getElementById("reservationTable") || document.body;
        const observer = new MutationObserver(() => {
            observer.disconnect();
            patchReservationList();
            observer.observe(target, { childList: true, subtree: true });
        });
        observer.observe(target, { childList: true, subtree: true });
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => setTimeout(start, 250));
    } else {
        setTimeout(start, 250);
    }
})();
