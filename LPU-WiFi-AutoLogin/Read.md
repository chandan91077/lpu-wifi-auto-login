# requirements.txt
keyboard==0.13.5
pyinstaller==6.3.0

# ============================================
# BUILD INSTRUCTIONS
# ============================================

# 1. Install dependencies
pip install -r requirements.txt

# 2. Build for Windows
pyinstaller --onefile --windowed --name "LPU-WiFi-AutoLogin" --icon=icon128.png main.py

# 3. Build for macOS
pyinstaller --onefile --windowed --name "LPU-WiFi-AutoLogin" --icon=icon128.png main.py

# Output will be in the 'dist' folder

# ============================================
# ALTERNATIVE: Build Script (build.py)
# ============================================
# Save this as build.py and run: python build.py
import PyInstaller.__main__
import sys
import os

def build():
    args = [
        'main.py',
        '--onefile',
        '--windowed',
        '--name=LPU-WiFi-AutoLogin',
        '--add-data=icon128.png:.',
        '--hidden-import=keyboard',
        '--hidden-import=tkinter',
    ]
    
    if sys.platform == 'win32':
        args.append('--icon=icon128.png')
    elif sys.platform == 'darwin':
        args.append('--icon=icon128.png')
    
    PyInstaller.__main__.run(args)
    print("\n✅ Build complete! Check the 'dist' folder for the executable.")

if __name__ == '__main__':
    build()

# ============================================
# PROJECT STRUCTURE
# ============================================
# LPU-WiFi-AutoLogin/
# ├── main.py (the Python script above)
# ├── requirements.txt
# ├── build.py
# ├── icon128.png
# └── extension/
#     ├── manifest.json
#     ├── content.js
#     ├── popup.html
#     ├── popup.js
#     └── icon128.png

# ============================================
# USAGE INSTRUCTIONS FOR END USERS
# ============================================
# 1. Run the executable
# 2. First time: Enter LPU credentials
# 3. Install Chrome extension (follow prompts)
# 4. Press Ctrl+Alt+L anytime to trigger auto-login