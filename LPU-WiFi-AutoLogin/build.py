#!/usr/bin/env python3
"""
LPU WiFi Auto Login - Build Script
Builds the executable for Windows and macOS
"""

import sys
import os
import platform

def check_dependencies():
    """Check if required packages are installed"""
    required = ['keyboard', 'PyInstaller', 'pystray', 'PIL']
    missing = []
    
    for package in required:
        try:
            if package == 'PIL':
                __import__('PIL')
            else:
                __import__(package)
        except ImportError:
            missing.append(package if package != 'PIL' else 'pillow')
    
    if missing:
        print("❌ Missing dependencies:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\nPlease install them using:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

def build():
    """Build the executable using PyInstaller"""
    
    print("=" * 60)
    print("LPU WiFi Auto Login - Build Script")
    print("=" * 60)
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print("=" * 60)
    
    # Import here to show better error if missing
    try:
        import PyInstaller.__main__
    except ImportError:
        print("❌ PyInstaller not found!")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)
    
    # Base arguments - WINDOWED mode (no console, GUI only)
    args = [
        'main.py',
        '--onefile',
        '--windowed',  # NO CONSOLE - GUI only
        '--noconsol/e',  # Extra flag to ensure no console
        '--name=LPU-WiFi-AutoLogin',
        '--hidden-import=keyboard',
        '--hidden-import=tkinter',
        '--hidden-import=pystray',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageDraw',
        '--clean',
    ]
    
    # Add icon if exists
    if os.path.exists('icon128.png'):
        args.append('--icon=icon128.png')
    
    # Platform-specific options
    if sys.platform == 'win32':
        print("\n🪟 Building for Windows (GUI mode - no console)")
    elif sys.platform == 'darwin':
        print("\n🍎 Building for macOS...")
        args.append('--osx-bundle-identifier=com.lpuwifi.autologin')
    else:
        print("\n🐧 Building for Linux...")
    
    print("\n🔨 Starting build process...")
    print("This may take a few minutes...\n")
    
    try:
        PyInstaller.__main__.run(args)
        print("\n" + "=" * 60)
        print("✅ BUILD SUCCESSFUL!")
        print("=" * 60)
        print(f"\n📦 Executable location: ./dist/")
        
        if sys.platform == 'win32':
            print("   → LPU-WiFi-AutoLogin.exe")
        elif sys.platform == 'darwin':
            print("   → LPU-WiFi-AutoLogin.app")
        else:
            print("   → LPU-WiFi-AutoLogin")
        
        print("\n📋 Features:")
        print("✅ Runs in background (no console window)")
        print("✅ First run shows installation GUI popup")
        print("✅ Added to Windows startup automatically")
        print("✅ Global hotkey: Ctrl+Alt+L")
        print("✅ System tray icon")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ BUILD FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("\n🔍 Checking dependencies...")
    check_dependencies()
    print("✅ All dependencies found!\n")
    
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found!")
        sys.exit(1)
    
    print("✅ main.py found!\n")
    build()