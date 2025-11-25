chrome.storage.sync.get(
  ["username", "password", "autoLoginEnabled"],
  ({ username, password, autoLoginEnabled }) => {

    const userField  = document.querySelector("input[name='username']");
    const passField  = document.querySelector("input[name='password']");
    const agreeCheck = document.querySelector("#agreepolicy");
    const loginBtn   = document.querySelector("#loginbtn");

    if (!userField || !passField) {
      console.log("LPU AutoLogin: Fields not found.");
      return;
    }

    // Create fake cursor
    function createFakeCursor() {
      const cursor = document.createElement("div");
      cursor.id = "fakeCursor";
      cursor.style.width = "18px";
      cursor.style.height = "18px";
      cursor.style.position = "fixed";
      cursor.style.top = "20px";
      cursor.style.left = "20px";
      cursor.style.zIndex = "999999";
      cursor.style.backgroundImage = "url('data:image/svg+xml;utf8,<svg width=\"32\" height=\"32\" xmlns=\"http://www.w3.org/2000/svg\"><polygon points=\"0,0 0,24 8,18 16,28 20,24 12,14 24,14\" fill=\"black\"/></svg>')";
      cursor.style.backgroundSize = "contain";
      cursor.style.backgroundRepeat = "no-repeat";
      cursor.style.transition = "all 0.5s ease";
      document.body.appendChild(cursor);
      return cursor;
    }

    function moveCursor(cursor, element) {
      return new Promise((resolve) => {
        const rect = element.getBoundingClientRect();
        cursor.style.left = rect.left + 5 + "px";
        cursor.style.top = rect.top + 5 + "px";
        setTimeout(resolve, 600);
      });
    }

    function fakeClick(element) {
      return new Promise((resolve) => {
        ["mousedown", "mouseup", "click"].forEach(evt => {
          element.dispatchEvent(
            new MouseEvent(evt, { bubbles: true, cancelable: true, view: window })
          );
        });
        setTimeout(resolve, 400);
      });
    }

    // Save credentials on first manual login
    if (!username || !password) {
      console.log("Waiting for first manual login...");
      const form = userField.form || document.querySelector("form");
      if (form) {
        form.addEventListener("submit", () => {
          chrome.storage.sync.set({
            username: userField.value.trim(),
            password: passField.value.trim(),
            autoLoginEnabled: true
          });
        });
      }
      return;
    }

    // Fill credentials
    userField.value = username;
    passField.value = password;

    if (autoLoginEnabled === false) return;

    // Start animation
    const cursor = createFakeCursor();

    // Sequence animation
    (async () => {
      // 1. Move to checkbox
      if (agreeCheck) {
        await moveCursor(cursor, agreeCheck);
        await fakeClick(agreeCheck);
      }

      // Enable login button
      if (loginBtn.disabled) loginBtn.disabled = false;

      // 2. Move to Login button
      await moveCursor(cursor, loginBtn);
      await fakeClick(loginBtn);

      // Remove cursor
      setTimeout(() => cursor.remove(), 1000);
    })();
  }
);
