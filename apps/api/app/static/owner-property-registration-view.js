(() => {
  const esc = x => String(x ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
  const money = x => x === null || x === undefined || x === '' ? '—' : Number(x).toLocaleString();
  const list = (items, empty='—') => Array.isArray(items) && items.length ? items.map(x => typeof x === 'string' ? esc(x) : esc(x?.name ?? x?.label ?? '')).join(', ') : empty;
  const media = (url, title, image=true) => {
    if (!url) return '<span class="muted">Not uploaded</span>';
    const safe=esc(url);
    return `<div style="margin-top:8px"><a href="${safe}" target="_blank" rel="noopener">${image ? `<img src="${safe}" alt="${esc(title)}" style="display:block;max-width:280px;max-height:180px;width:auto;height:auto;object-fit:contain;border:1px solid #d9e0e7;border-radius:10px;background:#fff">` : esc(title)}</a><div style="margin-top:6px"><a href="${safe}" target="_blank" rel="noopener">View / Open</a></div></div>`;
  };
  const valueRow = (label, value) => `<div class="kv" style="margin:0"><b>${esc(label)}</b><span>${esc(value ?? '—')}</span></div>`;
  const section = (title, body) => `<div class="card" style="margin-top:14px"><h2 style="margin:0 0 12px;font-size:18px">${esc(title)}</h2>${body}</div>`;
  const grid = rows => `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px">${rows.join('')}</div>`;

  function render(h) {
    const root=document.getElementById('propertyData');
    if(!root || !h) return;
    const owner=h.owner || {};
    const docs=h.documents || [];
    const photos=h.photos || [];
    const rooms=h.room_types || [];
    const facilities=h.facilities || [];
    const policy=h.policy || {};

    const hotelDetails=grid([
      valueRow('Property ID',h.property_id), valueRow('Hotel Name',h.name), valueRow('Property Type',h.property_type),
      valueRow('Status',h.status), valueRow('Star Rating',h.star_rating), valueRow('Email',h.email),
      valueRow('Phone',h.phone), valueRow('Alternate Phone',h.alternate_phone), valueRow('Website',h.website),
      valueRow('Address',h.address), valueRow('City',h.city), valueRow('Country',h.country), valueRow('Postal Code',h.postal_code),
      valueRow('Total Rooms',h.total_rooms), valueRow('Check-in',h.check_in_time), valueRow('Check-out',h.check_out_time),
      valueRow('Timezone',h.timezone), valueRow('Currency',h.currency), valueRow('Tax %',h.tax_percent), valueRow('Commission %',h.commission_percent)
    ]);

    const ownerDetails=grid([
      valueRow('Owner Name',owner.full_name), valueRow('Owner Email',owner.email), valueRow('Owner Phone',owner.phone), valueRow('Username',owner.username)
    ]);

    const policyDetails=grid([
      valueRow('Cancellation Policy',policy.cancellation_policy), valueRow('Child Policy',policy.child_policy), valueRow('Pet Policy',policy.pet_policy),
      valueRow('Smoking Policy',policy.smoking_policy), valueRow('Payment Methods',policy.payment_methods), valueRow('Extra Bed Policy',policy.extra_bed_policy),
      valueRow('Age Restriction',policy.age_restriction), valueRow('Quiet Hours',policy.quiet_hours), valueRow('House Rules',policy.house_rules)
    ]);

    const facilitiesHtml=list(facilities,'No facilities selected.');
    const documentsHtml=docs.length ? `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px">${docs.map(d=>`<div class="kv" style="display:block;padding:14px"><b>${esc(d.document_type || 'Registration Document')}</b>${d.license_number ? `<div class="muted" style="margin-top:5px">License: ${esc(d.license_number)}</div>`:''}${d.registration_number ? `<div class="muted">Registration: ${esc(d.registration_number)}</div>`:''}${media(d.document_url,d.document_type || 'Document',/\.(jpg|jpeg|png|gif|webp|bmp|svg)(\?|#|$)/i.test(d.document_url||''))}</div>`).join('')}</div>` : '<div class="empty">No registration documents provided.</div>';

    const ownerDocs=[
      ['CNIC / Passport Front',h.owner_cnic_front_url],['CNIC / Passport Back',h.owner_cnic_back_url],['Signed Agreement',h.signed_agreement_url]
    ];
    const ownerDocsHtml=`<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px">${ownerDocs.map(([title,url])=>`<div class="kv" style="display:block;padding:14px"><b>${esc(title)}</b>${media(url,title,/\.(jpg|jpeg|png|gif|webp|bmp|svg)(\?|#|$)/i.test(url||''))}</div>`).join('')}</div>`;

    const photosHtml=photos.length ? `<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">${photos.map((p,i)=>`<div class="kv" style="display:block;padding:10px"><img src="${esc(p.photo_url)}" alt="${esc(p.caption || p.category || `Property Photo ${i+1}`)}" style="display:block;width:100%;height:160px;object-fit:cover;border-radius:9px" onerror="this.style.display='none'"><b style="display:block;margin-top:7px">${esc(p.caption || p.category || `Property Photo ${i+1}`)}</b><a href="${esc(p.photo_url)}" target="_blank" rel="noopener">View / Open</a></div>`).join('')}</div>` : '<div class="empty">No property photos provided.</div>';

    const roomsHtml=rooms.length ? rooms.map((r,i)=>{
      const rphotos=r.photos || [];
      const rfac=list(r.facilities,'No room facilities selected.');
      const rp=rphotos.length ? `<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">${rphotos.map((p,j)=>`<a href="${esc(p.photo_url)}" target="_blank" rel="noopener"><img src="${esc(p.photo_url)}" alt="${esc(p.caption || `${r.name} photo ${j+1}`)}" style="width:110px;height:80px;object-fit:cover;border-radius:8px;border:1px solid #d9e0e7"></a>`).join('')}</div>` : '';
      return `<div class="kv" style="display:block;padding:14px;margin-bottom:10px"><h3 style="margin:0 0 10px">${esc(r.name || `Room Type ${i+1}`)}</h3>${grid([valueRow('Rooms',r.number_of_rooms),valueRow('Base Price',money(r.base_price)),valueRow('Discount %',r.discount_percent),valueRow('Max Adults',r.max_adults),valueRow('Max Children',r.max_children),valueRow('Bed Type',r.bed_type),valueRow('Room Size',r.room_size),valueRow('Smoking Allowed',r.smoking_allowed?'Yes':'No'),valueRow('Extra Bed',r.extra_bed_available?'Yes':'No'),valueRow('Extra Bed Price',money(r.extra_bed_price))])}<div style="margin-top:10px"><b>Room Facilities</b><div class="muted" style="margin-top:4px">${rfac}</div></div>${r.description?`<div style="margin-top:10px"><b>Description</b><div class="muted" style="margin-top:4px">${esc(r.description)}</div></div>`:''}${rp}</div>`;
    }).join('') : '<div class="empty">No room categories provided.</div>';

    root.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><div><h2 style="margin:0">Hotel Registration Details</h2><p class="muted" style="margin:5px 0 0">Read-only registration information approved and maintained by StayHub Admin.</p></div><span class="badge">View Only</span></div>${section('Hotel Details',hotelDetails)}${section('Owner Details',ownerDetails)}${section('Description',`<div style="white-space:pre-wrap;line-height:1.6">${esc(h.description || '—')}</div>`)}${section('Rooms & Rates',roomsHtml)}${section('Facilities',`<div style="line-height:1.8">${facilitiesHtml}</div>`)}${section('Policies',policyDetails)}${section('Registration Documents',documentsHtml)}${section('Owner Verification Documents',ownerDocsHtml)}${section('Property Photos',photosHtml)}`;
  }

  function enhance(){
    if(typeof window.stayhubOwnerRegistrationViewInstalled==='undefined') window.stayhubOwnerRegistrationViewInstalled=true;
    const oldLoadHotels=window.loadHotels;
    if(typeof oldLoadHotels==='function' && !oldLoadHotels.__registrationWrapped){
      const wrapped=async function(){ const result=await oldLoadHotels.apply(this,arguments); const id=window.hotelId || localStorage.getItem('stayhub_hotel_id'); const h=(window.hotels||[]).find(x=>String(x.id)===String(id)); if(h) render(h); return result; };
      wrapped.__registrationWrapped=true; window.loadHotels=wrapped;
    }
    const oldSelect=window.selectHotel;
    if(typeof oldSelect==='function' && !oldSelect.__registrationWrapped){
      const wrapped=async function(){ const result=await oldSelect.apply(this,arguments); const id=window.hotelId || localStorage.getItem('stayhub_hotel_id'); const h=(window.hotels||[]).find(x=>String(x.id)===String(id)); if(h) render(h); return result; };
      wrapped.__registrationWrapped=true; window.selectHotel=wrapped;
    }
    const h=(window.hotels||[]).find(x=>String(x.id)===String(window.hotelId||localStorage.getItem('stayhub_hotel_id')));
    if(h) render(h);
  }
  document.addEventListener('DOMContentLoaded',()=>setTimeout(enhance,300));
  setInterval(enhance,1000);
})();