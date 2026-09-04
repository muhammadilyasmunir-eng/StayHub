(() => {
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>\"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#039;'}[m]));
  const categories = [
    ['Top Amenities', ['Air conditioning','Heating','Free WiFi','Soundproof rooms','Non-smoking rooms','Private entrance','Desk','Wardrobe or closet','Ironing facilities']],
    ['Room Amenities', ['Balcony','Terrace','Patio','Socket near the bed','Clothes rack','Sofa bed','Extra long beds','Cleaning products','Drying rack for clothing','Fan']],
    ['Bathroom', ['Private bathroom','Bath','Shower','Toilet','Hairdryer','Free toiletries','Toilet paper','Bidet','Slippers','Bathrobe']],
    ['Media & Technology', ['Flat-screen TV','TV','Cable channels','Satellite channels','Telephone','Radio','Streaming service']],
    ['Food & Drink', ['Tea/Coffee maker','Electric kettle','Coffee machine','Refrigerator','Dining area','Dining table','Minibar','Microwave','Kitchenette','Kitchen']],
    ['Services & Extras', ['Wake-up service','Wake-up service / alarm clock','Linen','Towels','Towels/sheets','Executive lounge access']],
    ['Outdoor & View', ['City view','Garden view','Pool view','Mountain view','Landmark view','Sea view','Lake view','View']],
    ['Accessibility', ['Entire unit wheelchair accessible','Upper floors accessible by elevator','Upper floors accessible by stairs only','Accessible by elevator','Roll-in shower','Raised toilet']],
    ['Entertainment & Family Services', ['Board games/puzzles','Books, DVDs or music for children','Child safety socket covers']],
    ['Safety & Security', ['Safety deposit box','Smoke alarm','Fire extinguisher','Security alarm','Key access','24-hour security']],
    ['Safety Features', ['Carbon monoxide detector','Carbon monoxide sources'],],
    ['Physical Distancing', ['Single-room air conditioning for guest accommodation','Physical distancing rules followed']],
    ['Cleanliness & Disinfection', ['Hand sanitizer','Disinfected between stays','Guest accommodation sealed after cleaning','Linens, towels and laundry washed in accordance with local authority guidelines']]
  ];
  const paidAmenities = new Set(['Minibar','Microwave','Coffee machine']);
  const amenityNames = categories.flatMap(([, items]) => items).filter((v, i, a) => a.indexOf(v) === i);
  let token = localStorage.getItem('stayhub_token') || '';
  let hotelId = localStorage.getItem('stayhub_hotel_id') || '';
  let state = { unit:'sqm', roomTypes:[], amenities:{}, roomSizes:{} };

  function injectStyles() {
    if ($('stayhub-room-amenities-style')) return;
    const style = document.createElement('style'); style.id = 'stayhub-room-amenities-style';
    style.textContent = `
      #roomamenities .ra-card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;margin-bottom:18px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.03)}
      #roomamenities .ra-head{padding:20px 22px;border-bottom:1px solid #e5e7eb}#roomamenities .ra-head h2{margin:0 0 5px;font-size:19px}#roomamenities .ra-head p{margin:0;color:#667085;font-size:14px}
      #roomamenities .ra-body{padding:20px 22px}.ra-size-row{display:grid;grid-template-columns:1fr 190px;gap:12px;align-items:center;padding:12px 0;border-bottom:1px solid #f0f2f5}.ra-size-row:last-child{border-bottom:0}.ra-room-name{font-weight:600;color:#1d2939}.ra-size{display:flex;gap:8px}.ra-size input{width:100%;padding:9px 10px;border:1px solid #d0d5dd;border-radius:7px}.ra-size select{padding:9px 10px;border:1px solid #d0d5dd;border-radius:7px;background:#fff}
      #roomamenities .ra-table{width:100%;border-collapse:collapse}.ra-table th,.ra-table td{border-bottom:1px solid #eaecf0;padding:13px 10px;text-align:left;vertical-align:top}.ra-table th{background:#f8fafc;color:#475467;font-size:13px;font-weight:700}.ra-table td:first-child{width:40%;font-weight:600;color:#344054}.ra-options{display:flex;gap:7px;flex-wrap:wrap}.ra-choice{border:1px solid #d0d5dd;background:#fff;color:#344054;border-radius:7px;padding:7px 10px;font-size:13px;cursor:pointer}.ra-choice.active{border-color:#2563eb;background:#eff6ff;color:#1d4ed8}.ra-choice input{display:none}.ra-some{margin-top:10px;padding:10px;background:#f8fafc;border-radius:8px}.ra-check{display:inline-flex;align-items:center;gap:6px;margin:4px 12px 4px 0;font-size:13px;color:#475467}.ra-paid{font-size:11px;color:#b54708;background:#fffaeb;border:1px solid #fedf89;border-radius:10px;padding:2px 7px;margin-left:6px;font-weight:600}.ra-category{padding:8px 0 12px}.ra-category h3{font-size:16px;margin:10px 0 0}.ra-savebar{position:sticky;bottom:0;background:rgba(255,255,255,.96);border-top:1px solid #e5e7eb;padding:12px 0;display:flex;justify-content:flex-end;gap:10px;backdrop-filter:blur(5px)}.ra-save{background:#2563eb;color:#fff;border:0;border-radius:7px;padding:10px 18px;font-weight:700;cursor:pointer}.ra-save:disabled{opacity:.6;cursor:wait}.ra-note{font-size:12px;color:#667085;margin-top:7px}
      @media(max-width:800px){.ra-size-row{grid-template-columns:1fr}.ra-table{min-width:700px}.ra-table-wrap{overflow:auto}.ra-savebar{position:static}}
    `; document.head.appendChild(style);
  }

  function addNav() {
    const sidebar = document.querySelector('.sidebar'); if (!sidebar || sidebar.querySelector('[data-room-amenities-nav]')) return;
    const property = [...sidebar.querySelectorAll('.nav-btn')].find(b => b.textContent.includes('Property'));
    const button = document.createElement('button'); button.className='nav-btn'; button.dataset.roomAmenitiesNav='1'; button.innerHTML='▤ <span class="nav-label">Room Amenities</span>'; button.onclick=()=>showPage();
    if (property && property.nextSibling) sidebar.insertBefore(button, property.nextSibling); else sidebar.appendChild(button);
  }

  function addPage() {
    const main=document.querySelector('main.content'); if(!main || $('roomamenities')) return;
    const section=document.createElement('section'); section.id='roomamenities'; section.className='hidden';
    section.innerHTML=`<div class="page-head"><div><span class="eyebrow">PROPERTY</span><h1>Room Amenities</h1><p class="muted">Highlight room differences and show guests exactly what each room includes.</p></div></div><div id="raContent"></div>`;
    main.appendChild(section);
  }

  async function req(url,opt={}){opt.headers={...(opt.headers||{}),Authorization:'Bearer '+token};const r=await fetch(url,opt);const d=await r.json().catch(()=>({}));if(!r.ok)throw Error(d.detail||'Request failed');return d}
  function roomState(name){const ids=state.amenities[name]||[];if(!ids.length)return'none';if(ids.length===state.roomTypes.length&&state.roomTypes.length)return'all';return'some'}
  function selectedIds(name){return new Set(state.amenities[name]||[])}
  function parseSize(value){const m=String(value||'').trim().match(/^([0-9]+(?:\.[0-9]+)?)\s*(sqm|m2|sq\s*m|sqft|ft2|sq\s*ft)?$/i);if(!m)return{value:String(value||'').replace(/\s+(sqm|m2|sq\s*m|sqft|ft2|sq\s*ft)$/i,''),unit:state.unit};let n=Number(m[1]);let u=(m[2]||state.unit).toLowerCase().replace(/\s/g,'');if(u==='m2'||u==='sqm'||u==='sqm')u='sqm';else if(u==='ft2'||u==='sqft')u='sqft';if(u!==state.unit)n=state.unit==='sqft'?n*10.7639:n/10.7639;return{value:n?String(Math.round(n*100)/100):'',unit:state.unit}}
  function render(){
    const el=$('raContent'); if(!el)return;
    if(!hotelId){el.innerHTML='<div class="card empty">Select a property first.</div>';return;}
    const sizeRows=state.roomTypes.map(room=>{const p=parseSize(room.room_size);state.roomSizes[room.id]=p.value;return `<div class="ra-size-row"><div><div class="ra-room-name">${esc(room.name)}</div></div><div class="ra-size"><input data-size="${room.id}" value="${esc(p.value)}" inputmode="decimal" placeholder="e.g. 28"><select data-unit="${room.id}"><option value="sqm" ${state.unit==='sqm'?'selected':''}>m²</option><option value="sqft" ${state.unit==='sqft'?'selected':''}>ft²</option></select></div></div>`}).join('')||'<div class="empty">No active room types found. Add a room type first.</div>';
    let html=`<div class="ra-card"><div class="ra-head"><h2>Room size</h2><p>Enter the size for each existing room type. Choose square meters or square feet.</p></div><div class="ra-body">${sizeRows}</div></div>`;
    for(const [category,items] of categories){html+=`<div class="ra-card"><div class="ra-head"><h2>${esc(category)}</h2><p>Select whether each amenity is available in all rooms, some rooms, or none.</p></div><div class="ra-body ra-table-wrap"><table class="ra-table"><thead><tr><th>Amenity</th><th>Availability</th></tr></thead><tbody>`;for(const name of items){const st=roomState(name),selected=selectedIds(name);html+=`<tr><td>${esc(name)}${paidAmenities.has(name)?'<span class="ra-paid">Chargeable</span>':''}</td><td><div class="ra-options">${['all','some','none'].map(v=>`<button type="button" class="ra-choice ${st===v?'active':''}" data-amenity="${esc(name)}" data-state="${v}">${v==='all'?'All rooms':v==='some'?'Some rooms':'None'}</button>`).join('')}</div>${st==='some'?`<div class="ra-some">${state.roomTypes.map(r=>`<label class="ra-check"><input type="checkbox" data-room-check="${esc(name)}" value="${r.id}" ${selected.has(r.id)?'checked':''}>${esc(r.name)}</label>`).join('')||'<span class="ra-note">No active room types.</span>'}</div>`:''}</td></tr>`}html+='</tbody></table></div></div>'}
    html+='<div class="ra-savebar"><button class="ra-save" id="raSave">Save Room Amenities</button></div><div class="ra-note">Chargeable items are shown for reference only and are not turned into free room amenities. Charges remain separate from room amenity availability.</div>';el.innerHTML=html;
    el.querySelectorAll('[data-amenity]').forEach(btn=>btn.onclick=()=>{const name=btn.dataset.amenity,v=btn.dataset.state;if(v==='all')state.amenities[name]=state.roomTypes.map(r=>r.id);else if(v==='none')state.amenities[name]=[];else if(!state.amenities[name]?.length)state.amenities[name]=state.roomTypes.map(r=>r.id);render()});
    el.querySelectorAll('[data-room-check]').forEach(box=>box.onchange=()=>{const name=box.dataset.roomCheck;let ids=new Set(state.amenities[name]||[]);const id=Number(box.value);box.checked?ids.add(id):ids.delete(id);state.amenities[name]=[...ids];render()});
    el.querySelectorAll('[data-size]').forEach(input=>input.oninput=()=>{state.roomSizes[Number(input.dataset.size)]=input.value});
    el.querySelectorAll('[data-unit]').forEach(select=>select.onchange=()=>{const old=state.unit,newUnit=select.value;if(old===newUnit)return;state.unit=newUnit;state.roomTypes.forEach(r=>{const input=el.querySelector(`[data-size="${r.id}"]`);if(input){let n=Number(input.value);if(Number.isFinite(n)){n=newUnit==='sqft'?n*10.7639:n/10.7639;input.value=Math.round(n*100)/100;state.roomSizes[r.id]=input.value}}});el.querySelectorAll('[data-unit]').forEach(s=>s.value=newUnit)});
    $('raSave').onclick=save;
  }

  async function load(){try{const data=await req(`/room-amenities/hotel/${hotelId}`);state.unit=data.unit||'sqm';state.roomTypes=data.room_types||[];state.amenities={};for(const name of amenityNames)state.amenities[name]=data.amenities?.[name]||[];state.roomSizes={};render()}catch(e){$('raContent').innerHTML=`<div class="card error">${esc(e.message)}</div>`}}
  async function save(){const button=$('raSave');if(button)button.disabled=true;try{for(const room of state.roomTypes){await req(`/room-types/${room.id}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({room_size:state.roomSizes[room.id]?`${state.roomSizes[room.id]} ${state.unit}`:null})})}const amenities={};for(const name of amenityNames){const ids=state.amenities[name]||[];amenities[name]={state:ids.length===0?'none':ids.length===state.roomTypes.length?'all':'some',room_type_ids:ids}}await req(`/room-amenities/hotel/${hotelId}`,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({unit:state.unit,room_sizes:state.roomSizes,amenities})});if(button){button.textContent='Saved';setTimeout(()=>{button.textContent='Save Room Amenities';button.disabled=false},1200)}}catch(e){alert(e.message);if(button)button.disabled=false}}
  function showPage(){addNav();addPage();document.querySelectorAll('main section').forEach(s=>s.classList.add('hidden'));$('roomamenities').classList.remove('hidden');document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('active'));document.querySelector('[data-room-amenities-nav]')?.classList.add('active');hotelId=localStorage.getItem('stayhub_hotel_id')||hotelId;injectStyles();load()}
  function boot(){injectStyles();addNav();addPage();const observer=new MutationObserver(()=>addNav());const sidebar=document.querySelector('.sidebar');if(sidebar)observer.observe(sidebar,{childList:true});}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
