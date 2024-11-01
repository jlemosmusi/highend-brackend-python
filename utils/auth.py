# import hashlib
# from functools import wraps
# from flask import request, jsonify
# import logging
# from db.conection import connection

# def verify_sanctum_token(token):
#     try:
#         token_id, token_value = token.split('|')
#         hashed_token = hashlib.sha256(token_value.encode()).hexdigest()

#         cursor = connection.cursor()
#         cursor.execute("""
#             SELECT tokenable_id FROM personal_access_tokens 
#             WHERE id = %s AND token = %s
#         """, (token_id, hashed_token))
        
#         result = cursor.fetchone()
#         cursor.close()  # Cierra el cursor después de usarlo
        

#         if result:
#             logging.info(f"Token verificado para user_id: {result[0]}")
#             return result[0] ,None
#         else:
#             logging.warning("Token inválido")
#             return None, "Token inválido"

#     except Exception as e:
#         logging.error(f"Error verificando el token: {str(e)}")
#         return None, str(e)

# # Decorador para rutas protegidas
# def sanctum_auth_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         auth_header = request.headers.get("Authorization")
#         if not auth_header:
#             logging.warning("Falta el encabezado de autorización")
#             return jsonify({"error": "Falta el token de autorización"}), 401

#         try:
#             token = auth_header.split(" ")[1]
#         except IndexError:
#             logging.warning("Formato de token inválido")
#             return jsonify({"error": "Formato de token inválido"}), 401

#         user_id, error = verify_sanctum_token(token)
#         if error:
#             return jsonify({"error": error}), 401

#         kwargs["user_id"] = user_id
#         return f(*args, **kwargs)
#     return decorated_function
