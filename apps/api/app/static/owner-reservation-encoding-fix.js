(()=>{
  'use strict';

  // Repair common UTF-8-as-Windows-1252 mojibake in the reservation detail UI.
  // Keep this file ASCII-only so the fix itself cannot suffer from the same issue.
  const badToGood = new Map([
    ['\u00e2\u2020\u0090','\u2190'], // ←
    ['\u00e2\u02c6\u2019','\u2212'], // −
    ['\u00c3\u2014','\u00d7'],       // ×
    ['\u00c2\u00b7','\u00b7']        // ·
  ]);

  const repairTextNode = node => {
    let value=node.nodeValue||'';
    let changed=false;
    for(const [bad,good] of badToGood){
      if(value.includes(bad)){ value=value.split(bad).join(good); changed=true; }
    }
    if(changed) node.nodeValue=value;
  };

  const repair = root => {
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    let node;
    while((node=walker.nextNode())) repairTextNode(node);
  };

  const fixBookedOn = async root => {
    const field=[...root.querySelectorAll('.sh-rd-field')].find(el=>el.querySelector('span')?.textContent?.trim()==='Booked on');
    const value=field?.querySelector('b');
    if(!value || !/bookedDate|bookingDate/.test(value.textContent||'')) return;
    const number=root.querySelector('.sh-rd-sub b')?.textContent?.trim();
    if(!number) return;
    try{
      const token=localStorage.getItem('stayhub_token')||'';
      const r=await fetch(`/reservations/${encodeURIComponent(number)}`,{headers:{Authorization:`Bearer ${token}`}});
      if(!r.ok)return;
      const data=await r.json();
      const bookingDate=data.created_at||data.booked_at||data.booking_date;
      value.textContent=bookingDate?new Date(bookingDate).toLocaleDateString('en-GB',{day:'2-digit',month:'short',year:'numeric'}):'—';
    }catch(_){ }
  };

  const repairReservation = root => { repair(root); if(root.querySelector?.('.sh-rd-shell')) fixBookedOn(root); };

  const init=()=>{
    repairReservation(document.body);
    new MutationObserver(mutations=>{
      for(const m of mutations){
        if(m.type==='characterData') repairTextNode(m.target);
        for(const n of m.addedNodes){
          if(n.nodeType===Node.TEXT_NODE) repairTextNode(n);
          else if(n.nodeType===Node.ELEMENT_NODE) repairReservation(n);
        }
      }
    }).observe(document.body,{subtree:true,childList:true,characterData:true});
  };

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
