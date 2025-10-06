#!/usr/bin/env python
"""
Quick database connection test
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ETWeb.settings')
django.setup()

from django.db import connection
from django.core.management.color import no_style

def test_database_connection():
    """Test database connection"""
    try:
        print("🔍 Testing database connection...")
        
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result:
            print("✅ Database connection successful!")
            print(f"📊 Database: {settings.DATABASES['default']['NAME']}")
            print(f"🔗 Engine: {settings.DATABASES['default']['ENGINE']}")
            return True
        else:
            print("❌ Database connection failed - no result")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n💡 Possible solutions:")
        print("1. Check your Supabase project is active")
        print("2. Verify the database URL is correct")
        print("3. Check your internet connection")
        print("4. Try using SQLite for local development")
        return False

def show_database_info():
    """Show current database configuration"""
    print("\n📋 Current Database Configuration:")
    db_config = settings.DATABASES['default']
    for key, value in db_config.items():
        if 'PASSWORD' in key.upper():
            print(f"  {key}: {'*' * len(str(value))}")
        else:
            print(f"  {key}: {value}")

if __name__ == "__main__":
    show_database_info()
    test_database_connection()
