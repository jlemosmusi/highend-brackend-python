import hashlib
import secrets
from flask import Blueprint, request, jsonify

loginByEmail = Blueprint("loginByEmail", __name__)


import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv("ENVIRONMENT") != "local":
    from db.conection import get_connection # Solo importa si no es "local"



# Función para generar un token seguro y su hash
def generate_token():
    plain_token = secrets.token_urlsafe(40)  # Genera el token seguro
    hashed_token = hashlib.sha256(plain_token.encode()).hexdigest()
    return plain_token, hashed_token

# Función para buscar al usuario y almacenar el token en la base de datos
def store_token_for_user(email):
    # Establece la conexión
    connection = get_connection()
    cursor = connection.cursor()

    # Busca el ID del usuario en la tabla `users` por email
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user:
        return None, "User not found"

    user_id = user[0]
    plain_token, hashed_token = generate_token()

    # Verifica si ya existe un token para este usuario
    cursor.execute("""
        SELECT id FROM personal_access_tokens 
        WHERE tokenable_id = %s AND tokenable_type = 'App\\Models\\User'
    """, (user_id,))
    existing_token = cursor.fetchone()

    if existing_token:
        # Si existe, actualiza el token
        cursor.execute("""
            UPDATE personal_access_tokens 
            SET token = %s, last_used_at = NOW()
            WHERE id = %s
        """, (hashed_token, existing_token[0]))
    else:
        # Si no existe, inserta un nuevo token
        cursor.execute("""
            INSERT INTO personal_access_tokens (tokenable_type, tokenable_id, name, token, abilities)
            VALUES ('App\\Models\\User', %s, 'api', %s, '["*"]')
        """, (user_id, hashed_token))

    connection.commit()

    # Cierra la conexión
    cursor.close()
    connection.close()

    return plain_token, None  # Devuelve el token plano para el frontend


# Ruta en el microservicio para autenticar al usuario por email
@loginByEmail.route("/login-by-email", methods=["POST"])
def login_by_email():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Genera y guarda el token
    plain_token, error = store_token_for_user(email)
    if error:
        return jsonify({"error": error}), 404

    # Devuelve el token y los detalles del usuario al frontend
    return jsonify({"token": plain_token}), 200