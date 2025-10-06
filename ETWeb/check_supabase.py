#!/usr/bin/env python
"""
Check Supabase project status and connectivity
"""
import socket
import requests
import sys

def check_dns_resolution(hostname):
    """Check if hostname can be resolved"""
    try:
        print(f"🔍 Checking DNS resolution for: {hostname}")
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS resolved to: {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False

def check_http_connectivity(url):
    """Check if Supabase API is accessible"""
    try:
        print(f"🔍 Checking HTTP connectivity to: {url}")
        response = requests.get(url, timeout=10)
        print(f"✅ HTTP response: {response.status_code}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP connection failed: {e}")
        return False

def check_database_port(hostname, port=5432):
    """Check if database port is accessible"""
    try:
        print(f"🔍 Checking database port {port} on: {hostname}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is accessible")
            return True
        else:
            print(f"❌ Port {port} is not accessible")
            return False
    except Exception as e:
        print(f"❌ Port check failed: {e}")
        return False

def main():
    print("🚀 Supabase Connectivity Checker")
    print("=" * 50)
    
    # Your Supabase project details
    project_ref = "hlakyczavlrswrqweyed"
    supabase_url = f"https://{project_ref}.supabase.co"
    db_hostname = f"db.{project_ref}.supabase.co"
    
    print(f"📋 Project Reference: {project_ref}")
    print(f"🌐 Supabase URL: {supabase_url}")
    print(f"🗄️ Database Host: {db_hostname}")
    print()
    
    # Run checks
    checks = [
        ("DNS Resolution", lambda: check_dns_resolution(db_hostname)),
        ("HTTP Connectivity", lambda: check_http_connectivity(supabase_url)),
        ("Database Port", lambda: check_database_port(db_hostname, 5432)),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n--- {check_name} ---")
        result = check_func()
        results.append((check_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! Supabase should be accessible.")
        print("💡 The issue might be with your credentials or database configuration.")
    else:
        print("\n⚠️ Some checks failed. Possible solutions:")
        print("1. Check your internet connection")
        print("2. Verify your Supabase project is active (not paused)")
        print("3. Check if your Supabase project reference is correct")
        print("4. Try using SQLite for local development as a fallback")

if __name__ == "__main__":
    main()
