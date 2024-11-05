import os
import psycopg2
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT")

# Función para obtener la conexión a la base de datos solo si el entorno no es "local"
def get_connection():
    if ENVIRONMENT != "local":
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD")
        )
    else:
        return None  # En entorno local, no se establece conexión

# Solo se invoca la conexión cuando se necesite explícitamente
# connection = get_connection()