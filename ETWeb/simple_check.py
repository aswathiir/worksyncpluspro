#!/usr/bin/env python
"""
Simple Supabase connectivity check without external dependencies
"""
import socket
import sys

def check_dns_resolution(hostname):
    """Check if hostname can be resolved"""
    try:
        print(f"🔍 Checking DNS resolution for: {hostname}")
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS resolved to: {ip}")
        return True, ip
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False, None

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
            print(f"❌ Port {port} is not accessible (error code: {result})")
            return False
    except Exception as e:
        print(f"❌ Port check failed: {e}")
        return False

def ping_host(hostname):
    """Simple ping test"""
    import subprocess
    import platform
    
    try:
        print(f"🔍 Pinging: {hostname}")
        
        # Determine ping command based on OS
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", "1", hostname]
        else:
            cmd = ["ping", "-c", "1", hostname]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Ping successful")
            return True
        else:
            print(f"❌ Ping failed")
            return False
    except Exception as e:
        print(f"❌ Ping test failed: {e}")
        return False

def main():
    print("🚀 Simple Supabase Connectivity Checker")
    print("=" * 50)
    
    # Your Supabase project details
    project_ref = "hlakyczavlrswrqweyed"
    db_hostname = f"db.{project_ref}.supabase.co"
    
    print(f"📋 Project Reference: {project_ref}")
    print(f"🗄️ Database Host: {db_hostname}")
    print()
    
    # Run checks
    print("--- DNS Resolution Check ---")
    dns_success, ip = check_dns_resolution(db_hostname)
    
    if dns_success:
        print(f"\n--- Ping Test ---")
        ping_success = ping_host(db_hostname)
        
        print(f"\n--- Database Port Check ---")
        port_success = check_database_port(db_hostname, 5432)
    else:
        ping_success = False
        port_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"  DNS Resolution: {'✅ PASS' if dns_success else '❌ FAIL'}")
    print(f"  Ping Test: {'✅ PASS' if ping_success else '❌ FAIL'}")
    print(f"  Database Port: {'✅ PASS' if port_success else '❌ FAIL'}")
    
    if dns_success and ping_success and port_success:
        print("\n🎉 All checks passed! Supabase should be accessible.")
        print("💡 The issue might be with your credentials or database configuration.")
        print("🔧 Try running: python test_connection.py")
    elif not dns_success:
        print("\n⚠️ DNS resolution failed. Possible solutions:")
        print("1. Check your internet connection")
        print("2. Verify the Supabase project reference is correct")
        print("3. Check if your Supabase project is active (not paused)")
        print("4. Try using a different DNS server (8.8.8.8 or 1.1.1.1)")
        print("5. Use SQLite for local development as a fallback")
    else:
        print("\n⚠️ Network connectivity issues detected.")
        print("💡 Try using SQLite for local development.")

if __name__ == "__main__":
    main()
