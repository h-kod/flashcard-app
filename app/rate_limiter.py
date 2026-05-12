from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create limiter instance with default key function (IP address)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


def init_limiter(app):
    """Initialize rate limiter with the Flask app."""
    limiter.init_app(app)
    return limiter
