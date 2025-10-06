"""
Supabase client configuration for Employee Tracker
"""
import os
from supabase import create_client, Client
from django.conf import settings

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance
    """
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    return create_client(url, key)

def get_supabase_service_client() -> Client:
    """
    Create and return a Supabase service client instance (for admin operations)
    """
    url = os.environ.get('SUPABASE_URL')
    service_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not url or not service_key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")
    
    return create_client(url, service_key)

# Initialize clients
try:
    supabase_client = get_supabase_client()
    supabase_service_client = get_supabase_service_client()
except ValueError as e:
    print(f"Warning: Supabase client initialization failed: {e}")
    supabase_client = None
    supabase_service_client = None
