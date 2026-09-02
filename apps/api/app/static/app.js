"use strict";

/*
|--------------------------------------------------------------------------
| StayHub Web Application
|--------------------------------------------------------------------------
*/

const API_BASE = "";

let accessToken = localStorage.getItem("stayhub_token") || null;
let currentHotelId = localStorage.getItem("stayhub_hotel_id") || null;
let hotels = [];
let currentReservations = [];
let currentGuests = [];
let currentRooms = [];
let currentRoomTypes = [];


/*
|--------------------------------------------------------------------------
| DOM Helpers
|--------------------------------------------------------------------------
*/

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


/*
|--------------------------------------------------------------------------
| API
|--------------------------------------------------------------------------
*/

async function apiRequest(
    endpoint,
    options = {}
) {

    const headers = {
        Accept: "application/json",
        ...(options.headers || {})
    };

    if (
        options.body &&
        typeof options.body !== "string"
    ) {
        headers["Content-Type"] =
            "application/json";

        options.body =
            JSON.stringify(options.body);
    }

    if (accessToken) {
        headers["Authorization"] =
            `Bearer ${accessToken}`;
    }

    const response = await fetch(
        `${API_BASE}${endpoint}`,
        {
            ...options,
            headers
        }
    );

    if (
        response.status === 401 ||
        response.status === 403
    ) {

        logout();

        throw new Error(
            "Your session has expired. Please login again."
        );
    }

    let data = null;

    const contentType =
        response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {

        data = await response.json();

    } else {

        data = await response.text();

    }

    if (!response.ok) {

        let message =
            `Request failed (${response.status})`;

        if (data) {

            if (typeof data === "string") {

                message = data;

            } else if (data.detail) {

                message =
                    typeof data.detail === "string"
                        ? data.detail
                        : JSON.stringify(data.detail);
            }
        }

        throw new Error(message);
    }

    return data;
}


/*
|--------------------------------------------------------------------------
| Login
|--------------------------------------------------------------------------
*/

async function login(email, password) {

    const body =
        new URLSearchParams();

    body.append(
        "username",
        email
    );

    body.append(
        "password",
        password
    );

    body.append(
        "grant_type",
        "password"
    );


    const response = await fetch(
        "/users/login",
        {
            method: "POST",

            headers: {
                Accept:
                    "application/json",

                "Content-Type":
                    "application/x-www-form-urlencoded"
            },

            body
        }
    );


    const data =
        await response.json();


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Login failed"
        );
    }


    accessToken =
        data.access_token;


    localStorage.setItem(
        "stayhub_token",
        accessToken
    );


    return data;
}


/*
|--------------------------------------------------------------------------
| Logout
|--------------------------------------------------------------------------
*/

function logout() {

    accessToken = null;
    currentHotelId = null;

    localStorage.removeItem(
        "stayhub_token"
    );

    localStorage.removeItem(
        "stayhub_hotel_id"
    );

    $("mainApp")
        .classList.add("hidden");

    $("loginScreen")
        .classList.remove("hidden");
}


/*
|--------------------------------------------------------------------------
| Hotels
|--------------------------------------------------------------------------
*/

async function loadHotels() {

    try {

        hotels =
            await apiRequest(
                "/hotels/"
            );


        const select =
            $("hotelSelect");


        select.innerHTML =
            `<option value="">
                Select Hotel
            </option>`;


        hotels.forEach(
            (hotel) => {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    hotel.id;

                option.textContent =
                    `${hotel.name} — ${hotel.city}`;

                select.appendChild(
                    option
                );
            }
        );


        if (currentHotelId) {

            const exists =
                hotels.some(
                    hotel =>
                        String(hotel.id) ===
                        String(currentHotelId)
                );

            if (exists) {

                select.value =
                    currentHotelId;

                updateHotelHeader();

                await loadHotelData();
            }
        }


    } catch (error) {

        showToast(
            error.message,
            "error"
        );
    }
}


/*
|--------------------------------------------------------------------------
| Hotel Selection
|--------------------------------------------------------------------------
*/

$("hotelSelect")
    .addEventListener(
        "change",
        async function () {

            currentHotelId =
                this.value || null;


            if (currentHotelId) {

                localStorage.setItem(
                    "stayhub_hotel_id",
                    currentHotelId
                );

                updateHotelHeader();

                await loadHotelData();

            } else {

                localStorage.removeItem(
                    "stayhub_hotel_id"
                );
            }
        }
    );


