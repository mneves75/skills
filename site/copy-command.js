document.querySelectorAll('button[data-copy]').forEach((button) => {
  let resetTimer;
  button.addEventListener('click', async () => {
    clearTimeout(resetTimer);
    const command = document.getElementById(button.dataset.copy);
    const status = document.getElementById('copied');
    button.disabled = true;
    button.textContent = 'Copying';
    status.textContent = 'Copying command';
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(command.textContent);
      button.textContent = 'Copied';
      status.textContent = 'Command copied';
      resetTimer = setTimeout(() => { button.textContent = 'Copy'; }, 1500);
    } catch {
      button.textContent = 'Copy';
      status.textContent = 'Copy unavailable. Select the command and copy it manually.';
      command.focus();
    } finally {
      button.disabled = false;
    }
  });
});
