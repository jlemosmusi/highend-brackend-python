import logging
from flask import Blueprint, request, jsonify
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv("ENVIRONMENT") != "local":
    from db.conection import get_connection


get_user_hist = Blueprint("get_user_hist", __name__)


@get_user_hist.route("/api/user-payment-history", methods=["POST"])
def get_user_payment_history():
    """
    Ruta para obtener el historial de eventos de pago de un usuario mediante user_id o payment_intent_id.
    Retorna un JSON con los eventos relacionados al usuario.
    """
    data = request.json
   # Verificar que se envíe user_id o payment_intent_id en el body
    user_id = data.get("user_id")
    payment_intent_id = data.get("payment_intent_id")

    # Validación de que al menos uno de los parámetros esté presente
    if not user_id and not payment_intent_id:
        return jsonify({"error": "Debe proporcionar user_id o payment_intent_id para realizar la consulta"}), 400
    connection=get_connection()
    try:
        # Crear la conexión a la base de datos y ejecutar la consulta
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT id, user_id, payment_intent_id, events, status, created_at, updated_at
                FROM user_payment_history
                WHERE (user_id = %s OR payment_intent_id = %s)
            """
            cursor.execute(query, (user_id, payment_intent_id))
            history_records = cursor.fetchall()

        # Si no se encuentran registros, retorna un mensaje apropiado
        if not history_records:
            return jsonify({"message": "No se encontraron eventos para el usuario o payment_intent_id proporcionado"}), 404

        # Estructurar la respuesta JSON con los eventos
        response_data = []
        for record in history_records:
            response_data.append({
                "id": record["id"],
                "user_id": record["user_id"],
                "payment_intent_id": record["payment_intent_id"],
                "events": record["events"],
                "status": record["status"],
                "created_at": record["created_at"],
                "updated_at": record["updated_at"]
            })

        # Retornar la data estructurada como JSON
        return jsonify(response_data), 200

    except Exception as e:
        logging.error(f"Error al obtener el historial de eventos: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500