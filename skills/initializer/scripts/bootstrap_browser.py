#!/usr/bin/env python3
"""
Bootstrap browser access for agents.
Attempts to configure browser access with minimal user intervention.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_browser_available():
    """Check if a browser is available on the system."""
    browsers = ['chrome', 'firefox', 'edge', 'safari']
    for browser in browsers:
        try:
            subprocess.run([browser, '--version'], capture_output=True, check=True)
            return browser
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    return None

def install_playwright_browsers():
    """Install Playwright browsers if not already installed."""
    try:
        subprocess.run([sys.executable, '-m', 'playwright', 'install'], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def bootstrap_browser_access():
    """Main function to bootstrap browser access."""
    print("Checking browser availability...")
    browser = check_browser_available()
    
    if browser:
        print(f"Found browser: {browser}")
        return True
    
    print("No browser found. Attempting to install Playwright browsers...")
    if install_playwright_browsers():
        print("Playwright browsers installed successfully")
        return True
    
    print("Failed to bootstrap browser access. User intervention may be required.")
    return False

if __name__ == "__main__":
    success = bootstrap_browser_access()
    sys.exit(0 if success else 1)