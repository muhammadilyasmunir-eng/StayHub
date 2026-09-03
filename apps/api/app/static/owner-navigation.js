(() => {
  const esc = x => String(x ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));

  const updateOwnerNavigation = () => {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;
    const buttons = [...sidebar.querySelectorAll('.nav-btn')];
    buttons
      .filter(b => /^(?:♙\s*)?Guests$/i.test((b.textContent || '').trim()) || /^(?:₨\s*)?Rates$/i.test((b.textContent || '').trim()))
      .forEach(b => b.remove());
    const remaining = [...sidebar.querySelectorAll('.nav-btn')];
    const property = remaining.find(b => /property/i.test(b.textContent || ''));
    const finance = remaining.find(b => /finance/i.test(b.textContent || ''));
    if (property && finance && finance.nextElementSibling !== property) finance.after(property);
  };

  const money = x => x === null || x === undefined || x === '' ? '—' : Number(x).toLocaleString();
  const val = (label, value) => `<div class="kv" style="margin:0"><b>${esc(label)}</b><span>${esc(value ?? '—')}</span></div>`;
  const grid = rows => `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px">${rows.join('')}</div>`;
  const section = (title, body) => `<div class="card" style="margin-top:14px"><h2 style="margin:0 0 12px;font-size:18px">${esc(title)}</h2>${body}</div>`;
  const isImage = url => /\.(jpg|jpeg|png|gif|webp|bmp|svg)(\?|#|$)/i.test(String(url || ''));
  const media = (url, title) => {
    if (!url) return '<span class="muted">Not uploaded</span>';
    const safe=esc(url);
    return `<div style="margin-top:8px"><a href="${safe}" target="_blank" rel="noopener">${isImage(url) ? `<img src="${safe}" alt="${esc(title)}" style="display:block;max-width:280px;max-height:180px;width:auto;height:auto;object-fit:contain;border:1px solid #d9e0e7;border-radius:10px;background:#fff">` : esc(title)}</a><div style="margin-top:6px"><a href="${safe}" target="_blank" rel="noopener">View / Open</a></div></div>`;
  };
  const names = items => Array.isArray(items) && items.length ? items.map(x => esc(typeof x === 'string' ? x : (x?.name ?? x?.label ?? ''))).join(', ') : '—';

  function renderDetails(h) {
    const owner=h.owner || {}, policy=h.policy || {}, docs=h.documents || [], photos=h.photos || [], rooms=h.room_types || [], facilities=h.facilities || [];
    const hotel=grid([
      val('Property ID',h.property_id),val('Hotel Name',h.name),val('Property Type',h.property_type),val('Status',h.status),val('Star Rating',h.star_rating),
      val('Email',h.email),val('Phone',h.phone),val('Alternate Phone',h.alternate_phone),val('Website',h.website),val('Address',h.address),val('City',h.city),val('Country',h.country),
      val('Postal Code',h.postal_code),val('Total Rooms',h.total_rooms),val('Check-in',h.check_in_time),val('Check-out',h.check_out_time),val('Timezone',h.timezone),val('Currency',h.currency),val('Tax %',h.tax_percent),val('Commission %',h.commission_percent)
    ]);
    const ownerBox=grid([val('Owner Name',owner.full_name),val('Owner Email',owner.email),val('Owner Phone',owner.phone),val('Username',owner.username)]);
    const policyBox=grid([
      val('Cancellation Policy',policy.cancellation_policy),val('Child Policy',policy.child_policy),val('Pet Policy',policy.pet_policy),val('Smoking Policy',policy.smoking_policy),
      val('Payment Methods',policy.payment_methods),val('Extra Bed Policy',policy.extra_bed_policy),val('Age Restriction',policy.age_restriction),val('Quiet Hours',policy.quiet_hours),val('House Rules',policy.house_rules)
    ]);
    const docsBox=docs.length ? `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px">${docs.map(d=>`<div class="kv" style="display:block;padding:14px"><b>${esc(d.document_type || 'Registration Document')}</b>${d.license_number?`<div class="muted">License: ${esc(d.license_number)}</div>`:''}${d.registration_number?`<div class="muted">Registration: ${esc(d.registration_number)}</div>`:''}${media(d.document_url,d.document_type || 'Document')}</div>`).join('')}</div>` : '<div class="empty">No registration documents provided.</div>';
    const ownerDocs=[['CNIC / Passport Front',h.owner_cnic_front_url],['CNIC / Passport Back',h.owner_cnic_back_url],['Signed Agreement',h.signed_agreement_url]];
    const ownerDocsBox=`<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px">${ownerDocs.map(([t,u])=>`<div class="kv" style="display:block;padding:14px"><b>${esc(t)}</b>${media(u,t)}</div>`).join('')}</div>`;
    const photosBox=photos.length ? `<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">${photos.map((p,i)=>`<div class="kv" style="display:block;padding:10px"><img src="${esc(p.photo_url)}" alt="${esc(p.caption || p.category || `Property Photo ${i+1}`)}" style="display:block;width:100%;height:160px;object-fit:cover;border-radius:9px" onerror="this.style.display='none'"><b style="display:block;margin-top:7px">${esc(p.caption || p.category || `Property Photo ${i+1}`)}</b><a href="${esc(p.photo_url)}" target="_blank" rel="noopener">View / Open</a></div>`).join('')}</div>` : '<div class="empty">No property photos provided.</div>';
    const roomsBox=rooms.length ? rooms.map((r,i)=>{
      const rphotos=r.photos || [];
      const rp=rphotos.length ? `<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">${rphotos.map((p,j)=>`<a href="${esc(p.photo_url)}" target="_blank" rel="noopener"><img src="${esc(p.photo_url)}" alt="${esc(p.caption || `${r.name} photo ${j+1}`)}" style="width:110px;height:80px;object-fit:cover;border-radius:8px;border:1px solid #d9e0e7"></a>`).join('')}</div>` : '<div class="muted" style="margin-top:8px">No room photos.</div>';
      return `<div class="kv" style="display:block;padding:14px;margin-bottom:10px"><h3 style="margin:0 0 10px">${esc(r.name || `Room Type ${i+1}`)}</h3>${grid([val('Rooms',r.number_of_rooms),val('Base Price',money(r.base_price)),val('Discount %',r.discount_percent),val('Max Adults',r.max_adults),val('Max Children',r.max_children),val('Bed Type',r.bed_type),val('Room Size',r.room_size),val('Smoking Allowed',r.smoking_allowed?'Yes':'No'),val('Extra Bed',r.extra_bed_available?'Yes':'No'),val('Extra Bed Price',money(r.extra_bed_price))])}<div style="margin-top:10px"><b>Room Facilities</b><div class="muted" style="margin-top:4px">${names(r.facilities)}</div></div>${r.description?`<div style="margin-top:10px"><b>Description</b><div style="white-space:pre-wrap;line-height:1.5">${esc(r.description)}</div></div>`:''}${rp}</div>`;
    }).join('') : '<div class="empty">No room categories provided.</div>';
    return `<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><div><h2 style="margin:0">Hotel Registration Details</h2><p class="muted" style="margin:5px 0 0">Read-only information maintained by StayHub Admin.</p></div><span class="badge">View Only</span></div>${section('Hotel Details',hotel)}${section('Owner Details',ownerBox)}${section('Description',`<div style="white-space:pre-wrap;line-height:1.6">${esc(h.description || '—')}</div>`)}${section('Rooms & Rates',roomsBox)}${section('Facilities',`<div style="line-height:1.8">${names(facilities)}</div>`)}${section('Policies',policyBox)}${section('Registration Documents',docsBox)}${section('Owner Verification Documents',ownerDocsBox)}${section('Property Photos',photosBox)}`;
  }

  async function openRegistrationDetails() {
    const token=localStorage.getItem('stayhub_token') || '';
    const id=document.getElementById('hotelSelect')?.value || localStorage.getItem('stayhub_hotel_id') || '';
    if(!id) return;
    const button=document.getElementById('hotelRegistrationDetailsBtn');
    if(button){button.disabled=true;button.textContent='Loading...';}
    try {
      const r=await fetch('/hotels/',{headers:{Authorization:'Bearer '+token}});
      const hotels=await r.json();
      if(!r.ok) throw Error(hotels.detail || 'Unable to load property details');
      const h=hotels.find(x=>String(x.id)===String(id));
      if(!h) throw Error('Selected property not found');
      let modal=document.getElementById('hotelRegistrationDetailsModal');
      if(!modal){
        modal=document.createElement('div');
        modal.id='hotelRegistrationDetailsModal';
        modal.style.cssText='position:fixed;inset:0;background:rgba(15,23,42,.62);z-index:99999;padding:24px;overflow:auto;box-sizing:border-box;display:none';
        modal.innerHTML='<div id="hotelRegistrationDetailsPanel" style="max-width:1100px;margin:0 auto;background:#f8fafc;border-radius:16px;padding:20px;box-shadow:0 20px 60px rgba(0,0,0,.25)"><div style="display:flex;justify-content:flex-end;margin-bottom:8px"><button type="button" id="hotelRegistrationDetailsClose" class="ghost">Close</button></div><div id="hotelRegistrationDetailsBody"></div></div>';
        document.body.appendChild(modal);
        document.getElementById('hotelRegistrationDetailsClose').addEventListener('click',()=>modal.style.display='none');
        modal.addEventListener('click',e=>{if(e.target===modal)modal.style.display='none'});
      }
      document.getElementById('hotelRegistrationDetailsBody').innerHTML=renderDetails(h);
      modal.style.display='block';
    } catch(e) { alert(e.message || 'Unable to load property details'); }
    finally { if(button){button.disabled=false;button.textContent='Hotel Registration Details';} }
  }

  function ensurePropertyButton(){
    const root=document.getElementById('property');
    const data=document.getElementById('propertyData');
    if(!root || !data) return;
    if(document.getElementById('hotelRegistrationDetailsBtn')) return;
    const box=document.createElement('div');
    box.style.cssText='margin-top:14px';
    box.innerHTML='<button type="button" id="hotelRegistrationDetailsBtn" class="primary">Hotel Registration Details</button><div class="muted" style="margin-top:6px">View the complete submitted registration profile. Editing is not available to property owners.</div>';
    data.insertAdjacentElement('afterend',box);
    document.getElementById('hotelRegistrationDetailsBtn').addEventListener('click',openRegistrationDetails);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',()=>{updateOwnerNavigation();ensurePropertyButton();setInterval(ensurePropertyButton,1000)});
  else {updateOwnerNavigation();ensurePropertyButton();setInterval(ensurePropertyButton,1000)}
})();