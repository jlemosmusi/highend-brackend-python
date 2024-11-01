import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    PORT = int(os.getenv("PORT", 5000))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "test")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Only use the database URL in development
    if ENVIRONMENT == "production":
        SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
