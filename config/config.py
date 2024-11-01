import os
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()

class Config:
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    # SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))
