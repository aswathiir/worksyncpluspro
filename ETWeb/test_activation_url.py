#!/usr/bin/env python
"""
Test activation URL generation
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ETWeb.settings')
django.setup()

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from accounts.api.tokens import account_activation_token

def test_activation_url():
    """Test activation URL generation"""
    # Mock user data (we'll just use a test user ID)
    test_user_id = 1

    # Generate the link the same way the signal does
    link = '{protocol}://{domain}/activate/{uid}/{token}'.format(
        protocol='https' if settings.USE_HTTPS else 'http',
        domain=settings.BASE_URL,
        uid=urlsafe_base64_encode(force_bytes(test_user_id)),
        token='test-token'  # Using a placeholder for testing
    )

    print("🔍 Testing Activation URL Generation")
    print("=" * 50)
    print(f"USE_HTTPS: {settings.USE_HTTPS}")
    print(f"BASE_URL: {settings.BASE_URL}")
    print(f"Generated Link: {link}")

    # Check if the link looks correct
    if link.startswith('http://') and 'http://http://' not in link:
        print("✅ Link format looks correct!")
        return True
    else:
        print("❌ Link format is incorrect!")
        return False

if __name__ == "__main__":
    test_activation_url()