function getCurrentHotel() {

    return hotels.find(
        hotel =>
            String(hotel.id) ===
            String(currentHotelId)
    );
}


function updateHotelHeader() {

    const hotel =
        getCurrentHotel();

    if (!hotel) {
        return;
    }

    $("dashboardHotelName")
        .textContent =
        hotel.name;

    document.title =
        `${hotel.name} - StayHub`;
}


/*
|--------------------------------------------------------------------------
| Load Hotel Data
|--------------------------------------------------------------------------
*/

async function loadHotelData() {

    if (!currentHotelId) {
        return;
    }


    await Promise.allSettled([
        loadGuests(),
        loadReservations(),
        loadRoomTypes(),
        loadRooms()
    ]);


    updateDashboard();
}


/*
|--------------------------------------------------------------------------
| Guests
|--------------------------------------------------------------------------
*/

async function loadGuests() {

    if (!currentHotelId) {
        return;
    }


    try {

        currentGuests =
            await apiRequest(
                `/guests/hotel/${currentHotelId}`
            );


        renderGuests();


    } catch (error) {

        currentGuests = [];

        renderGuestsError(
            error.message
        );
    }
}


function renderGuests() {

    const table =
        $("guestsTable");


    if (!currentGuests.length) {

        table.innerHTML = `
            <tr>
                <td colspan="8">
                    <div class="empty-state">
                        No guests found.
                    </div>
                </td>
            </tr>
        `;

        return;
    }


    table.innerHTML =
        currentGuests.map(
            guest => `

            <tr>

                <td>
                    <strong>
                        ${escapeHtml(
                            guest.first_name
                        )}
                        ${escapeHtml(
                            guest.last_name
                        )}
                    </strong>
                </td>

                <td>
                    ${escapeHtml(
                        guest.gender
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        guest.phone
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        guest.email || "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        guest.id_number
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        guest.city
                    )}
                </td>

                <td>
                    ${
                        guest.vip
                            ? '<span class="status confirmed">VIP</span>'
                            : "-"
                    }
                </td>

                <td>
                    ${
                        guest.blacklist
                            ? '<span class="status no-show">BLACKLIST</span>'
                            : "-"
                    }
                </td>

            </tr>
        `
        ).join("");
}


function renderGuestsError(
    message
) {

    $("guestsTable").innerHTML = `
        <tr>
            <td colspan="8">
                <div class="empty-state">
                    ${escapeHtml(message)}
                </div>
            </td>
        </tr>
    `;
}


/*
|--------------------------------------------------------------------------
| Reservations
|--------------------------------------------------------------------------
*/

async function loadReservations() {

    if (!currentHotelId) {

        currentReservations = [];

        renderReservations();

        return;
    }


    /*
     * Reservation endpoint may be different depending
     * on the current backend implementation.
     *
     * We first try the hotel endpoint.
     */

    const endpoints = [
        `/reservations/hotel/${currentHotelId}`,
        `/reservations/hotel/${currentHotelId}/`,
        `/reservations/?hotel_id=${currentHotelId}`
    ];


    let loaded = false;


    for (const endpoint of endpoints) {

        try {

            const data =
                await apiRequest(
                    endpoint
                );


            if (Array.isArray(data)) {

                currentReservations =
                    data;

                loaded = true;

                break;
            }


        } catch (error) {

            /*
             * Try next known endpoint.
             */
        }
    }


    if (!loaded) {

        currentReservations = [];

    }


    renderReservations();

    updateReservationSummary();
}


function getGuestName(
    reservation
) {

    if (
        reservation.guest &&
        typeof reservation.guest ===
            "object"
    ) {

        return `${reservation.guest.first_name || ""}
                ${reservation.guest.last_name || ""}`
            .trim();
    }


    if (
        reservation.guest_name
    ) {

        return reservation.guest_name;
    }


    return `Guest #${reservation.guest_id || "-"}`;
}


function getRoomName(
    reservation
) {

    if (
        reservation.room &&
        typeof reservation.room ===
            "object"
    ) {

        return (
            reservation.room.room_number ||
            reservation.room.name ||
            `Room #${reservation.room.id || "-"}`
        );
    }


    if (
        reservation.room_number
    ) {

        return reservation.room_number;
    }


    return `Room #${reservation.room_id || "-"}`;
}


function getReservationStatus(
    reservation
) {

    return (
        reservation.status ||
        "Pending"
    );
}


function statusClass(
    status
) {

    return String(status)
        .toLowerCase()
        .replaceAll(" ", "-");
}


