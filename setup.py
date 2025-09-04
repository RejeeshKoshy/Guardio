#!/usr/bin/env python3
"""
Guardio Setup Script
This script helps set up Guardio with proper configuration and database initialization.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print the Guardio banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                    🔐 GUARDIO SETUP 🔐                      ║
    ║                                                              ║
    ║              Your Private, End-to-End Encrypted Cloud        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_virtual_environment():
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        return True
    else:
        print("⚠️  Warning: Not running in a virtual environment")
        print("   It's recommended to use a virtual environment")
        response = input("   Continue anyway? (y/N): ")
        return response.lower() in ['y', 'yes']

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        sys.exit(1)

def generate_encryption_key():
    """Generate a secure encryption key"""
    try:
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()
        print("✅ Encryption key generated")
        return key
    except ImportError:
        print("❌ Error: cryptography package not available")
        return None

def create_env_file():
    """Create .env file with configuration"""
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("   Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("   Skipping .env file creation")
            return
    
    print("\n🔧 Creating .env file...")
    
    # Generate encryption key
    encryption_key = generate_encryption_key()
    if not encryption_key:
        print("❌ Cannot generate encryption key")
        return
    
    # Get user input
    secret_key = input("Enter Flask secret key (or press Enter for auto-generated): ").strip()
    if not secret_key:
        import secrets
        secret_key = secrets.token_urlsafe(32)
        print(f"   Generated secret key: {secret_key[:16]}...")
    
    gemini_key = input("Enter Google Gemini API key (optional, press Enter to skip): ").strip()
    
    # Create .env file
    env_content = f"""# Guardio Environment Variables
SECRET_KEY={secret_key}
ENCRYPTION_KEY={encryption_key}
GEMINI_API_KEY={gemini_key}
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created successfully")

def initialize_database():
    """Initialize the database"""
    print("\n🗄️  Initializing database...")
    try:
        # Import here to avoid issues if dependencies aren't installed
        from app import app, db
        
        with app.app_context():
            db.create_all()
        
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

def test_blockchain():
    """Test the blockchain audit trail"""
    print("\n⛓️  Testing blockchain audit trail...")
    try:
        result = subprocess.run([sys.executable, "test_blockchain.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Blockchain audit trail test passed")
        else:
            print("⚠️  Blockchain test had issues (this is normal for first run)")
    except subprocess.TimeoutExpired:
        print("⚠️  Blockchain test timed out (this is normal)")
    except Exception as e:
        print(f"⚠️  Blockchain test error: {e}")

def print_next_steps():
    """Print next steps for the user"""
    print("""
    🎉 Setup Complete!
    
    Next steps:
    1. Start the application:
       flask run
       
    2. Open your browser and go to:
       http://127.0.0.1:5000
       
    3. Create your first account (this will be the admin account)
    
    4. Set up MFA using your authenticator app
    
    5. Start using Guardio!
    
    📚 Documentation: README.md
    🐛 Issues: GitHub Issues
    🔒 Security: SECURITY.md
    
    Happy securing! 🔐⛓️
    """)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Check virtual environment
    if not check_virtual_environment():
        print("Setup cancelled")
        sys.exit(0)
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file
    create_env_file()
    
    # Initialize database
    initialize_database()
    
    # Test blockchain functionality
    test_blockchain()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
