"""
Quick Setup Script for Firebase Authentication
Run this script to set up everything automatically
"""
import subprocess
import sys
import os

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_command(command, description):
    print(f"➤ {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {description} completed successfully")
            return True
        else:
            print(f"  ✗ {description} failed:")
            print(f"    {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print_header("Smart Waste Reporting - Firebase Setup")
    
    print("This script will:")
    print("1. Install required Python packages")
    print("2. Migrate your database to support Firebase")
    print("3. Verify the setup")
    print()
    
    input("Press Enter to continue...")
    
    # Step 1: Install dependencies
    print_header("Step 1: Installing Dependencies")
    success = run_command(
        "pip install -r requirements.txt",
        "Installing Python packages"
    )
    
    if not success:
        print("\n⚠ Warning: Some packages may have failed to install.")
        print("You can manually install them with: pip install -r requirements.txt")
        input("Press Enter to continue anyway...")
    
    # Step 2: Migrate database
    print_header("Step 2: Database Migration")
    
    if os.path.exists("waste_report.db"):
        print("Existing database found. Running migration...")
        run_command("python migrate_db.py", "Running database migration")
    else:
        print("No existing database found. A new one will be created when you run the app.")
    
    # Step 3: Verify setup
    print_header("Step 3: Verification")
    
    files_to_check = [
        "static/js/firebase-config.js",
        "static/js/auth.js",
        "firebase_admin_config.py",
        "templates/login.html",
        "templates/register.html"
    ]
    
    all_present = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_present = False
    
    # Summary
    print_header("Setup Complete!")
    
    if all_present:
        print("✓ All files are in place!")
        print()
        print("Next steps:")
        print()
        print("1. Enable Email/Password & Google authentication in Firebase Console:")
        print("   https://console.firebase.google.com/project/smart-waste-reporting/authentication/providers")
        print()
        print("2. Run your application:")
        print("   python app.py")
        print()
        print("3. Open your browser to: http://localhost:5000")
        print()
        print("📖 For detailed instructions, see: FIREBASE_SETUP.md")
    else:
        print("⚠ Some files are missing. Please check the setup.")
        print("📖 See FIREBASE_SETUP.md for manual setup instructions")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