function formatDate(
    value
) {

    if (!value) {
        return "-";
    }

    const date =
        new Date(value);

    if (Number.isNaN(
        date.getTime()
    )) {

        return value;
    }


    return date.toLocaleDateString(
        "en-GB",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    );
}


function formatMoney(
    value
) {

    const number =
        Number(value || 0);

    return `PKR ${number.toLocaleString(
        "en-PK",
        {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }
    )}`;
}


function getCommission(
    reservation
) {

    const status =
        getReservationStatus(
            reservation
        );


    if (
        status === "No Show" &&
        reservation.no_show_fee_waived
    ) {

        return 0;
    }


    if (
        reservation.commission !==
        undefined
    ) {

        return Number(
            reservation.commission
        );
    }


    /*
     * Default Booking.com commission.
     * This can later be made configurable
     * per hotel.
     */

    return Number(
        reservation.total_amount ||
        reservation.room_rate ||
        0
    ) * 0.15;
}


function getReservationAmount(
    reservation
) {

    return Number(
        reservation.total_amount ??
        reservation.room_rate ??
        0
    );
}


function renderReservations(
    reservations =
        currentReservations
) {

    const table =
        $("reservationsTable");


    if (!reservations.length) {

        table.innerHTML = `
            <tr>
                <td colspan="9">

                    <div class="empty-state">

                        ${
                            currentHotelId
                                ? "No reservations found."
                                : "Select a hotel to load reservations."
                        }

                    </div>

                </td>
            </tr>
        `;

        return;
    }


    table.innerHTML =
        reservations.map(
            reservation => {

                const status =
                    getReservationStatus(
                        reservation
                    );


                return `

                <tr
                    class="reservation-row"
                    data-id="${reservation.id}"
                >

                    <td>
                        <strong>
                            ${escapeHtml(
                                getGuestName(
                                    reservation
                                )
                            )}
                        </strong>
                    </td>

                    <td>
                        ${formatDate(
                            reservation.check_in
                        )}
                    </td>

                    <td>
                        ${formatDate(
                            reservation.check_out
                        )}
                    </td>

                    <td>
                        ${escapeHtml(
                            getRoomName(
                                reservation
                            )
                        )}
                    </td>

                    <td>
                        ${formatDate(
                            reservation.created_at ||
                            reservation.booking_date
                        )}
                    </td>

                    <td>

                        <span
                            class="status ${statusClass(
                                status
                            )}"
                        >
                            ${escapeHtml(
                                status
                            )}
                        </span>

                    </td>

                    <td>
                        ${formatMoney(
                            getReservationAmount(
                                reservation
                            )
                        )}
                    </td>

                    <td>
                        ${formatMoney(
                            getCommission(
                                reservation
                            )
                        )}
                    </td>

                    <td>
                        <strong>
                            ${escapeHtml(
                                reservation.confirmation_no ||
                                reservation.confirmation_number ||
                                "-"
                            )}
                        </strong>
                    </td>

                </tr>
                `;
            }
        ).join("");


    document
        .querySelectorAll(
            ".reservation-row"
        )
        .forEach(
            row => {

                row.addEventListener(
                    "click",
                    () => {

                        const id =
                            row.dataset.id;

                        const reservation =
                            currentReservations.find(
                                item =>
                                    String(item.id) ===
                                    String(id)
                            );

                        if (reservation) {

                            showReservationDetail(
                                reservation
                            );
                        }
                    }
                );
            }
        );
}


function updateReservationSummary() {

    const reservations =
        currentReservations;


    $("reservationTotal")
        .textContent =
        reservations.length;


    $("reservationConfirmed")
        .textContent =
        reservations.filter(
            r =>
                getReservationStatus(r) ===
                "Confirmed"
        ).length;


    $("reservationCheckedIn")
        .textContent =
        reservations.filter(
            r =>
                getReservationStatus(r) ===
                "Checked In"
        ).length;


    $("reservationNoShow")
        .textContent =
        reservations.filter(
            r =>
                getReservationStatus(r) ===
                "No Show"
        ).length;


    const revenue =
        reservations.reduce(
            (total, reservation) =>
                total +
                getReservationAmount(
                    reservation
                ),
            0
        );


    const commission =
        reservations.reduce(
            (total, reservation) =>
                total +
                getCommission(
                    reservation
                ),
            0
        );


    $("reservationRevenue")
        .textContent =
        formatMoney(revenue);


    $("reservationCommission")
        .textContent =
        formatMoney(commission);
}


