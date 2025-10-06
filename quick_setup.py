#!/usr/bin/env python3
"""
Quick setup script for Employee Tracker with integrated collaboration features
Run this from the Employee-Tracker root directory
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and return success status"""
    try:
        print(f"🔄 Running: {command}")
        result = subprocess.run(command, shell=True, cwd=cwd, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {command}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        return False

def check_requirements():
    """Check if required tools are available"""
    print("🔍 Checking requirements...")
    
    # Check Python
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Python not found. Please install Python 3.8+")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 14+")
        return False
    
    return True

def setup_virtual_environment():
    """Set up Python virtual environment"""
    print("\n🐍 Setting up Python virtual environment...")
    
    if not run_command("python -m venv venv"):
        return False
    
    print("✅ Virtual environment created")
    return True

def install_dependencies():
    """Install Python and Node.js dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Activate virtual environment and install Python packages
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    if not run_command(f"{pip_cmd} install -r ETWeb/requirements.txt"):
        return False
    
    # Install Node.js packages
    if not run_command("npm install", cwd="ETWeb"):
        return False
    
    print("✅ Dependencies installed")
    return True

def setup_database():
    """Set up database with migrations"""
    print("\n🗄️ Setting up database...")
    
    if os.name == 'nt':  # Windows
        python_cmd = "..\\venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "../venv/bin/python"
    
    # Run migrations
    if not run_command(f"{python_cmd} manage.py makemigrations", cwd="ETWeb"):
        return False
    
    if not run_command(f"{python_cmd} manage.py makemigrations collaboration", cwd="ETWeb"):
        return False
    
    if not run_command(f"{python_cmd} manage.py migrate", cwd="ETWeb"):
        return False
    
    print("✅ Database migrations completed")
    return True

def build_frontend():
    """Build the React frontend"""
    print("\n🎨 Building frontend...")
    
    if not run_command("npm run build", cwd="ETWeb"):
        return False
    
    if os.name == 'nt':  # Windows
        python_cmd = "..\\venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "../venv/bin/python"
    
    if not run_command(f"{python_cmd} manage.py collectstatic --noinput", cwd="ETWeb"):
        return False
    
    print("✅ Frontend built successfully")
    return True

def create_superuser():
    """Create Django superuser"""
    print("\n👤 Creating superuser...")
    
    if os.name == 'nt':  # Windows
        python_cmd = "..\\venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "../venv/bin/python"
    
    print("Please create a superuser account for Django admin:")
    if not run_command(f"{python_cmd} manage.py createsuperuser", cwd="ETWeb", check=False):
        print("⚠️ Superuser creation skipped or failed")
    else:
        print("✅ Superuser created")
    
    return True

def setup_sample_data():
    """Set up sample collaboration data"""
    print("\n📊 Setting up sample data...")
    
    if os.name == 'nt':  # Windows
        python_cmd = "..\\venv\\Scripts\\python"
    else:  # Unix/Linux/macOS
        python_cmd = "../venv/bin/python"
    
    if not run_command(f"{python_cmd} manage.py setup_sample_data", cwd="ETWeb"):
        print("⚠️ Sample data setup failed, but you can continue without it")
    else:
        print("✅ Sample data created")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Employee Tracker + Collaboration Features Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("ETWeb").exists():
        print("❌ ETWeb directory not found")
        print("Please run this script from the Employee-Tracker root directory")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Setting up database", setup_database),
        ("Building frontend", build_frontend),
        ("Creating superuser", create_superuser),
        ("Setting up sample data", setup_sample_data),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            print("Setup incomplete. Please check the errors above.")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update your .env file with actual Supabase credentials")
    print("2. Start the development server:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\python ETWeb\\manage.py runserver")
    else:  # Unix/Linux/macOS
        print("   venv/bin/python ETWeb/manage.py runserver")
    
    print("\n🌐 Access your application:")
    print("   • Main app: http://localhost:8000")
    print("   • Admin panel: http://localhost:8000/admin")
    print("   • API docs: http://localhost:8000/api/collaboration/")
    
    print("\n🔧 Features available:")
    print("   • Employee monitoring (screenshots, activity tracking)")
    print("   • Team management and collaboration")
    print("   • Task management with time tracking")
    print("   • Real-time chat system")
    print("   • Meeting management")
    print("   • Activity metrics and analytics")
    print("   • Django admin for database management")
    
    print("\n📚 For detailed documentation, see SUPABASE_SETUP.md")

if __name__ == "__main__":
    main()
