document.addEventListener("DOMContentLoaded", () => {
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const autoLoginCheckbox = document.getElementById("autoLogin");
  const saveBtn = document.getElementById("saveBtn");
  const status = document.getElementById("status");

  // Live cleaning
  usernameInput.addEventListener("input", () => {
    let val = usernameInput.value;

    if (val.includes("@")) val = val.split("@")[0];
    val = val.replace(/\D/g, "").slice(0, 8);

    usernameInput.value = val;
  });

  // Load saved
  chrome.storage.sync.get(
    ["username", "password", "autoLoginEnabled"],
    (data) => {
      if (data.username) usernameInput.value = data.username;
      if (data.password) passwordInput.value = data.password;

      autoLoginCheckbox.checked = data.autoLoginEnabled !== false;
    }
  );

  // Save
  saveBtn.addEventListener("click", () => {
    let username = usernameInput.value.trim();

    if (username.length !== 8) {
      status.textContent = "User ID must be exactly 8 digits!";
      status.style.color = "red";
      setTimeout(() => (status.textContent = ""), 1500);
      return;
    }

    const password = passwordInput.value.trim();
    const autoLoginEnabled = autoLoginCheckbox.checked;

    chrome.storage.sync.set(
      { username, password, autoLoginEnabled },
      () => {
        status.style.color = "green";
        status.textContent = "Saved!";
        setTimeout(() => (status.textContent = ""), 1500);
      }
    );
  });

  // Password toggle
  const togglePassword = document.getElementById("togglePassword");
  togglePassword.addEventListener("click", () => {
    const type =
      passwordInput.type === "password" ? "text" : "password";
    passwordInput.type = type;
    togglePassword.textContent =
      type === "password" ? "👁️" : "🙈";
  });
});
