/* StayHub Owner Room Photo — instant local preview for selected files */
(function(){
'use strict';
const STYLE_ID='stayhub-room-photo-preview-style';
function installStyle(){
  if(document.getElementById(STYLE_ID)) return;
  const s=document.createElement('style'); s.id=STYLE_ID;
  s.textContent='#rpm-preview{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:10px;margin:12px 0}#rpm-preview .rpm-preview-item{position:relative;border:1px solid #e2e8f0;border-radius:9px;padding:6px;background:#f8fafc}#rpm-preview img{display:block;width:100%;height:90px;object-fit:cover;border-radius:6px}#rpm-preview .rpm-preview-name{display:block;margin-top:5px;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#475569}#rpm-preview .rpm-preview-empty{font-size:12px;color:#64748b}';
  document.head.appendChild(s);
}
function render(input){
  const modal=input.closest('#room-photo-modal'); if(!modal) return;
  let box=modal.querySelector('#rpm-preview');
  if(!box){box=document.createElement('div');box.id='rpm-preview';input.insertAdjacentElement('afterend',box)}
  const old=box.querySelectorAll('img'); old.forEach(img=>{if(img.dataset.objectUrl)URL.revokeObjectURL(img.dataset.objectUrl)});
  const files=[...(input.files||[])].filter(f=>/^image\/(jpeg|png|webp|gif)$/i.test(f.type));
  box.innerHTML=files.length?files.map((f,i)=>{const url=URL.createObjectURL(f);return `<div class="rpm-preview-item"><img src="${url}" data-object-url="${url}" alt="Selected photo ${i+1}"><span class="rpm-preview-name" title="${String(f.name).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;')}">${String(f.name).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</span></div>`}).join(''):'<div class="rpm-preview-empty">Selected photos will appear here before upload.</div>';
}
function hook(){
  installStyle();
  const modal=document.getElementById('room-photo-modal'); if(!modal) return;
  const input=modal.querySelector('#rpm-files'); if(!input||input.dataset.previewHooked==='1') return;
  input.dataset.previewHooked='1';
  input.addEventListener('change',()=>render(input));
  render(input);
}
const observer=new MutationObserver(()=>hook());
function start(){hook();observer.observe(document.body,{childList:true,subtree:true})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);else start();
})();
