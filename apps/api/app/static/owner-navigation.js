(() => {
  const updateOwnerNavigation = () => {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;

    const buttons = [...sidebar.querySelectorAll('.nav-btn')];

    // Remove only the Guest and Rates tabs from the Owner Panel UI.
    buttons
      .filter(b => /^(?:♙\s*)?Guests$/i.test((b.textContent || '').trim()) || /^(?:₨\s*)?Rates$/i.test((b.textContent || '').trim()))
      .forEach(b => b.remove());

    // Keep Property below Finance as in the existing Owner Panel layout.
    const remaining = [...sidebar.querySelectorAll('.nav-btn')];
    const property = remaining.find(b => /property/i.test(b.textContent || ''));
    const finance = remaining.find(b => /finance/i.test(b.textContent || ''));
    if (property && finance && finance.nextElementSibling !== property) finance.after(property);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateOwnerNavigation);
  } else {
    updateOwnerNavigation();
  }
})();
