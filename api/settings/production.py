from .base import *

ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ORIGINS = os.environ.get("CORS_ALLOW_ORIGINS")
