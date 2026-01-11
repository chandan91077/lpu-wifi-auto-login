// content.js - Auto-fill and login on LPU WiFi page ONLY

(function() {
    'use strict';
    
    console.log("🔵 LPU WiFi Extension: Content script loaded on:", window.location.href);
    
    // Verify we're on the correct page
    if (!window.location.href.includes('internet.lpu.in/24online')) {
        console.log("⚠️ Not on LPU WiFi page, exiting...");
        return;
    }
    
    console.log("✅ On LPU WiFi login page!");
    
    function autoLogin() {
        console.log("🔍 Checking for saved credentials...");
        
        chrome.storage.local.get(['username', 'password'], function(data) {
            if (data.username && data.password) {
                console.log("✅ Credentials found! Filling form...");
                console.log("👤 Username:", data.username);
                
                // Find and fill username field
                const usernameField = document.querySelector('input[name="username"]') || 
                                     document.querySelector('input[type="text"]') ||
                                     document.querySelector('#username');
                
                // Find and fill password field
                const passwordField = document.querySelector('input[name="password"]') || 
                                     document.querySelector('input[type="password"]') ||
                                     document.querySelector('#password');
                
                // Find submit button
                const submitButton = document.querySelector('input[type="submit"]') || 
                                    document.querySelector('button[type="submit"]') ||
                                    document.querySelector('input[value="Login"]') ||
                                    document.querySelector('button');
                
                if (usernameField && passwordField) {
                    console.log("📝 Filling username field...");
                    usernameField.value = data.username;
                    
                    console.log("📝 Filling password field...");
                    passwordField.value = data.password;
                    
                    // Trigger change events (some forms require this)
                    usernameField.dispatchEvent(new Event('input', { bubbles: true }));
                    usernameField.dispatchEvent(new Event('change', { bubbles: true }));
                    passwordField.dispatchEvent(new Event('input', { bubbles: true }));
                    passwordField.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    console.log("✅ Form filled successfully!");
                    
                    // Auto-submit after a short delay
                    if (submitButton) {
                        setTimeout(() => {
                            console.log("🚀 Submitting form...");
                            submitButton.click();
                            console.log("✅ Login submitted!");
                        }, 500);
                    } else {
                        console.warn("⚠️ Submit button not found - form filled but not submitted");
                        console.log("💡 User can manually click submit button");
                    }
                } else {
                    console.error("❌ Login form fields not found!");
                    console.log("Debug info:");
                    console.log("- Username field found:", !!usernameField);
                    console.log("- Password field found:", !!passwordField);
                }
            } else {
                console.log("⚠️ No credentials saved yet");
                console.log("💡 Click extension icon to save credentials");
            }
        });
    }
    
    // Run auto-login when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoLogin);
    } else {
        autoLogin();
    }
    
    // Also listen for page becoming visible (in case user switches tabs)
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            console.log("👀 Page became visible, checking if login needed...");
            setTimeout(autoLogin, 500);
        }
    });
    
    console.log("✅ LPU WiFi Auto-Login script ready!");
})();