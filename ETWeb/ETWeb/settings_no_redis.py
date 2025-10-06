# Temporary settings without Redis for initial testing
# Copy this content to settings.py if Redis is not available

# Replace the CHANNEL_LAYERS section in settings.py with this:
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    },
}

# This will use in-memory channels instead of Redis
# Note: This won't work for production or multiple server instances
