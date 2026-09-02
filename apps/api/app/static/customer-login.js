(() => {
  const $ = (id) => document.getElementById(id);
  const sendForm = $('sendForm');
  const verifyForm = $('verifyForm');
  const emailInput = $('email');
  const codeInput = $('code');
  const message = $('msg');
  const sendButton = sendForm?.querySelector('button[type="submit"]');
  const verifyButton = verifyForm?.querySelector('button[type="submit"]');
  const changeButton = $('change');

  const msg = (text) => {
    if (message) message.textContent = text || '';
  };

  if (!sendForm || !verifyForm || !emailInput || !codeInput) return;

  sendForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = emailInput.value.trim();
    if (!email) return;

    if (sendButton) sendButton.disabled = true;
    msg('Sending verification code…');

    try {
      const response = await fetch('/public/booking-otp/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Unable to send code');

      sendForm.classList.add('hidden');
      verifyForm.classList.remove('hidden');
      msg(data.delivery === 'development'
        ? 'Verification code generated. Check the StayHub API terminal for the 6-digit code.'
        : 'Verification code sent. Check your email.');
      codeInput.focus();
    } catch (error) {
      msg(error?.message || 'Unable to send code');
    } finally {
      if (sendButton) sendButton.disabled = false;
    }
  });

  verifyForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = emailInput.value.trim();
    const code = codeInput.value.trim();
    if (!email || !code) return;

    if (verifyButton) verifyButton.disabled = true;
    msg('Verifying…');

    try {
      const response = await fetch('/public/booking-otp/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Verification failed');

      localStorage.setItem('stayhub_token', data.access_token);
      localStorage.setItem('stayhub_customer_email', email);
      window.location.href = '/my-reservations';
    } catch (error) {
      msg(error?.message || 'Verification failed');
    } finally {
      if (verifyButton) verifyButton.disabled = false;
    }
  });

  changeButton?.addEventListener('click', () => {
    verifyForm.classList.add('hidden');
    sendForm.classList.remove('hidden');
    codeInput.value = '';
    msg('');
    emailInput.focus();
  });
})();
