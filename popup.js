document.addEventListener("DOMContentLoaded", () => {
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const autoLoginCheckbox = document.getElementById("autoLogin");
  const saveBtn = document.getElementById("saveBtn");
  const status = document.getElementById("status");

  // Load saved values
  chrome.storage.sync.get(["username", "password", "autoLoginEnabled"], (data) => {
    if (data.username) usernameInput.value = data.username;
    if (data.password) passwordInput.value = data.password;
    autoLoginCheckbox.checked = data.autoLoginEnabled !== false;
  });

  // Save credentials
  saveBtn.addEventListener("click", () => {
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    const autoLoginEnabled = autoLoginCheckbox.checked;

    chrome.storage.sync.set(
      { username, password, autoLoginEnabled },
      () => {
        status.textContent = "Saved!";
        setTimeout(() => (status.textContent = ""), 1500);
      }
    );
  });

  // Password show/hide toggle
  const togglePassword = document.getElementById("togglePassword");
  togglePassword.addEventListener("click", () => {
    const type = passwordInput.type === "password" ? "text" : "password";
    passwordInput.type = type;
    togglePassword.textContent = type === "password" ? "👁️" : "🙈";
  });
});
