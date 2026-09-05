const DESTINATION_DETAILS = {
    Lahore: 'Badshahi Mosque & Mughal heritage',
    Islamabad: 'Faisal Mosque & Margalla Hills',
    Karachi: 'Mazar-e-Quaid & coastal city life',
    Rawalpindi: 'Historic bazaars & old city charm',
    Murree: 'Mountain views & Mall Road'
};

function toLocalDateInputValue(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function setDefaultSearchDates() {
    const checkIn = document.getElementById('check-in');
    const checkOut = document.getElementById('check-out');
    if (!checkIn || !checkOut) return;

    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);

    if (!checkIn.value) checkIn.value = toLocalDateInputValue(today);
    if (!checkOut.value) checkOut.value = toLocalDateInputValue(tomorrow);

    checkOut.min = checkIn.value;
    if (!checkOut.value || checkOut.value <= checkIn.value) {
        const nextDay = new Date(`${checkIn.value}T00:00:00`);
        nextDay.setDate(nextDay.getDate() + 1);
        checkOut.value = toLocalDateInputValue(nextDay);
    }
    checkIn.min = toLocalDateInputValue(today);
}

function escapePublic(v) {
    return String(v ?? '').replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    }[m]));
}

async function loadTrendingDestinations() {
    const grid = document.querySelector('.destination-grid');
    if (!grid) return;
    try {
        const response = await fetch('/public/destinations/');
        if (!response.ok) throw new Error(`Destination request failed: ${response.status}`);
        const destinations = await response.json();
        grid.innerHTML = destinations.map(item => `
            <button class="destination-card ${escapePublic(item.city).toLowerCase()}"
                onclick="searchCity('${escapePublic(item.hotel_search_city || item.city)}')"
                aria-label="Explore hotels in ${escapePublic(item.city)}"
                style="background-image:linear-gradient(to top,rgba(0,0,0,.74),rgba(0,0,0,.06)),url('${escapePublic(item.image_url || '')}');background-size:cover;background-position:center;">
                <div class="destination-overlay"></div>
                <div class="destination-content">
                    <span>${escapePublic(item.country || 'Pakistan')}</span>
                    <h3>${escapePublic(item.city)}</h3>
                    <small>${escapePublic(item.title || DESTINATION_DETAILS[item.city] || '')}</small>
                    <div style="margin-top:7px;font-weight:800;font-size:12px;">Explore hotels →</div>
                </div>
            </button>
        `).join('');
    } catch (error) {
        console.error('StayHub destinations load failed:', error);
    }
}

function getSearchDates() {
    setDefaultSearchDates();
    return {
        checkIn: document.getElementById('check-in')?.value || '',
        checkOut: document.getElementById('check-out')?.value || ''
    };
}

function formatMoney(value, currency) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return '';
    return `${escapePublic(currency || 'PKR')} ${Number(value).toLocaleString('en-PK', { maximumFractionDigits: 0 })}`;
}

