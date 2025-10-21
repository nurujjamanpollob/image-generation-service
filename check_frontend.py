#!/usr/bin/env python3
"""
Script to verify that all frontend files are properly created
"""

import os

def check_files():
    """Check if all required frontend files exist"""
    
    # Define expected files and directories
    expected_files = [
        "frontend/templates/index.html",
        "frontend/templates/documentation.html", 
        "frontend/templates/admin_login.html",
        "frontend/templates/admin_management.html",
        "frontend/templates/client_test.html",
        "frontend/static/",
        "main.py",
        "requirements.txt"
    ]
    
    print("Checking frontend files...")
    all_good = True
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_good = False
    
    if all_good:
        print("\n✅ All frontend files are properly created!")
        print("To run the application:")
        print("1. Set your ADMIN_API_KEY environment variable")
        print("2. Run: python main.py")
        print("3. Visit http://localhost:8000 in your browser")
    else:
        print("\n❌ Some files are missing. Please check the setup.")
    
    return all_good

if __name__ == "__main__":
    check_files()