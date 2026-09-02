(()=>{
  // The approval workflow is exposed by admin-approval-workflow-v2.js as window.stayhubApproveProperty.
  if(window.__stayhubApprovalV2)return;window.__stayhubApprovalV2=true;const s=document.createElement('script');s.src='/static/admin-approval-workflow-v2.js?v=3';s.defer=true;document.head.appendChild(s)
})();
