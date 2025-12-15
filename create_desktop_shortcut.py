"""
Create Desktop Shortcut for Mobile Accessory Inventory System
Run this script to create a desktop shortcut with the custom icon.
"""
import os
import sys

try:
    import winshell
    from win32com.client import Dispatch
except ImportError:
    print("Installing required packages...")
    os.system('pip install pywin32 winshell')
    import winshell
    from win32com.client import Dispatch

def create_shortcut():
    """Create a desktop shortcut for the application."""
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    desktop = winshell.desktop()
    
    # Shortcut properties
    shortcut_name = "Mobile Accessory Inventory.lnk"
    shortcut_path = os.path.join(desktop, shortcut_name)
    
    # Target - Python executable
    python_exe = sys.executable
    
    # Script to run
    main_script = os.path.join(script_dir, "frontend", "main.py")
    
    # Icon path
    icon_path = os.path.join(script_dir, "frontend", "assets", "app_icon.ico")
    
    # Working directory
    working_dir = os.path.join(script_dir, "frontend")
    
    # Create shortcut
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = python_exe
    shortcut.Arguments = f'"{main_script}"'
    shortcut.WorkingDirectory = working_dir
    shortcut.IconLocation = icon_path
    shortcut.Description = "Mobile Accessory Inventory Management System"
    shortcut.save()
    
    print(f"✓ Desktop shortcut created successfully!")
    print(f"  Location: {shortcut_path}")
    print(f"  Icon: {icon_path}")
    print(f"\nYou can now launch the app from your desktop!")

if __name__ == "__main__":
    create_shortcut()
