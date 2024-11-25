import os
import psycopg2
from dotenv import load_dotenv
import logging

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


# def get_connection():
#     return psycopg2.connect(
#             host="127.0.0.1",
#             port="5432",
#             database="dbCopyAWSHighEnd",
#             user="postgres",
#             password="Aa.111Aa.111"
#         )
# connection = get_connection()




# def get_connection():
#     return psycopg2.connect(
#             host="highend-production-instance-1.chu8gn9clulu.ap-southeast-2.rds.amazonaws.com",
#             port="5432",
#             database="postgres",
#             user="postgres",
#             password="1nPCo7ZJbkcSK86j3U93X10Y0Oj4Svsm"
#         )
# connection = get_connection()



# def get_connection():
#     return psycopg2.connect(
#             host="highend-test-instance.chu8gn9clulu.ap-southeast-2.rds.amazonaws.com",
#             port="5432",
#             database="postgres",
#             user="postgres",
#             password="1nPCo7ZJbkcSK86j3U93X10Y0Oj4Svsm"
#         )
# connection = get_connection()

# conn = psycopg2.connect(
#     host="highend-test-instance.chu8gn9clulu.ap-southeast-2.rds.amazonaws.com",
#     port="5432",
#     database="postgres",
#     user="postgres",
#     password="1nPCo7ZJbkcSK86j3U93X10Y0Oj4Svsm"
# )

# # Cursor para ejecutar consultas
# cur = conn.cursor()

# # Ejecutar una consulta de prueba
# cur.execute("SELECT NOW();")
# print(cur.fetchone())

# # Cerrar la conexión
# cur.close()
# conn.close()

# import time

# payment_intent={
#     "id":"id.asdoasdksadjksa",
#     "metadata":{
#         "user_id":"asdasdqewdas",
#         "product_ids":"asdasdadsadas,asdasdasdasd"
#     },
#     "created":int(time.time())
# }
# status="created"

# import json
# def create_user_payment_history(user_id, payment_intent, status):
#     try:
#         user_id = payment_intent.get("metadata", {}).get("user_id", "unknown_user")
#         products = payment_intent.get("metadata", {}).get("product_ids", "unknown_products")

#         initial_event = {
#             "type": "payment_intent.created",
#             "timestamp": payment_intent["created"],
#             "products":products
#         }
#         connection=get_connection()

#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT id FROM user_payment_history WHERE payment_intent_id = %s
#             """, (payment_intent['id'],))
#             existing_payment_history = cursor.fetchone()
            
#             # Si la transacción ya existe, registra un log y no inserta nada
#             if existing_payment_history:
#                 logging.info(f"existing_payment_history with PaymentIntent {payment_intent['id']}")
#                 # return existing_transaction[0]
#                 # return None
            
#             cursor.execute("""
#                 INSERT INTO user_payment_history (user_id, payment_intent_id, status, events, created_at)
#                 VALUES (%s, %s, %s, %s::jsonb, CURRENT_TIMESTAMP)
#             """, (
#                 user_id,
#                 payment_intent['id'],
#                 status,
#                 json.dumps([initial_event])
#             ))
#             connection.commit()
#             logging.info(f"User payment history created for PaymentIntent {payment_intent['id']}")
#     except Exception as e:
#         logging.error(f"Error creating user payment history: {e}")
#         connection.rollback()


#     finally:
#         connection.close()