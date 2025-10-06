#!/usr/bin/env python3
"""
Quick setup script for Employee Tracker with Supabase integration
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path("ETWeb/.env")
    if not env_path.exists():
        print("❌ .env file not found in ETWeb directory")
        print("Please create .env file with your Supabase credentials")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
        
    required_vars = ['SECRET_KEY', 'DATABASE_URL', 'SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = []
    
    for var in required_vars:
        if f"{var}=" not in content or f"{var}=your-" in content or f"{var}=https://your-" in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or incomplete environment variables: {', '.join(missing_vars)}")
        print("Please update your .env file with actual values")
        return False
    
    print("✓ Environment file configured")
    return True

def main():
    """Main setup function"""
    print("🚀 Employee Tracker - Supabase Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("ETWeb").exists():
        print("❌ ETWeb directory not found")
        print("Please run this script from the Employee-Tracker root directory")
        sys.exit(1)
    
    # Check environment file
    if not check_env_file():
        print("\n📝 Please follow these steps:")
        print("1. Update ETWeb/.env with your Supabase credentials")
        print("2. Run this script again")
        sys.exit(1)
    
    print("\n📦 Installing dependencies...")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", cwd="ETWeb"):
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Install Node.js dependencies
    if not run_command("npm install", cwd="ETWeb"):
        print("❌ Failed to install Node.js dependencies")
        sys.exit(1)
    
    print("\n🗄️ Setting up database...")
    
    # Run migrations
    if not run_command("python manage.py makemigrations", cwd="ETWeb"):
        print("❌ Failed to create migrations")
        sys.exit(1)
    
    if not run_command("python manage.py migrate", cwd="ETWeb"):
        print("❌ Failed to run migrations")
        print("Please check your Supabase database connection")
        sys.exit(1)
    
    print("\n🎨 Building frontend...")
    
    # Build frontend
    if not run_command("npm run build", cwd="ETWeb"):
        print("❌ Failed to build frontend")
        sys.exit(1)
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", cwd="ETWeb"):
        print("❌ Failed to collect static files")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\n🚀 To start the application:")
    print("1. Start Redis server: redis-server")
    print("2. Start Django server: cd ETWeb && python manage.py runserver")
    print("3. Access the app at: http://localhost:8000")
    print("\n📚 For detailed instructions, see SUPABASE_SETUP.md")

if __name__ == "__main__":
    main()
