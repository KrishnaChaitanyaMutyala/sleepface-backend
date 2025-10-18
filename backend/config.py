"""
Configuration management for different environments
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Determine environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Load appropriate .env file
env_file = f".env.{ENVIRONMENT}"
if Path(env_file).exists():
    load_dotenv(env_file, override=True)  # Override existing env vars
else:
    # Fallback to default .env
    load_dotenv(override=True)

# Database configuration - Atlas only
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://mkrishnachaitanya21:mkrishnachaitanya@cluster0.mwnoez2.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sleepface")

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# AI Model configuration
MODEL_PATH = os.getenv("MODEL_PATH", "./models/")
TENSORFLOW_LITE_MODELS = os.getenv("TENSORFLOW_LITE_MODELS", "True").lower() == "true"

# Firebase configuration
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_PRIVATE_KEY_ID = os.getenv("FIREBASE_PRIVATE_KEY_ID")
FIREBASE_PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY")
FIREBASE_CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
FIREBASE_CLIENT_ID = os.getenv("FIREBASE_CLIENT_ID")
FIREBASE_AUTH_URI = os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
FIREBASE_TOKEN_URI = os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if ENVIRONMENT == "production" else "DEBUG")

def get_database_config():
    """Get database configuration based on environment"""
    return {
        "mongo_url": MONGO_URL,
        "database_name": DATABASE_NAME,
        "environment": ENVIRONMENT
    }

def is_production():
    """Check if running in production environment"""
    return ENVIRONMENT == "production"

def is_development():
    """Check if running in development environment"""
    return ENVIRONMENT == "development"
