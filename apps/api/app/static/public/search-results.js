(() => {
    const $ = (id) => document.getElementById(id);
    const state = { all: [], destination: '', checkIn: '', checkOut: '' };

    function todayValue() {
        const d = new Date();
        return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    }
    function tomorrowValue() {
        const d = new Date(); d.setDate(d.getDate()+1);
        return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
    }
    function esc(v) { return String(v ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m])); }
    function money(v, currency='PKR') {
        if (v == null || Number.isNaN(Number(v))) return 'Check availability';
        return `${esc(currency)} ${Number(v).toLocaleString('en-PK',{maximumFractionDigits:0})}`;
    }
    function queryState() {
        const q = new URLSearchParams(location.search);
        state.destination = q.get('destination') || '';
        state.checkIn = q.get('check_in') || todayValue();
        state.checkOut = q.get('check_out') || tomorrowValue();
        $('destination').value = state.destination;
        $('check-in').value = state.checkIn;
        $('check-out').value = state.checkOut;
        $('check-in').min = todayValue();
        $('check-out').min = state.checkIn;
    }
    function updateUrl() {
        const q = new URLSearchParams();
        const city = $('destination').value.trim();
        if (city) q.set('destination', city);
        if ($('check-in').value) q.set('check_in', $('check-in').value);
        if ($('check-out').value) q.set('check_out', $('check-out').value);
        history.replaceState(null,'',`${location.pathname}?${q.toString()}`);
        state.destination = city; state.checkIn = $('check-in').value; state.checkOut = $('check-out').value;
    }
    function filters() {
        return {
            types: [...document.querySelectorAll('input[name="property-type"]:checked')].map(x=>x.value.toLowerCase()),
            stars: [...document.querySelectorAll('input[name="stars"]:checked')].map(x=>Number(x.value)),
            facilities: [...document.querySelectorAll('input[name="facility"]:checked')].map(x=>x.value.toLowerCase())
        };
    }
    function filteredItems() {
        const f = filters();
        let items = state.all.filter(h => {
            if (f.types.length && !f.types.some(t => String(h.property_type||'').toLowerCase().includes(t))) return false;
            const rating = Number(h.rating ?? h.star_rating ?? 0);
            if (f.stars.length && !f.stars.some(s => rating >= s)) return false;
            const facilities = (h.facilities || []).map(x=>String(x).toLowerCase());
            if (f.facilities.length && !f.facilities.every(w => facilities.some(x=>x.includes(w)))) return false;
            return true;
        });
        const sort = $('sort').value;
        items.sort((a,b) => {
            const pa=Number(a.lowest_available_total ?? a.lowest_available_rate ?? Infinity), pb=Number(b.lowest_available_total ?? b.lowest_available_rate ?? Infinity);
            const ra=Number(a.rating ?? a.star_rating ?? 0), rb=Number(b.rating ?? b.star_rating ?? 0);
            if(sort==='price-low') return pa-pb;
            if(sort==='price-high') return pb-pa;
            if(sort==='rating') return rb-ra || pb-pa;
            if(sort==='name') return String(a.name).localeCompare(String(b.name));
            return (rb-ra) || (pa-pb);
        });
        return items;
    }
    function card(h) {
        const rating = h.rating ?? h.star_rating;
        const ratingText = rating != null ? Number(rating).toFixed(1) : 'New';
        const stars = rating != null ? '★'.repeat(Math.max(0,Math.min(5,Math.round(Number(rating))))) : '☆';
        const photo = h.primary_photo || '';
        const location = [h.city,h.country].filter(Boolean).join(', ');
        const type = h.property_type || 'Stay';
        const price = h.lowest_available_total ?? h.lowest_available_rate;
        const q = new URLSearchParams(); if(state.checkIn) q.set('check_in',state.checkIn); if(state.checkOut) q.set('check_out',state.checkOut);
        const detail = `/hotel/${encodeURIComponent(h.slug)}${q.toString()?`?${q}`:''}`;
        const bg = photo ? `style="background-image:url('${esc(photo)}')"` : '';
        return `<article class="sr-card">
            <a class="sr-card-media" ${bg} href="${detail}" aria-label="View ${esc(h.name)}"></a>
            <div class="sr-card-body">
                <div class="sr-card-location">${esc(location || 'Pakistan')}</div>
                <a href="${detail}" class="sr-card-name" title="${esc(h.name)}">${esc(h.name)}</a>
                <div class="sr-card-type">${esc(type)}${h.total_rooms ? ` · ${esc(h.total_rooms)} rooms` : ''}</div>
                <div class="sr-rating-line"><span class="sr-rating">${esc(ratingText)}</span><span class="sr-stars">${stars}</span></div>
                <p class="sr-description">${esc(h.description || 'An approved StayHub property with rooms available for your selected dates.')}</p>
                <div class="sr-card-bottom">
                    <div class="sr-price"><small>From</small><strong>${money(price,h.lowest_available_currency || h.currency || 'PKR')}</strong><span>per stay · available now</span></div>
                    <a class="sr-view" href="${detail}">View stay →</a>
                </div>
            </div>
        </article>`;
    }
    function render() {
        const grid=$('hotel-grid'), empty=$('empty');
        const items=filteredItems();
        grid.innerHTML=items.map(card).join('');
        empty.classList.toggle('hidden',items.length>0);
        $('results-summary').textContent = `${items.length} ${items.length===1?'stay':'stays'} available${state.destination ? ` in ${state.destination}` : ''} for ${state.checkIn} to ${state.checkOut}.`;
        $('results-title').textContent = state.destination ? `Stays in ${state.destination}` : 'Places to stay';
    }
    async function load() {
        $('loading').classList.remove('hidden'); $('error').classList.add('hidden'); $('empty').classList.add('hidden'); $('hotel-grid').innerHTML='';
        try {
            const p=new URLSearchParams(); if(state.destination) p.set('city',state.destination); if(state.checkIn && state.checkOut){p.set('check_in',state.checkIn);p.set('check_out',state.checkOut)}
            const r=await fetch(`/public/hotels/?${p.toString()}`); if(!r.ok) throw new Error(`HTTP ${r.status}`);
            const data=await r.json(); state.all=Array.isArray(data)?data:(data.items||[]); render();
        } catch(e) {
            console.error('StayHub search results failed',e); $('error').classList.remove('hidden');
            $('results-summary').textContent='There was a problem checking availability.';
        } finally { $('loading').classList.add('hidden'); }
    }
    function validateDates() {
        if(!$('check-in').value) $('check-in').value=todayValue();
        $('check-out').min=$('check-in').value;
        if(!$('check-out').value || $('check-out').value <= $('check-in').value) {
            const d=new Date(`${$('check-in').value}T00:00:00`); d.setDate(d.getDate()+1);
            $('check-out').value=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
        }
    }
    document.addEventListener('DOMContentLoaded', () => {
        queryState(); validateDates(); load();
        $('search-form').addEventListener('submit', e => {e.preventDefault();validateDates();updateUrl();load();window.scrollTo({top:0,behavior:'smooth'});});
        $('check-in').addEventListener('change',validateDates);
        $('sort').addEventListener('change',render);
        document.querySelectorAll('.sr-filters input').forEach(x=>x.addEventListener('change',render));
        $('clear-filters').addEventListener('click',()=>{document.querySelectorAll('.sr-filters input').forEach(x=>x.checked=false);render();});
        $('retry').addEventListener('click',load);
    });
})();
