document.getElementById('copy-prompt').addEventListener('click',async () => {
  const prompt = document.getElementById('starter');
  const status = document.getElementById('prompt-status');
  try { await navigator.clipboard.writeText(prompt.value); status.textContent = 'Copied. Paste into your assistant and replace [my street address].'; }
  catch { prompt.focus(); prompt.select(); status.textContent = 'Select and copy the prompt above, then paste into your assistant.'; }
});
