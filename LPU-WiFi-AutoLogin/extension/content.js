// ---------------------------------------------------------
// STOP CHROME AUTOFILL COMPLETELY
// ---------------------------------------------------------
const styleFix = document.createElement("style");
styleFix.innerHTML = `
input[name='username'],
input[name='password'] {
    autocomplete: off !important;
    -webkit-autocomplete: off !important;
}
input[name='username']:-webkit-autofill,
input[name='password']:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 1000px white inset !important;
    transition: background-color 5000s ease-in-out 0s !important;
}
`;
document.head.appendChild(styleFix);

// Disable autocomplete on form
const form = document.querySelector("form");
if (form) {
    form.setAttribute("autocomplete", "off");
}

// ---------------------------------------------------------
// DEBUG: Check storage on page load
// ---------------------------------------------------------
console.log("🔍 Checking storage on page load...");
chrome.storage.sync.get(["username", "password", "autoLoginEnabled"], (data) => {
  console.log("📦 Current storage state:", {
    username: data.username || "NOT SET",
    passwordLength: data.password ? data.password.length : "NOT SET",
    autoLogin: data.autoLoginEnabled
  });
});

// ---------------------------------------------------------
// MAIN LOGIN HANDLER
// ---------------------------------------------------------
chrome.storage.sync.get(
  ["username", "password", "autoLoginEnabled"],
  ({ username, password, autoLoginEnabled }) => {

    console.log("📥 Loaded from storage:", {
      username: username || "NONE",
      hasPassword: !!password,
      autoLogin: autoLoginEnabled
    });

    const userField  = document.querySelector("input[name='username']");
    const passField  = document.querySelector("input[name='password']");
    const agreeCheck = document.querySelector("#agreepolicy");
    const loginBtn   = document.querySelector("#loginbtn");

    if (!userField || !passField) {
      console.log("⚠️ Login fields not found on this page");
      return;
    }

    // Force disable Chrome autofill on fields
    userField.setAttribute("autocomplete", "off");
    passField.setAttribute("autocomplete", "off");

    // ---------------------------------------------------------
    // 1️⃣ FIRST TIME LOGIN CAPTURE (FIXED)
    // ---------------------------------------------------------
    const loginForm = userField.form || document.querySelector("form");

    // Check if we need to capture credentials
    const needsCapture = !username || !password;

    if (loginForm && needsCapture) {
      console.log("🔓 First login detected - will capture credentials");

      // Method 1: Capture on form submit
      loginForm.addEventListener("submit", (e) => {
        console.log("📝 Form submitted - capturing credentials");
        captureAndSave();
      }, { once: true });

      // Method 2: Capture on login button click (backup)
      if (loginBtn) {
        loginBtn.addEventListener("click", () => {
          console.log("🖱️ Login button clicked - capturing credentials");
          setTimeout(captureAndSave, 50);
        }, { once: true });
      }

      // Method 3: Monitor field changes (fallback)
      let captureTimeout;
      const setupCaptureMonitor = () => {
        clearTimeout(captureTimeout);
        captureTimeout = setTimeout(() => {
          if (userField.value && passField.value) {
            console.log("📊 Fields filled - preparing to capture");
          }
        }, 500);
      };

      userField.addEventListener("input", setupCaptureMonitor);
      passField.addEventListener("input", setupCaptureMonitor);

      // Capture function
      function captureAndSave() {
        let capturedUsername = userField.value.trim();
        let capturedPassword = passField.value.trim();

        console.log("🔍 Raw captured data:");
        console.log("   Username:", capturedUsername);
        console.log("   Password length:", capturedPassword ? capturedPassword.length : 0);

        // Clean username - remove @lpu.in or @lpu.com if present
        if (capturedUsername.includes("@")) {
          capturedUsername = capturedUsername.split("@")[0];
        }
        
        // Keep only digits and limit to 8
        capturedUsername = capturedUsername.replace(/\D/g, "").slice(0, 8);

        console.log("🧹 Cleaned username:", capturedUsername);

        // Validate before saving
        if (capturedUsername.length !== 8) {
          console.error("❌ Invalid username length:", capturedUsername.length, "(need 8)");
          showNotification("❌ Username must be 8 digits!");
          return;
        }

        if (!capturedPassword) {
          console.error("❌ Password is empty");
          showNotification("❌ Password cannot be empty!");
          return;
        }

        // Save credentials
        console.log("💾 Saving to storage...");
        chrome.storage.sync.set({
          username: capturedUsername,
          password: capturedPassword,
          autoLoginEnabled: true
        }, () => {
          // Check for errors
          if (chrome.runtime.lastError) {
            console.error("❌ Save failed:", chrome.runtime.lastError);
            showNotification("❌ Save failed: " + chrome.runtime.lastError.message);
            return;
          }

          console.log("✅ Credentials saved successfully!");
          console.log("   Username:", capturedUsername);
          console.log("   Password length:", capturedPassword.length);
          
          // Verify save
          chrome.storage.sync.get(["username", "password"], (data) => {
            console.log("🔍 Verification check:", {
              savedUsername: data.username,
              savedPasswordLength: data.password ? data.password.length : 0,
              matches: data.username === capturedUsername && data.password === capturedPassword
            });

            if (data.username === capturedUsername && data.password === capturedPassword) {
              console.log("✅ Verification successful!");
              showNotification("✅ Credentials saved! Open popup to verify.");
            } else {
              console.error("❌ Verification failed - data mismatch!");
              showNotification("⚠️ Save may have failed - please check popup");
            }
          });
        });
      }

      // Don't auto-fill on first login - let user enter manually
      return;
    }

    // Helper function to show notification
    function showNotification(message) {
      const notification = document.createElement("div");
      notification.textContent = message;
      notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${message.includes("✅") ? "#4CAF50" : message.includes("❌") ? "#f44336" : "#ff9800"};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        z-index: 999999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideIn 0.3s ease;
      `;
      
      const style = document.createElement("style");
      style.textContent = `
        @keyframes slideIn {
          from { transform: translateX(400px); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `;
      document.head.appendChild(style);
      
      document.body.appendChild(notification);
      
      setTimeout(() => {
        notification.style.animation = "slideIn 0.3s ease reverse";
        setTimeout(() => notification.remove(), 300);
      }, 4000);
    }

    // ---------------------------------------------------------
    // 2️⃣ AUTO-FILL LOGIN PAGE (when credentials exist)
    // ---------------------------------------------------------
    if (username && password) {
      console.log("🔐 Credentials found - auto-filling");
      
      // Clean username to only 8 digits - NO @lpu.in anywhere
      const cleanUsername = username.replace(/\D/g, "").slice(0, 8);
      
      console.log("   Using username:", cleanUsername);
      console.log("   Password length:", password.length);

      // Clear fields first to prevent Chrome autofill
      userField.value = "";
      passField.value = "";

      // Multiple attempts to override Chrome autofill
      setTimeout(() => {
        userField.value = cleanUsername;
        passField.value = password;
        console.log("✅ Fields filled (attempt 1)");
      }, 100);

      setTimeout(() => {
        userField.value = cleanUsername;
        passField.value = password;
        console.log("✅ Fields filled (attempt 2)");
      }, 300);

      setTimeout(() => {
        userField.value = cleanUsername;
        passField.value = password;
        console.log("✅ Fields filled (attempt 3)");
      }, 600);

      // STOP if auto-login disabled
      if (!autoLoginEnabled) {
        console.log("⏸️ Auto-login disabled - fields filled only");
        return;
      }

      // ---------------------------------------------------------
      // 3️⃣ AUTO LOGIN ANIMATION
      // ---------------------------------------------------------
      function createCursor() {
        const c = document.createElement("div");
        c.id = "fakeCursor";
        c.style.width = "18px";
        c.style.height = "18px";
        c.style.position = "fixed";
        c.style.top = "20px";
        c.style.left = "20px";
        c.style.zIndex = "999999";
        c.style.backgroundImage =
          "url('data:image/svg+xml;utf8,<svg width=\"32\" height=\"32\" xmlns=\"http://www.w3.org/2000/svg\"><polygon points=\"0,0 0,24 8,18 16,28 20,24 12,14 24,14\" fill=\"black\"/></svg>')";
        c.style.backgroundSize = "contain";
        c.style.transition = "all 0.5s ease";
        document.body.appendChild(c);
        return c;
      }

      function moveCursor(cursor, element) {
        return new Promise((resolve) => {
          const rect = element.getBoundingClientRect();
          cursor.style.left = rect.left + "px";
          cursor.style.top = rect.top + "px";
          setTimeout(resolve, 500);
        });
      }

      function fakeClick(element) {
        return new Promise((resolve) => {
          ["mousedown", "mouseup", "click"].forEach(evt => {
            element.dispatchEvent(
              new MouseEvent(evt, { bubbles: true })
            );
          });
          setTimeout(resolve, 300);
        });
      }

      // Wait for fields to be filled properly
      setTimeout(async () => {
        console.log("🎬 Starting auto-login animation");
        const cursor = createCursor();

        if (agreeCheck && !agreeCheck.checked) {
          await moveCursor(cursor, agreeCheck);
          await fakeClick(agreeCheck);
          console.log("✅ Checked agreement");
        }

        if (loginBtn.disabled) {
          loginBtn.disabled = false;
          console.log("✅ Enabled login button");
        }

        await moveCursor(cursor, loginBtn);
        await fakeClick(loginBtn);
        console.log("✅ Clicked login button");

        setTimeout(() => cursor.remove(), 800);
      }, 800);
    }
  }
);