/*
|--------------------------------------------------------------------------
| Dashboard
|--------------------------------------------------------------------------
*/

function updateDashboard() {

    const reservations =
        currentReservations;


    $("todayReservations")
        .textContent =
        reservations.length;


    $("confirmedReservations")
        .textContent =
        reservations.filter(
            r =>
                getReservationStatus(r) ===
                "Confirmed"
        ).length;


    $("checkIns")
        .textContent =
        reservations.filter(
            r =>
                getReservationStatus(r) ===
                "Checked In"
        ).length;


    $("checkOuts")
        .textContent =
        reservations.filter(
            r =>
                getReservationStatus(r) ===
                "Checked Out"
        ).length;


    $("noShows")
        .textContent =
        reservations.filter(
            r =>
                getReservationStatus(r) ===
                "No Show"
        ).length;


    const revenue =
        reservations.reduce(
            (sum, reservation) =>
                sum +
                getReservationAmount(
                    reservation
                ),
            0
        );


    $("todayRevenue")
        .textContent =
        formatMoney(revenue);


    renderDashboardReservations();
}


function renderDashboardReservations() {

    const table =
        $("dashboardReservations");


    const reservations =
        currentReservations.slice(
            0,
            8
        );


    if (!reservations.length) {

        table.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="empty-state">
                        No reservations found.
                    </div>
                </td>
            </tr>
        `;

        return;
    }


    table.innerHTML =
        reservations.map(
            reservation => {

                const status =
                    getReservationStatus(
                        reservation
                    );


                return `
                    <tr>

                        <td>
                            <strong>
                                ${escapeHtml(
                                    getGuestName(
                                        reservation
                                    )
                                )}
                            </strong>
                        </td>

                        <td>
                            ${formatDate(
                                reservation.check_in
                            )}
                        </td>

                        <td>
                            ${formatDate(
                                reservation.check_out
                            )}
                        </td>

                        <td>
                            ${escapeHtml(
                                getRoomName(
                                    reservation
                                )
                            )}
                        </td>

                        <td>
                            <span
                                class="status ${statusClass(
                                    status
                                )}"
                            >
                                ${escapeHtml(
                                    status
                                )}
                            </span>
                        </td>

                        <td>
                            ${formatMoney(
                                getReservationAmount(
                                    reservation
                                )
                            )}
                        </td>

                    </tr>
                `;
            }
        ).join("");
}


/*
|--------------------------------------------------------------------------
| Reservation Detail
|--------------------------------------------------------------------------
*/

function showReservationDetail(
    reservation
) {

    const guestName =
        getGuestName(
            reservation
        );


    const status =
        getReservationStatus(
            reservation
        );


    const amount =
        getReservationAmount(
            reservation
        );


    const commission =
        getCommission(
            reservation
        );


    $("modalTitle")
        .textContent =
        `Reservation #${
            reservation.confirmation_no ||
            reservation.id
        }`;


    $("modalBody").innerHTML = `

        <div class="reservation-detail">

            <div class="detail-section">

                <h3>Guest Information</h3>

                <div class="detail-grid">

                    <div>
                        <label>Guest</label>
                        <strong>
                            ${escapeHtml(
                                guestName
                            )}
                        </strong>
                    </div>

                    <div>
                        <label>Guest ID</label>
                        <strong>
                            ${escapeHtml(
                                reservation.guest_id ||
                                "-"
                            )}
                        </strong>
                    </div>

                </div>

            </div>


            <div class="detail-section">

                <h3>Reservation</h3>

                <div class="detail-grid">

                    <div>
                        <label>Check-in</label>
                        <strong>
                            ${formatDate(
                                reservation.check_in
                            )}
                        </strong>
                    </div>

                    <div>
                        <label>Check-out</label>
                        <strong>
                            ${formatDate(
                                reservation.check_out
                            )}
                        </strong>
                    </div>

                    <div>
                        <label>Room</label>
                        <strong>
                            ${escapeHtml(
                                getRoomName(
                                    reservation
                                )
                            )}
                        </strong>
                    </div>

                    <div>
                        <label>Status</label>

                        <span
                            class="status ${statusClass(
                                status
                            )}"
                        >
                            ${escapeHtml(
                                status
                            )}
                        </span>

                    </div>

                    <div>
                        <label>Booking Date</label>
                        <strong>
                            ${formatDate(
                                reservation.created_at ||
                                reservation.booking_date
                            )}
                        </strong>
                    </div>

                    <div>
                        <label>Confirmation No.</label>
                        <strong>
                            ${escapeHtml(
                                reservation.confirmation_no ||
                                "-"
                            )}
                        </strong>
                    </div>

                </div>

            </div>


            <div class="detail-section">

                <h3>Financial</h3>

                <div class="detail-grid">

                    <div>
                        <label>Room Rate</label>
                        <strong>
                            ${formatMoney(
                                reservation.room_rate
                            )}
                        </strong>
                    </div>

                    <div>
                        <label>Discount</label>
                        <strong>
                            ${formatMoney(
                                reservation.discount
                            )}
                        </strong>
                    </div>

                    <div>
                        <label>Tax</label>
                        <strong>
                            ${formatMoney(
                                reservation.tax
                            )}
                        </strong>
                    </div>

                    <div>
                        <label>Total</label>
                        <strong>
                            ${formatMoney(
                                amount
                            )}
                        </strong>
                    </div>

                    <div>
                        <label>Commission</label>
                        <strong>
                            ${formatMoney(
                                commission
                            )}
                        </strong>
                    </div>

                </div>

            </div>


            <div class="detail-actions">

                <button
                    class="btn btn-light"
                    onclick="window.print()"
                >
                    Print This Page
                </button>


                ${
                    status !== "No Show"
                        ? `
                        <button
                            class="btn btn-primary"
                            onclick="markReservationNoShow(
                                ${reservation.id}
                            )"
                        >
                            Mark as No-show
                        </button>
                        `
                        : `
                        <span class="status no-show">
                            No-show
                        </span>
                        `
                }

            </div>

        </div>
    `;


    openModal();
}


/*
|--------------------------------------------------------------------------
| Mark No Show
|--------------------------------------------------------------------------
*/

async function markReservationNoShow(
    reservationId
) {

    const waive =
        confirm(
            "Do you want to waive off the no-show fee?\n\n" +
            "Yes = Commission will be zero.\n" +
            "Cancel = Keep the no-show fee."
        );


    /*
     * We will connect this with the exact
     * backend endpoint after confirming the
     * current reservation API implementation.
     *
     * For now the UI behaviour is prepared.
     */


    const reservation =
        currentReservations.find(
            item =>
                String(item.id) ===
                String(reservationId)
        );


    if (!reservation) {
        return;
    }


    reservation.status =
        "No Show";


    reservation.no_show_fee_waived =
        waive;


    renderReservations();

    updateReservationSummary();

    updateDashboard();


    closeModal();


    showToast(
        waive
            ? "Reservation marked as No-show. Commission waived."
            : "Reservation marked as No-show.",
        "success"
    );
}


/*
|--------------------------------------------------------------------------
| Room Types
|--------------------------------------------------------------------------
*/

async function loadRoomTypes() {

    if (!currentHotelId) {
        return;
    }


    try {

        currentRoomTypes =
            await apiRequest(
                `/room-types/hotel/${currentHotelId}`
            );


        renderRoomTypes();


    } catch (error) {

        currentRoomTypes = [];

        $("roomTypesTable").innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="empty-state">
                        ${escapeHtml(
                            error.message
                        )}
                    </div>
                </td>
            </tr>
        `;
    }
}


