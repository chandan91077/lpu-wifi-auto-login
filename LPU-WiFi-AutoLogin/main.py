import os
import sys
import json
import tkinter as tk
from tkinter import messagebox
import keyboard
import threading
import webbrowser
import time
from pathlib import Path

EXT_CRED_FILE = "ext_credentials.json"

# -------------------------------------------------------------
# AUTO-START ON WINDOWS
# -------------------------------------------------------------
def add_to_startup():
    """Add this program to Windows startup"""
    if sys.platform != 'win32':
        return False
    
    try:
        import winreg
        
        # FIXED: Always use executable path when frozen
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            # If running as script, use Python + script path
            exe_path = f'"{sys.executable}" "{os.path.abspath(__file__)}"'
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "LPUWiFiAutoLogin", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        
        return True
    except Exception as e:
        print(f"Failed to add to startup: {e}")
        return False

def remove_from_startup():
    """Remove from Windows startup"""
    if sys.platform != 'win32':
        return False
    
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        try:
            winreg.DeleteValue(key, "LPUWiFiAutoLogin")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except:
        return False

def is_in_startup():
    """Check if already in startup"""
    if sys.platform != 'win32':
        return False
    
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, "LPUWiFiAutoLogin")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except:
        return False

# -------------------------------------------------------------
# SYSTEM TRAY ICON
# -------------------------------------------------------------
def create_system_tray():
    """Create system tray icon"""
    try:
        from pystray import Icon, Menu, MenuItem
        from PIL import Image, ImageDraw
        
        def create_icon_image():
            width = 64
            height = 64
            color1 = (33, 150, 243)
            color2 = (255, 255, 255)
            
            image = Image.new('RGB', (width, height), color1)
            dc = ImageDraw.Draw(image)
            
            dc.ellipse([20, 35, 44, 59], fill=color2)
            dc.arc([10, 25, 54, 69], 0, 180, fill=color2, width=4)
            dc.arc([5, 15, 59, 79], 0, 180, fill=color2, width=4)
            
            return image
        
        def on_quit(icon, item):
            icon.stop()
            os._exit(0)
        
        def on_open_settings(icon, item):
            webbrowser.open("https://internet.lpu.in/24online/")
        
        menu = Menu(
            MenuItem("LPU WiFi Auto Login", lambda: None, enabled=False),
            MenuItem("Press Ctrl+Alt+L to login", lambda: None, enabled=False),
            Menu.SEPARATOR,
            MenuItem("Open Login Page", on_open_settings),
            MenuItem("Quit", on_quit)
        )
        
        icon = Icon("LPU WiFi", create_icon_image(), "LPU WiFi Auto Login", menu)
        return icon
    except ImportError:
        return None

# -------------------------------------------------------------
# WELCOME WINDOW
# -------------------------------------------------------------
def show_welcome_window():
    """Show welcome window on first run"""
    root = tk.Tk()
    root.title("LPU WiFi Auto Login")
    root.geometry("500x450")
    root.resizable(False, False)
    root.configure(bg="#f5f5f5")
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 250
    y = (root.winfo_screenheight() // 2) - 225
    root.geometry(f'500x450+{x}+{y}')
    
    # Header
    header_frame = tk.Frame(root, bg="#1a73e8", height=100)
    header_frame.pack(fill=tk.X)
    
    tk.Label(header_frame, text="Welcome!", 
            font=("Segoe UI", 24, "bold"), fg="white", bg="#1a73e8").pack(pady=20)
    
    tk.Label(header_frame, text="LPU WiFi Auto Login Setup Complete", 
            font=("Segoe UI", 12), fg="#e3f2fd", bg="#1a73e8").pack(pady=5)
    
    # Main Content
    main_frame = tk.Frame(root, bg="#ffffff", relief=tk.FLAT)
    main_frame.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)
    
    info_text = """
SETUP COMPLETE

- App installed successfully
- Auto-start enabled (runs on Windows startup)
- Press Ctrl+Alt+L anytime to auto-login
- Works globally, even when Chrome is closed
- First time: Enter credentials when prompted
- App will run in background (check system tray)
    """
    
    tk.Label(main_frame, text=info_text, 
            font=("Segoe UI", 11), justify="left", 
            bg="#ffffff", fg="#333").pack(pady=20)
    
    # Button
    start_btn = tk.Button(root, text="Start Using App", 
             command=root.destroy,
             bg="#1a73e8", fg="white", 
             font=("Segoe UI", 12, "bold"),
             width=25, height=2,
             relief=tk.FLAT, cursor="hand2",
             activebackground="#1565c0")
    start_btn.pack(pady=20)
    
    root.mainloop()

