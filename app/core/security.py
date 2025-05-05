
import os
from app.core.config import settings

def verify_token(token: str):
    return token == settings.api_token
