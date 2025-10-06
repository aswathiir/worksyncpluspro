#!/usr/bin/env python
"""
Debug environment variables
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("🔍 Environment Variables Debug")
print("=" * 50)

# Check DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
print(f"DATABASE_URL: {database_url}")

# Check if there are any other database-related env vars
for key, value in os.environ.items():
    if 'DATABASE' in key.upper() or 'DB_' in key.upper():
        print(f"{key}: {value}")

print("\n🔍 Parsed Database Components:")
if database_url:
    from urllib.parse import urlparse
    parsed = urlparse(database_url)
    print(f"Scheme: {parsed.scheme}")
    print(f"Username: {parsed.username}")
    print(f"Password: {'*' * len(parsed.password) if parsed.password else 'None'}")
    print(f"Hostname: {parsed.hostname}")
    print(f"Port: {parsed.port}")
    print(f"Database: {parsed.path.lstrip('/')}")
