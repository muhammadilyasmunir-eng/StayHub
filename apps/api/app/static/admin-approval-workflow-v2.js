(()=>{
  const TYPES=[['terms','Terms & Conditions'],['accommodation','Accommodation Agreement'],['contract','Contract'],['agreement_form','Agreement Form']];
  const token=()=>localStorage.getItem('stayhub_admin_token')||'';
  const req=async(url,opt={})=>{opt.headers={...(opt.headers||{}),Authorization:'Bearer '+token()};const r=await fetch(url,opt);const d=await r.json().catch(()=>({}));if(!r.ok)throw Error(d.detail||'Request failed');return d};
  const esc=x=>String(x??'').replace(/[&<>\"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#039;'}[m]));

  async function finalQueue(){try{return await req('/admin/verification/queue')}catch(e){console.warn('Final review queue load failed',e);return[]}}

  const boot=()=>{
    const main=document.querySelector('main'),side=document.querySelector('.sidebar');
    if(!main||!side)return;
    let section=document.getElementById('approval-admin');
    let button=document.getElementById('approval-documents-nav');
    if(!section){
      section=document.createElement('section');section.id='approval-admin';section.className='hidden';
      section.innerHTML='<div class="page-head"><div><span class="eyebrow">PLATFORM</span><h1>Approval Documents</h1><p class="muted">Text only. No file attachment is required.</p></div></div><div id="approvalForms" style="display:grid;gap:18px"></div><div class="page-head" style="margin-top:28px"><div><span class="eyebrow">FINAL REVIEW</span><h2>Owner Submitted Documents</h2></div><button class="ghost" id="refreshReview">Refresh</button></div><div id="reviewQueue" class="card"><div class="empty">Loading...</div></div>';
      main.appendChild(section);
    }
    if(!button){
      button=document.createElement('button');button.id='approval-documents-nav';button.className='nav-btn';button.type='button';button.textContent='▤ Approval Documents';side.appendChild(button);
    }
    const open=()=>{document.querySelectorAll('main section').forEach(x=>x.classList.add('hidden'));section.classList.remove('hidden');document.querySelectorAll('.nav-btn').forEach(x=>x.classList.remove('active'));button.classList.add('active');loadForms();loadReview()};
    button.onclick=open;
    const wrap=document.getElementById('approvalForms');
    if(wrap&&!wrap.dataset.ready){
      TYPES.forEach(([type,label])=>{const c=document.createElement('div');c.className='card';c.innerHTML=`<h2>${label}</h2><input class="input" id="av_${type}" placeholder="Version e.g. v1.0"><textarea class="input" id="at_${type}" rows="12" placeholder="Enter ${label} text..."></textarea><div style="margin-top:10px"><button class="primary" id="as_${type}" type="button">Save / Activate</button><span class="muted" id="am_${type}" style="margin-left:10px"></span></div>`;wrap.appendChild(c);const saveBtn=document.getElementById('as_'+type);if(saveBtn)saveBtn.onclick=()=>save(type)});wrap.dataset.ready='1';
    }
    const refresh=document.getElementById('refreshReview');if(refresh)refresh.onclick=loadReview;
    installPendingActions();
  };

  async function loadForms(){try{const rows=await req('/admin/terms');TYPES.forEach(([type])=>{const a=rows.find(x=>x.document_type===type&&x.active),v=document.getElementById('av_'+type),t=document.getElementById('at_'+type);if(a&&v&&t){v.value=a.version;t.value=a.terms_text||a.description||''}})}catch(e){console.error('Approval documents load failed',e)}}
  async function save(type){const v=document.getElementById('av_'+type),t=document.getElementById('at_'+type),m=document.getElementById('am_'+type);if(!v||!t||!m)return;const fd=new FormData();fd.append('version',v.value.trim());fd.append('terms_text',t.value.trim());fd.append('document_type',type);try{await req('/admin/terms/upload',{method:'POST',body:fd});m.textContent='Saved & Active';}catch(e){m.textContent=e.message}}

  async function loadReview(){const q=document.getElementById('reviewQueue');if(!q)return;try{const rows=await finalQueue();q.innerHTML=rows.map(h=>`<div style="padding:16px;border-bottom:1px solid #eee"><h3>${esc(h.name)}</h3><div class="muted">${esc(h.property_id)} · Owner ${esc(h.owner_id)}</div><p><a href="${esc(h.cnic_front_url||'#')}" target="_blank">CNIC/Passport Front</a> · <a href="${esc(h.cnic_back_url||'#')}" target="_blank">Back</a> · <a href="${esc(h.signed_agreement_url||'#')}" target="_blank">Signed Agreement</a></p><button class="primary" type="button" onclick="window.stayhubGoLive(${h.id})">Go For Live</button></div>`).join('')||'<div class="empty">No properties awaiting final review.</div>'}catch(e){q.innerHTML='<div class="empty">'+esc(e.message)+'</div>'}}

  function installPendingActions(){
    const body=document.getElementById('statusRows-pending');
    if(!body||body.dataset.goLiveInstalled==='1')return;
    body.dataset.goLiveInstalled='1';
    const table=body.closest('table');
    const head=table?.querySelector('thead tr');
    if(head&&!head.querySelector('[data-go-live-head]')){const th=document.createElement('th');th.dataset.goLiveHead='1';th.textContent='Action';head.appendChild(th)}

    const render=async()=>{
      const queue=await finalQueue();
      const byId=new Map(queue.map(x=>[Number(x.id),x]));
      const byProperty=new Map(queue.map(x=>[String(x.property_id||'').trim(),x]));
      body.querySelectorAll('tr').forEach(row=>{
        const cells=row.querySelectorAll('td');
        if(!cells.length||cells.length<7||row.querySelector('[data-go-live-row]'))return;
        const propertyId=String(cells[2]?.textContent||'').trim();
        const match=byProperty.get(propertyId);
        const action=document.createElement('td');action.dataset.goLiveRow='1';
        if(match&&match.cnic_front_url&&match.cnic_back_url&&match.signed_agreement_url){
          if(cells[6])cells[6].innerHTML='<span class="badge pending">Ready for Final Review</span>';
          action.innerHTML='<button type="button" class="primary" data-go-live="'+Number(match.id)+'">Go For Live</button>';
          action.querySelector('button').onclick=()=>window.stayhubGoLive(Number(match.id));
        }else{
          const status=String(cells[6]?.textContent||'').trim().toLowerCase();
          if(status==='awaiting_terms'||status==='awaiting_documents'){
            if(cells[6])cells[6].innerHTML='<span class="badge">Awaiting Owner Submission</span>';
          }
          action.innerHTML='<span class="muted">Awaiting owner submission</span>';
        }
        row.appendChild(action);
      });
    };
    const observer=new MutationObserver(()=>{clearTimeout(body._goLiveTimer);body._goLiveTimer=setTimeout(render,80)});
    observer.observe(body,{childList:true});
    body._goLiveRender=render;
    render();
  }

  window.stayhubApproveProperty=async id=>{
    let approvalStarted=false;
    try{
      const rows=await req('/admin/terms'),active={};
      rows.filter(x=>x.active&&(x.terms_text||x.description||'').trim()).forEach(x=>active[x.document_type]=x);
      const missing=TYPES.map(x=>x[0]).filter(t=>!active[t]).map(t=>TYPES.find(x=>x[0]===t)[1]);
      if(missing.length){alert('Save active text first for: '+missing.join(', '));return}
      if(!confirm('Approve property and send the 3 documents plus Agreement Form to the owner?'))return;
      const fd=new FormData();fd.append('terms_id',String(active.terms.id));
      await req('/admin/terms/property/'+id+'/approve',{method:'POST',body:fd});
      approvalStarted=true;
      alert('Owner document stage started. Property is not live until final admin review.');
    }catch(e){alert(e.message);return;}
    if(approvalStarted){
      try{if(window.loadAll)await window.loadAll()}catch(e){console.warn('Properties refresh failed after approval',e)}
      try{if(window.loadPending)await window.loadPending()}catch(e){console.warn('Pending refresh failed after approval',e)}
      try{if(window.stayhubLoadPending)await window.stayhubLoadPending()}catch(e){console.warn('Pending operations refresh failed after approval',e)}
    }
  };

  window.approve=window.stayhubApproveProperty;
  window.stayhubGoLive=async id=>{
    if(!confirm('Review complete. Go For Live?'))return;
    try{
      await req('/admin/verification/property/'+id+'/go-live',{method:'POST'});
      alert('Property is now LIVE.');
      await loadReview();
      if(window.loadAll)await window.loadAll();
      if(window.stayhubLoadPending)await window.stayhubLoadPending();
    }catch(e){alert(e.message)}
  };

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
  setTimeout(boot,500);setTimeout(boot,1500);
})();
