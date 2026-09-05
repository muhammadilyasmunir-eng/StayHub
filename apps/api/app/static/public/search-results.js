(() => {
  const $ = (id) => document.getElementById(id);
  let allItems = [];
  let filteredItems = [];
  let map;
  let markers = [];
  let mapReady = false;

  function dateValue(id, fallbackDays) {
    const el = $(id);
    if (el?.value) return el.value;
    const d = new Date(); d.setDate(d.getDate() + fallbackDays);
    return d.toISOString().slice(0, 10);
  }
  function esc(value) { return String(value ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m])); }
  function money(value, currency) { return `${esc(currency || 'PKR')} ${Number(value || 0).toLocaleString('en-PK',{maximumFractionDigits:0})}`; }
  function paramsFromUrl() { return new URLSearchParams(location.search); }

  function initMap() {
    if (!window.L || mapReady) return;
    map = L.map('map', { scrollWheelZoom: false }).setView([31.5204, 74.3587], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap contributors' }).addTo(map);
    mapReady = true;
    updateMap();
  }

  function updateMap() {
    if (!mapReady) return;
    markers.forEach(m => m.remove()); markers = [];
    const points = [];
    filteredItems.forEach(item => {
      const lat = Number(item.latitude), lng = Number(item.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;
      const marker = L.marker([lat, lng]).addTo(map);
      marker.bindPopup(`<div class="marker-title">${esc(item.name)}</div><div>${esc(item.city || '')}</div><div class="marker-price">${money(item.lowest_available_total,item.lowest_available_currency)}</div><button style="margin-top:7px;background:#006ce4;color:#fff;border:0;border-radius:3px;padding:6px 8px;cursor:pointer" onclick="location.href='${esc(detailUrl(item))}'">View property</button>`);
      marker.on('click', () => highlightCard(item.id));
      marker._stayhubId = item.id; markers.push(marker); points.push([lat,lng]);
    });
    if (points.length === 1) map.setView(points[0], 14);
    else if (points.length > 1) map.fitBounds(points, { padding: [25,25], maxZoom: 13 });
  }

  function detailUrl(item) {
    const p = new URLSearchParams();
    const ci = $('check-in')?.value, co = $('check-out')?.value;
    if (ci) p.set('check_in', ci); if (co) p.set('check_out', co);
    return '/hotel/' + encodeURIComponent(item.slug) + (p.toString() ? '?' + p.toString() : '');
  }

  function renderPropertyTypes() {
    const box = $('property-types');
    const mapCounts = {};
    allItems.forEach(x => { const key = x.property_type || 'Other'; mapCounts[key] = (mapCounts[key] || 0) + 1; });
    box.innerHTML = Object.entries(mapCounts).sort((a,b)=>a[0].localeCompare(b[0])).map(([name,count]) => `<label class="check"><input class="type-filter" type="checkbox" value="${esc(name)}"><span>${esc(name)}</span><em>${count}</em></label>`).join('');
    box.querySelectorAll('input').forEach(x => x.addEventListener('change', applyFilters));
  }

  function setupPriceControls() {
    const prices = allItems.map(x => Number(x.lowest_available_total)).filter(Number.isFinite);
    const min = prices.length ? Math.floor(Math.min(...prices)/500)*500 : 0;
    const max = prices.length ? Math.ceil(Math.max(...prices)/500)*500 : 100000;
    $('price-min').min = min; $('price-min').max = max; $('price-min').value = min;
    $('price-max').min = min; $('price-max').max = max; $('price-max').value = max;
    $('min-price-label').textContent = money(min); $('max-price-label').textContent = money(max);
    $('price-min').oninput = applyFilters; $('price-max').oninput = applyFilters;
  }

  function selectedValues(selector) { return [...document.querySelectorAll(selector+':checked')].map(x=>x.value); }

  function applyFilters() {
    const minPrice = Number($('price-min').value), maxPrice = Number($('price-max').value);
    if (minPrice > maxPrice) $('price-min').value = maxPrice;
    $('min-price-label').textContent = money(Number($('price-min').value)); $('max-price-label').textContent = money(Number($('price-max').value));
    const ratings = selectedValues('.rating-filter').map(Number);
    const types = selectedValues('.type-filter').map(x=>x.toLowerCase());
    const facilities = selectedValues('.facility-filter').map(x=>x.toLowerCase());
    filteredItems = allItems.filter(item => {
      const score = Number(item.review_score ?? item.rating ?? 0);
      const ratingOk = !ratings.length || ratings.some(r => score >= r);
      const typeOk = !types.length || types.includes(String(item.property_type || '').toLowerCase());
      const price = Number(item.lowest_available_total);
      const priceOk = price >= Number($('price-min').value) && price <= Number($('price-max').value);
      const itemFacilities = (item.facilities || []).map(x=>String(x).toLowerCase());
      const facilitiesOk = facilities.every(f => itemFacilities.some(x => x.includes(f)));
      const familyOk = !$('family-filter').checked || item.family_friendly;
      const adultsOk = !$('adults-filter').checked || item.adults_only;
      const breakfastOk = !$('breakfast-filter').checked || item.breakfast_available;
      return ratingOk && typeOk && priceOk && facilitiesOk && familyOk && adultsOk && breakfastOk;
    });
    sortItems(); renderCards(); updateMap();
  }

  function sortItems() {
    const sort = $('sort').value;
    if (sort === 'price_low') filteredItems.sort((a,b)=>Number(a.lowest_available_total)-Number(b.lowest_available_total));
    else if (sort === 'price_high') filteredItems.sort((a,b)=>Number(b.lowest_available_total)-Number(a.lowest_available_total));
    else if (sort === 'rating') filteredItems.sort((a,b)=>Number(b.rating||0)-Number(a.rating||0));
    else filteredItems.sort((a,b)=>Number(b.rating||0)-Number(a.rating||0) || Number(a.lowest_available_total)-Number(b.lowest_available_total));
  }

  function renderCounts() {
    const score = threshold => allItems.filter(x => Number(x.review_score ?? x.rating ?? 0) >= threshold).length;
    [9,8,7,6].forEach(n => { const el=$(`count-${n}`); if(el) el.textContent=score(n); });
    const facilityIds = {'Free WiFi':'facility-free-wifi','Parking':'facility-parking','Swimming pool':'facility-pool','Restaurant':'facility-restaurant','Airport shuttle':'facility-shuttle'};
    Object.entries(facilityIds).forEach(([name,id]) => { const n=allItems.filter(x=>(x.facilities||[]).some(f=>String(f).toLowerCase().includes(name.toLowerCase()))).length; if($(id)) $(id).textContent=n; });
  }

  function renderCards() {
    const list=$('property-list');
    $('result-title').textContent = `${filteredItems.length.toLocaleString()} propert${filteredItems.length === 1 ? 'y' : 'ies'} found`;
    $('result-subtitle').textContent = filteredItems.length ? 'Prices and availability are based on your selected dates.' : 'No available properties match the selected filters.';
    $('empty').classList.toggle('hidden', filteredItems.length !== 0); $('loading').classList.add('hidden');
    list.innerHTML = filteredItems.map(item => {
      const score = item.review_score ?? item.rating;
      const scoreText = score != null ? Number(score).toFixed(1) : 'New';
      const scoreWord = score >= 9 ? 'Wonderful' : score >= 8 ? 'Very Good' : score >= 7 ? 'Good' : score >= 6 ? 'Pleasant' : 'New';
      const stars = item.star_rating ? '★'.repeat(Math.min(5, Math.max(1, Math.round(Number(item.star_rating))))) : '';
      const chips=(item.facilities||[]).slice(0,4).map(x=>`<span class="chip">${esc(x)}</span>`).join('');
      const photo=esc(item.primary_photo || '');
      return `<article class="property-card" data-id="${item.id}" onclick="if(!event.target.closest('.select-btn'))location.href='${esc(detailUrl(item))}'">
        ${photo ? `<img class="property-photo" src="${photo}" alt="${esc(item.name)}" loading="lazy">` : `<div class="property-photo" style="display:grid;place-items:center;font-size:40px">🏨</div>`}
        <div class="property-main"><h2 class="property-name">${esc(item.name)} <span class="stars">${stars}</span></h2><div class="location">${esc(item.city || '')}${item.address ? ` · ${esc(item.address)}` : ''}</div><p class="description">${esc(item.description || 'Approved StayHub property with bookable rooms.')}</p><div class="chips">${chips}</div></div>
        <div class="property-side"><div class="score"><span>${esc(scoreWord)}<br><small>${Number(item.review_count||0).toLocaleString()} review${Number(item.review_count||0)===1?'':'s'}</small></span><strong>${esc(scoreText)}</strong></div><div class="price">${money(item.lowest_available_total,item.lowest_available_currency)}<small>per night · lowest available</small><button class="select-btn" onclick="event.stopPropagation();location.href='${esc(detailUrl(item))}'">Select dates</button></div></div>
      </article>`;
    }).join('');
  }

  function highlightCard(id) {
    document.querySelectorAll('.property-card').forEach(c=>c.classList.toggle('map-active',String(c.dataset.id)===String(id)));
    const card=document.querySelector(`.property-card[data-id="${CSS.escape(String(id))}"]`); card?.scrollIntoView({behavior:'smooth',block:'center'});
  }
  window.highlightCard = highlightCard;

  async function load() {
    const url=paramsFromUrl();
    const destination=url.get('destination') || url.get('city') || '';
    $('destination').value=destination;
    $('check-in').value=url.get('check_in') || dateValue('check-in',0);
    $('check-out').value=url.get('check_out') || dateValue('check-out',1);
    $('check-in').min=dateValue('check-in',0);
    $('check-out').min=$('check-in').value;
    try {
      const p=new URLSearchParams(); if(destination)p.set('destination',destination); p.set('check_in',$('check-in').value); p.set('check_out',$('check-out').value);
      const response=await fetch(`/public/search/hotels?${p}`); if(!response.ok)throw new Error(`HTTP ${response.status}`);
      const data=await response.json(); allItems=Array.isArray(data)?data:(data.items||[]); filteredItems=[...allItems];
      renderPropertyTypes(); setupPriceControls(); renderCounts(); applyFilters();
    } catch(e) { console.error(e); $('loading').textContent='Unable to load properties. Please try again.'; }
  }

  function resetFilters(){ document.querySelectorAll('.filter-card input[type=checkbox]').forEach(x=>x.checked=false); setupPriceControls(); applyFilters(); }
  $('search-button').onclick=()=>{ const p=new URLSearchParams(); const d=$('destination').value.trim(); if(d)p.set('destination',d); p.set('check_in',$('check-in').value); p.set('check_out',$('check-out').value); location.href='/static/public/search-results.html?'+p; };
  $('clear-filters').onclick=resetFilters; $('sort').onchange=applyFilters;
  ['family-filter','adults-filter','breakfast-filter'].forEach(id=>$(id).addEventListener('change',applyFilters));
  document.querySelectorAll('.rating-filter,.facility-filter').forEach(x=>x.addEventListener('change',applyFilters));
  $('check-in').addEventListener('change',()=>{ if($('check-out').value <= $('check-in').value){const d=new Date($('check-in').value+'T00:00:00');d.setDate(d.getDate()+1);$('check-out').value=d.toISOString().slice(0,10)} });
  $('list-button').onclick=()=>{ $('property-list').classList.remove('grid-mode'); $('list-button').classList.add('active'); $('grid-button').classList.remove('active'); };
  $('grid-button').onclick=()=>{ $('property-list').classList.add('grid-mode'); $('grid-button').classList.add('active'); $('list-button').classList.remove('active'); };
  $('map-button').onclick=()=>{ $('map-wrap').classList.toggle('hidden'); $('map-button').classList.toggle('active'); if(mapReady)setTimeout(()=>map.invalidateSize(),50); };
  $('compare-toggle').onclick=()=>$('compare-toggle').classList.toggle('on');
  document.addEventListener('DOMContentLoaded',()=>{initMap();load();});
})();