# -------------------------------------------------------------
# MAIN APPLICATION CLASS
# -------------------------------------------------------------
class LPUWiFiApp:
    def __init__(self):
        self.config_file = self.get_config_path()
        self.credentials = None

        # Try loading credentials
        ext_creds = self.load_from_extension()
        if ext_creds:
            self.credentials = ext_creds
            self.save_credentials(ext_creds["username"], ext_creds["password"])
            print("\n[SUCCESS] Loaded credentials from Chrome extension")
        else:
            self.credentials = self.load_credentials()
            if self.credentials:
                print("\n[SUCCESS] Loaded credentials from local storage")

        if not self.credentials:
            print("\n[WARNING] No credentials found - showing setup window")
            self.show_setup_window()
        else:
            self.start_hotkey_listener()

    def get_config_path(self):
        """Get config file path"""
        if sys.platform == 'win32':
            app_data = os.getenv('APPDATA')
            config_dir = os.path.join(app_data, 'LPUWiFiAutoLogin')
        else:
            home = str(Path.home())
            config_dir = os.path.join(home, '.lpuwifi')

        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'credentials.json')

    def load_credentials(self):
        """Load stored credentials"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print("Error loading credentials:", e)
        return None

    def load_from_extension(self):
        """Load credentials from extension shared file"""
        config_dir = os.path.dirname(self.config_file)
        ext_file = os.path.join(config_dir, EXT_CRED_FILE)

        if os.path.exists(ext_file):
            try:
                with open(ext_file, "r") as f:
                    data = json.load(f)
                if "username" in data and "password" in data:
                    return data
            except:
                return None
        return None

    def save_credentials(self, username, password):
        """Save credentials locally"""
        try:
            creds = {"username": username, "password": password}
            with open(self.config_file, "w") as f:
                json.dump(creds, f)

            if sys.platform != 'win32':
                os.chmod(self.config_file, 0o600)

            self.credentials = creds
            return True
        except Exception as e:
            print("Error saving credentials:", e)
            return False

    def show_setup_window(self):
        """Show modern setup window"""
        self.setup_window = tk.Tk()
        self.setup_window.title("LPU WiFi Auto Login - Setup")
        self.setup_window.geometry("450x520")
        self.setup_window.resizable(False, False)
        self.setup_window.configure(bg="#f5f5f5")

        self.setup_window.update_idletasks()
        x = (self.setup_window.winfo_screenwidth() // 2) - 225
        y = (self.setup_window.winfo_screenheight() // 2) - 260
        self.setup_window.geometry(f'450x520+{x}+{y}')

        # Header
        header_frame = tk.Frame(self.setup_window, bg="#1a73e8", height=80)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="LPU WiFi Auto Login", 
                font=("Segoe UI", 20, "bold"), fg="white", bg="#1a73e8").pack(pady=20)

        # Main Content
        main_frame = tk.Frame(self.setup_window, bg="#ffffff", relief=tk.FLAT)
        main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Enter Your Credentials", 
                font=("Segoe UI", 14, "bold"), fg="#333", bg="#ffffff").pack(pady=20)

        # User ID Field
        tk.Label(main_frame, text="User ID (8 digits):", 
                font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#333").pack(pady=(10, 5), anchor='w', padx=20)
        self.username_entry = tk.Entry(main_frame, width=30, font=("Segoe UI", 12),
                                      relief=tk.SOLID, bd=1, highlightthickness=1,
                                      highlightbackground="#1a73e8", highlightcolor="#1a73e8")
        self.username_entry.pack(pady=5, ipady=8, padx=20)

        # Password Field
        tk.Label(main_frame, text="Password:", 
                font=("Segoe UI", 11, "bold"), bg="#ffffff", fg="#333").pack(pady=(20, 5), anchor='w', padx=20)
        self.password_entry = tk.Entry(main_frame, width=30, 
                                      font=("Segoe UI", 12), show="*",
                                      relief=tk.SOLID, bd=1, highlightthickness=1,
                                      highlightbackground="#1a73e8", highlightcolor="#1a73e8")
        self.password_entry.pack(pady=5, ipady=8, padx=20)

        # Info text
        info_label = tk.Label(main_frame, text="Press Ctrl+Alt+L anytime to auto-login", 
                font=("Segoe UI", 9), fg="#666", bg="#ffffff")
        info_label.pack(pady=20)

        # Buttons
        button_frame = tk.Frame(self.setup_window, bg="#f5f5f5")
        button_frame.pack(pady=20)

        save_btn = tk.Button(button_frame, text="Save and Start", 
                            bg="#1a73e8", fg="white", 
                            font=("Segoe UI", 12, "bold"),
                            command=self.manual_save, width=28, height=2,
                            relief=tk.FLAT, cursor="hand2",
                            activebackground="#1565c0")
        save_btn.pack(pady=5)

        self.setup_window.mainloop()

    def manual_save(self):
        """Manual save credentials"""
        u = self.username_entry.get().strip()
        p = self.password_entry.get().strip()

        u = ''.join(filter(str.isdigit, u))[:8]

        if len(u) != 8:
            messagebox.showwarning("Invalid Input", "User ID must be exactly 8 digits!")
            return

        if not p:
            messagebox.showwarning("Missing Input", "Password cannot be empty!")
            return

        if self.save_credentials(u, p):
            messagebox.showinfo("Success", "Credentials saved successfully!\n\nPress Ctrl+Alt+L to auto-login!")
            self.setup_window.destroy()
            self.start_hotkey_listener()
        else:
            messagebox.showerror("Error", "Failed to save credentials!")

    def start_hotkey_listener(self):
        """Start global hotkey listener with credentials"""
        print("\n" + "=" * 60)
        print("LPU WiFi Auto Login is ACTIVE")
        print("=" * 60)
        print("[SUCCESS] Credentials loaded")
        print(f"[INFO] User ID: {self.credentials['username']}")
        print("[INFO] Press Ctrl+Alt+L globally to auto-login")
        print("=" * 60)
        print("\n[INFO] App running in background\n")

        # Register GLOBAL hotkey
        keyboard.add_hotkey("ctrl+alt+l", self.trigger_login, suppress=False)

        tray_icon = create_system_tray()
        
        if tray_icon:
            print("[SUCCESS] Running in system tray\n")
            tray_icon.run()
        else:
            try:
                keyboard.wait()
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)

    def start_hotkey_listener_without_creds(self):
        """Start listener without credentials"""
        print("\n" + "=" * 60)
        print("Waiting for credentials...")
        print("=" * 60)
        print("[WARNING] No credentials found")
        print("[INFO] Enter credentials in the app")
        print("[INFO] Checking every 10 seconds...")
        print("=" * 60 + "\n")

        def check_credentials_periodically():
            while True:
                time.sleep(10)
                ext_creds = self.load_from_extension()
                if ext_creds:
                    self.credentials = ext_creds
                    self.save_credentials(ext_creds["username"], ext_creds["password"])
                    print("\n[SUCCESS] Credentials found!")
                    print(f"[INFO] User ID: {ext_creds['username']}")
                    print("[INFO] Global hotkey active!\n")
                    break
        
        checker_thread = threading.Thread(target=check_credentials_periodically, daemon=True)
        checker_thread.start()

        # Register GLOBAL hotkey
        keyboard.add_hotkey("ctrl+alt+l", self.trigger_login, suppress=False)

        tray_icon = create_system_tray()
        
        if tray_icon:
            print("[SUCCESS] Running in system tray\n")
            tray_icon.run()
        else:
            try:
                keyboard.wait()
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)

    def trigger_login(self):
        """Trigger login"""
        if not self.credentials:
            print("\n[WARNING] No credentials available! Enter credentials in the app.")
            return

        print("\n" + "=" * 60)
        print("GLOBAL HOTKEY TRIGGERED")
        print("=" * 60)
        print(f"[INFO] User: {self.credentials['username']}")
        print("[INFO] Opening browser...")
        print("=" * 60)
        
        webbrowser.open("https://internet.lpu.in/24online/")
        
        print("\n[SUCCESS] Browser opened!")
        print("[INFO] Ready to login\n")

# -------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------
if __name__ == "__main__":
    config_dir = os.path.join(os.getenv('APPDATA') if sys.platform == 'win32' 
                              else str(Path.home()), 
                              'LPUWiFiAutoLogin' if sys.platform == 'win32' else '.lpuwifi')
    os.makedirs(config_dir, exist_ok=True)
    
    first_run_marker = os.path.join(config_dir, '.first_run_complete')
    
    # Check if first run
    if not os.path.exists(first_run_marker):
        print("[INFO] First run detected!")
        
        # Add to startup
        if sys.platform == 'win32':
            if add_to_startup():
                print("[SUCCESS] Added to Windows Startup")
            else:
                print("[WARNING] Could not add to startup")
        
        # Show welcome window
        show_welcome_window()
        
        # Mark as completed
        open(first_run_marker, 'w').close()
    else:
        # Not first run - ensure in startup
        if sys.platform == 'win32' and not is_in_startup():
            print("[WARNING] Re-adding to startup...")
            add_to_startup()
    
    print("\n[INFO] Checking for credentials...")
    app = LPUWiFiApp()