function renderRoomTypes() {

    const table =
        $("roomTypesTable");


    if (!currentRoomTypes.length) {

        table.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="empty-state">
                        No room types found.
                    </div>
                </td>
            </tr>
        `;

        return;
    }


    table.innerHTML =
        currentRoomTypes.map(
            type => `

            <tr>

                <td>
                    <strong>
                        ${escapeHtml(
                            type.name
                        )}
                    </strong>
                </td>

                <td>
                    ${escapeHtml(
                        type.description || "-"
                    )}
                </td>

                <td>
                    ${type.max_adults ?? "-"}
                </td>

                <td>
                    ${type.max_children ?? "-"}
                </td>

                <td>
                    ${formatMoney(
                        type.base_price
                    )}
                </td>

                <td>
                    ${
                        type.status
                            ? '<span class="status confirmed">Active</span>'
                            : '<span class="status cancelled">Inactive</span>'
                    }
                </td>

            </tr>

        `
        ).join("");
}


/*
|--------------------------------------------------------------------------
| Rooms
|--------------------------------------------------------------------------
*/

async function loadRooms() {

    if (!currentHotelId) {
        return;
    }


    /*
     * Try common room endpoints.
     */

    const endpoints = [
        `/rooms/hotel/${currentHotelId}`,
        `/rooms/hotel/${currentHotelId}/`,
        `/rooms/?hotel_id=${currentHotelId}`
    ];


    let loaded = false;


    for (const endpoint of endpoints) {

        try {

            const data =
                await apiRequest(
                    endpoint
                );


            if (Array.isArray(data)) {

                currentRooms =
                    data;

                loaded = true;

                break;
            }

        } catch (error) {
            // Try next endpoint.
        }
    }


    if (!loaded) {
        currentRooms = [];
    }


    renderRooms();
}


function renderRooms() {

    const grid =
        $("roomsGrid");


    if (!currentRooms.length) {

        grid.innerHTML = `
            <div class="empty-state-card">
                No rooms found for this hotel.
            </div>
        `;

        return;
    }


    grid.innerHTML =
        currentRooms.map(
            room => {

                const status =
                    room.status ||
                    "Available";


                return `

                <div class="room-card">

                    <div class="room-number">
                        Room ${
                            escapeHtml(
                                room.room_number ||
                                room.id
                            )
                        }
                    </div>

                    <div class="room-type">
                        ${
                            room.room_type?.name ||
                            room.room_type_name ||
                            "Room"
                        }
                    </div>

                    <span
                        class="room-status status ${statusClass(
                            status
                        )}"
                    >
                        ${escapeHtml(
                            status
                        )}
                    </span>

                    <div
                        style="
                            margin-top:15px;
                            color:#6b7280;
                            font-size:12px;
                        "
                    >
                        Floor:
                        ${escapeHtml(
                            room.floor ?? "-"
                        )}
                    </div>

                </div>

                `;
            }
        ).join("");
}


/*
|--------------------------------------------------------------------------
| Guest Search
|--------------------------------------------------------------------------
*/

$("searchGuests")
    .addEventListener(
        "click",
        function () {

            const query =
                $("guestSearch")
                    .value
                    .trim()
                    .toLowerCase();


            if (!query) {

                renderGuests();

                return;
            }


            const filtered =
                currentGuests.filter(
                    guest => {

                        const text = `
                            ${guest.first_name || ""}
                            ${guest.last_name || ""}
                            ${guest.phone || ""}
                            ${guest.email || ""}
                            ${guest.id_number || ""}
                        `.toLowerCase();

                        return text.includes(
                            query
                        );
                    }
                );


            renderGuestList(
                filtered
            );
        }
    );


function renderGuestList(
    guests
) {

    const original =
        currentGuests;


    currentGuests =
        guests;

    renderGuests();

    currentGuests =
        original;
}


/*
|--------------------------------------------------------------------------
| Reservation Search
|--------------------------------------------------------------------------
*/

$("searchReservations")
    .addEventListener(
        "click",
        function () {

            const from =
                $("reservationFrom").value;

            const to =
                $("reservationTo").value;

            const guest =
                $("reservationGuestSearch")
                    .value
                    .trim()
                    .toLowerCase();

            const status =
                $("reservationStatusFilter")
                    .value;


            const filtered =
                currentReservations.filter(
                    reservation => {

                        const checkIn =
                            reservation.check_in;

                        const guestName =
                            getGuestName(
                                reservation
                            ).toLowerCase();

                        const reservationStatus =
                            getReservationStatus(
                                reservation
                            );


                        if (
                            from &&
                            checkIn &&
                            checkIn < from
                        ) {
                            return false;
                        }


                        if (
                            to &&
                            checkIn &&
                            checkIn > to
                        ) {
                            return false;
                        }


                        if (
                            guest &&
                            !guestName.includes(
                                guest
                            )
                        ) {
                            return false;
                        }


                        if (
                            status &&
                            reservationStatus !==
                                status
                        ) {
                            return false;
                        }


                        return true;
                    }
                );


            renderReservations(
                filtered
            );
        }
    );


/*
|--------------------------------------------------------------------------
| Navigation
|--------------------------------------------------------------------------
*/

document
    .querySelectorAll(
        ".nav-item"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    showPage(
                        button.dataset.page
                    );
                }
            );
        }
    );


document
    .querySelectorAll(
        "[data-page-link]"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    showPage(
                        button.dataset.pageLink
                    );
                }
            );
        }
    );


function showPage(
    pageName
) {

    document
        .querySelectorAll(
            ".page"
        )
        .forEach(
            page => {

                page.classList.remove(
                    "active-page"
                );
            }
        );


    const target =
        $(`page-${pageName}`);


    if (!target) {
        return;
    }


    target.classList.add(
        "active-page"
    );


    document
        .querySelectorAll(
            ".nav-item"
        )
        .forEach(
            button => {

                button.classList.toggle(
                    "active",
                    button.dataset.page ===
                    pageName
                );
            }
        );


    const titles = {

        dashboard: [
            "Dashboard",
            "Overview of your hotel"
        ],

        reservations: [
            "Reservations",
            "Search and manage hotel reservations"
        ],

        guests: [
            "Guests",
            "Manage hotel guest records"
        ],

        rooms: [
            "Rooms",
            "Manage hotel rooms and room status"
        ],

        availability: [
            "Availability",
            "Manage room availability and rates"
        ],

        inbox: [
            "Inbox",
            "Guest and platform messages"
        ],

        reviews: [
            "Guest Reviews",
            "View and manage guest reviews"
        ],

        finance: [
            "Finance",
            "Revenue, commission, invoices and statements"
        ],

        "room-types": [
            "Room Types",
            "Manage room categories and pricing"
        ],

        users: [
            "Users",
            "Manage administrators and staff accounts"
        ]
    };


    const title =
        titles[pageName];


    if (title) {

        $("pageTitle")
            .textContent =
            title[0];

        $("pageSubtitle")
            .textContent =
            title[1];
    }


    if (
        pageName ===
        "reservations"
    ) {

        renderReservations();

        updateReservationSummary();
    }


    if (
        pageName ===
        "guests"
    ) {

        renderGuests();
    }


    if (
        pageName ===
        "rooms"
    ) {

        renderRooms();
    }


    if (
        pageName ===
        "room-types"
    ) {

        renderRoomTypes();
    }
}


/*
|--------------------------------------------------------------------------
| Modal
|--------------------------------------------------------------------------
*/

function openModal() {

    $("modalOverlay")
        .classList.remove(
            "hidden"
        );
}


function closeModal() {

    $("modalOverlay")
        .classList.add(
            "hidden"
        );
}


$("closeModal")
    .addEventListener(
        "click",
        closeModal
    );


$("modalOverlay")
    .addEventListener(
        "click",
        function (event) {

            if (
                event.target ===
                $("modalOverlay")
            ) {

                closeModal();
            }
        }
    );


/*
|--------------------------------------------------------------------------
| Toast
|--------------------------------------------------------------------------
*/

function showToast(
    message,
    type = "success"
) {

    const toast =
        $("toast");


    toast.textContent =
        message;


    toast.classList.add(
        "show"
    );


    setTimeout(
        () => {

            toast.classList.remove(
                "show"
            );

        },
        3000
    );
}


/*
|--------------------------------------------------------------------------
| Refresh
|--------------------------------------------------------------------------
*/

$("refreshButton")
    .addEventListener(
        "click",
        async function () {

            if (!currentHotelId) {

                await loadHotels();

                return;
            }


            await loadHotelData();


            showToast(
                "Data refreshed",
                "success"
            );
        }
    );


/*
|--------------------------------------------------------------------------
| Logout
|--------------------------------------------------------------------------
*/

$("logoutButton")
    .addEventListener(
        "click",
        function () {

            if (
                confirm(
                    "Are you sure you want to logout?"
                )
            ) {

                logout();
            }
        }
    );


/*
|--------------------------------------------------------------------------
| Login Form
|--------------------------------------------------------------------------
*/

$("loginForm")
    .addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const email =
                $("loginEmail")
                    .value
                    .trim();

            const password =
                $("loginPassword")
                    .value;


            $("loginError")
                .textContent =
                "";


            try {

                await login(
                    email,
                    password
                );


                $("loginScreen")
                    .classList.add(
                        "hidden"
                    );


                $("mainApp")
                    .classList.remove(
                        "hidden"
                    );


                await loadHotels();


                showToast(
                    "Login successful",
                    "success"
                );


            } catch (error) {

                $("loginError")
                    .textContent =
                    error.message;
            }
        }
    );


/*
|--------------------------------------------------------------------------
| Add Guest
|--------------------------------------------------------------------------
*/

$("addGuestButton")
    .addEventListener(
        "click",
        function () {

            if (!currentHotelId) {

                showToast(
                    "Please select a hotel first.",
                    "error"
                );

                return;
            }


            $("modalTitle")
                .textContent =
                "Add Guest";


            $("modalBody").innerHTML = `

                <form id="guestForm">

                    <div
                        style="
                            display:grid;
                            grid-template-columns:1fr 1fr;
                            gap:14px;
                        "
                    >

                        <div class="form-group">

                            <label>First Name</label>

                            <input
                                name="first_name"
                                required
                            >

                        </div>


                        <div class="form-group">

                            <label>Last Name</label>

                            <input
                                name="last_name"
                                required
                            >

                        </div>


                        <div class="form-group">

                            <label>Gender</label>

                            <select
                                name="gender"
                                required
                            >

                                <option value="Male">
                                    Male
                                </option>

                                <option value="Female">
                                    Female
                                </option>

                                <option value="Other">
                                    Other
                                </option>

                            </select>

                        </div>


                        <div class="form-group">

                            <label>Date of Birth</label>

                            <input
                                type="date"
                                name="date_of_birth"
                            >

                        </div>


                        <div class="form-group">

                            <label>Nationality</label>

                            <input
                                name="nationality"
                                value="Pakistani"
                                required
                            >

                        </div>


                        <div class="form-group">

                            <label>ID Type</label>

                            <select
                                name="id_type"
                                required
                            >

                                <option value="CNIC">
                                    CNIC
                                </option>

                                <option value="Passport">
                                    Passport
                                </option>

                                <option value="Driving License">
                                    Driving License
                                </option>

                                <option value="Other">
                                    Other
                                </option>

                            </select>

                        </div>


                        <div class="form-group">

                            <label>ID Number</label>

                            <input
                                name="id_number"
                                required
                            >

                        </div>


                        <div class="form-group">

                            <label>Phone</label>

                            <input
                                name="phone"
                                required
                            >

                        </div>


                        <div class="form-group">

                            <label>Email</label>

                            <input
                                type="email"
                                name="email"
                            >

                        </div>


                        <div class="form-group">

                            <label>City</label>

                            <input
                                name="city"
                                value="Lahore"
                                required
                            >

                        </div>


                        <div class="form-group">

                            <label>Country</label>

                            <input
                                name="country"
                                value="Pakistan"
                                required
                            >

                        </div>

                    </div>


                    <div class="form-group">

                        <label>Address</label>

                        <input
                            name="address"
                            required
                        >

                    </div>


                    <div class="form-group">

                        <label>Notes</label>

                        <textarea
                            name="notes"
                            style="
                                width:100%;
                                min-height:80px;
                                border:1px solid #e5e7eb;
                                border-radius:8px;
                                padding:12px;
                            "
                        ></textarea>

                    </div>


                    <div
                        style="
                            display:flex;
                            justify-content:flex-end;
                            gap:10px;
                        "
                    >

                        <button
                            type="button"
                            class="btn btn-light"
                            onclick="closeModal()"
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            class="btn btn-primary"
                        >
                            Save Guest
                        </button>

                    </div>

                </form>
            `;


            $("guestForm")
                .addEventListener(
                    "submit",
                    saveGuest
                );


            openModal();
        }
    );


async function saveGuest(
    event
) {

    event.preventDefault();


    const form =
        event.target;


    const formData =
        new FormData(form);


    const data =
        Object.fromEntries(
            formData.entries()
        );


    data.vip = false;
    data.blacklist = false;


    if (!data.date_of_birth) {

        data.date_of_birth =
            null;
    }


    try {

        await apiRequest(
            `/guests/hotel/${currentHotelId}`,
            {
                method: "POST",
                body: data
            }
        );


        closeModal();


        await loadGuests();


        showToast(
            "Guest created successfully.",
            "success"
        );


    } catch (error) {

        showToast(
            error.message,
            "error"
        );
    }
}


/*
|--------------------------------------------------------------------------
| Current Date
|--------------------------------------------------------------------------
*/

function updateDate() {

    const now =
        new Date();


    const formatted =
        now.toLocaleDateString(
            "en-GB",
            {
                weekday: "long",
                day: "2-digit",
                month: "long",
                year: "numeric"
            }
        );


    $("currentDate")
        .textContent =
        formatted;


    $("dashboardDate")
        .textContent =
        formatted;
}


/*
|--------------------------------------------------------------------------
| Initialization
|--------------------------------------------------------------------------
*/

async function initialize() {

    updateDate();


    if (accessToken) {

        $("loginScreen")
            .classList.add(
                "hidden"
            );

        $("mainApp")
            .classList.remove(
                "hidden"
            );


        try {

            await loadHotels();

        } catch (error) {

            logout();
        }

    } else {

        $("loginScreen")
            .classList.remove(
                "hidden"
            );

        $("mainApp")
            .classList.add(
                "hidden"
            );
    }
}


initialize();