async function loadPublicHotels(city = '') {
    const grid = document.getElementById('hotel-grid');
    const loading = document.getElementById('hotel-loading');
    const empty = document.getElementById('hotel-empty');
    if (!grid) return;
    loading?.classList.remove('hidden');
    empty?.classList.add('hidden');
    try {
        const params = new URLSearchParams();
        if (city.trim()) params.set('city', city.trim());
        const { checkIn, checkOut } = getSearchDates();
        if (checkIn && checkOut) { params.set('check_in', checkIn); params.set('check_out', checkOut); }
        const query = params.toString();
        const response = await fetch(`/public/hotels/${query ? `?${query}` : ''}`);
        if (!response.ok) throw new Error(`Hotel request failed: ${response.status}`);
        const data = await response.json();
        const items = Array.isArray(data) ? data : (data.items || []);
        grid.innerHTML = items.map(h => {
            const rating = h.rating ?? h.star_rating;
            const photo = h.primary_photo || '';
            const currency = h.lowest_available_currency || h.currency || 'PKR';
            const price = h.lowest_available_total ?? h.lowest_available_rate;
            const location = `${escapePublic(h.city || '')}${h.country ? `, ${escapePublic(h.country)}` : ''}`;
            const ratingLabel = rating != null ? Number(rating).toFixed(1) : 'New';
            const priceLabel = price != null ? `From ${formatMoney(price, currency)}` : 'Check availability';
            const detailParams = new URLSearchParams(); if (checkIn) detailParams.set('check_in', checkIn); if (checkOut) detailParams.set('check_out', checkOut);
            const detailUrl = '/hotel/' + encodeURIComponent(h.slug) + (detailParams.toString() ? '?' + detailParams.toString() : '');
            return `<article class="hotel-card" style="overflow:hidden;cursor:pointer" onclick="location.href='${detailUrl}'">
                <div class="hotel-image" style="height:220px;${photo ? `background-image:linear-gradient(to top,rgba(0,0,0,.25),rgba(0,0,0,0)),url('${escapePublic(photo)}');background-size:cover;background-position:center;` : ''}">${photo ? '' : '🏨'}</div>
                <div class="hotel-card-body"><div class="hotel-location">${location}</div><h3 class="hotel-name">${escapePublic(h.name)}</h3>
                <div style="display:flex;align-items:center;gap:9px;margin-bottom:12px;"><span class="rating-box">${ratingLabel}</span><strong style="font-size:13px;">${rating != null ? 'Rated property' : 'New property'}</strong></div>
                <p style="color:#697386;font-size:12px;line-height:1.5;min-height:38px;">${escapePublic(h.description || 'Approved StayHub property with bookable rooms.')}</p>
                <div class="hotel-meta"><div class="hotel-rating"><span>★</span><span>${rating != null ? `${ratingLabel} rating` : 'No rating yet'}</span></div><div class="hotel-price"><strong>${priceLabel}</strong><span>lowest available room</span></div></div>
                <div class="hotel-view">See rooms & book →</div></div></article>`;
        }).join('');
        if (!items.length) empty?.classList.remove('hidden');
    } catch (error) {
        console.error('StayHub public hotel load failed:', error);
        grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;color:#697386;padding:40px 0;">Unable to load properties right now. Please try again.</p>';
    } finally {
        loading?.classList.add('hidden');
    }
}

function searchHotels() {
    setDefaultSearchDates();
    const city = document.getElementById('destination')?.value || '';
    document.getElementById('properties')?.scrollIntoView({ behavior: 'smooth' });
    loadPublicHotels(city);
}

function searchCity(city) {
    const destination = document.getElementById('destination');
    if (destination) destination.value = city;
    searchHotels();
}

function showAllDestinations() {
    const destination = document.getElementById('destination');
    if (destination) destination.value = '';
    searchHotels();
}

document.addEventListener('DOMContentLoaded', () => {
    setDefaultSearchDates();
    loadTrendingDestinations();
    loadPublicHotels();

    document.getElementById('check-in')?.addEventListener('change', () => {
        const checkIn = document.getElementById('check-in');
        const checkOut = document.getElementById('check-out');
        if (checkIn && checkOut) {
            checkOut.min = checkIn.value;
            if (!checkOut.value || checkOut.value <= checkIn.value) {
                const nextDay = new Date(`${checkIn.value}T00:00:00`);
                nextDay.setDate(nextDay.getDate() + 1);
                checkOut.value = toLocalDateInputValue(nextDay);
            }
        }
        const city = document.getElementById('destination')?.value || '';
        if (city) loadPublicHotels(city);
    });

    document.getElementById('check-out')?.addEventListener('change', () => {
        const city = document.getElementById('destination')?.value || '';
        if (city) loadPublicHotels(city);
    });
});

// Booking-style search results override. The home page now opens the full results screen.
function searchHotels() {
    setDefaultSearchDates();
    const destination = document.getElementById('destination')?.value?.trim() || '';
    const checkIn = document.getElementById('check-in')?.value || '';
    const checkOut = document.getElementById('check-out')?.value || '';
    const params = new URLSearchParams();
    if (destination) params.set('destination', destination);
    if (checkIn) params.set('check_in', checkIn);
    if (checkOut) params.set('check_out', checkOut);
    location.href = '/static/public/search-results.html?' + params.toString();
}
