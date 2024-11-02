# import logging
# from flask import Blueprint, request, jsonify
# import stripe
# from config.config import Config
# from dotenv import load_dotenv
# from utils.generate_id import generate_ulid

# # Cargar las variables de entorno directamente en webhook.py como depuración
# load_dotenv()
# # from db.conection import engine
# # from db.conection import connection
# import os
# if os.getenv("ENVIRONMENT") == "production":
#     print('es con base de datos')
#     from db.conection import connection

# import json
# # Crear un Blueprint para el webhook de Stripe
# webhook_bp = Blueprint("webhook", __name__)

# # Manejo de Webhook de Stripe
# @webhook_bp.route("/webhook", methods=["POST"])
# def stripe_webhook():
#     logging.info("Webhook recibido")
#     print(os.getenv("ENVIRONMENT"))
#     payload = request.get_data(as_text=True)
#     # sig_header = request.headers.get("Stripe-Signature")
#     event= request.json

#     try:
#         # event = stripe.Webhook.construct_event(payload, sig_header, Config.WEBHOOK_SECRET)
#         logging.info(f"Evento de Stripe: {event['type']}")

#         payment_intent = event["data"]["object"]
#         payment_intent_id = payment_intent["id"]
#         user_id = payment_intent.get("metadata", {}).get("user_id", "unknown_user")

#         # Intentos de Pago
#         # PENDING en transactions.status
#         if event["type"] == "payment_intent.created":
#             # Este evento ocurre al iniciar un pago.
#             # Útil para monitorear cuándo un usuario inicia el proceso de pago.
#             logging.info(f"PaymentIntent creado: {payment_intent['id']}")
#             # Guardar en `transactions` con status "PENDING" ya que está en el inicio del proceso de pago.
#             create_transaction(payment_intent, "PENDING")
#             create_user_payment_history(user_id, payment_intent, "payment_intent.created")


#         # REQUIRES_ACTION en transactions.status
#         elif event["type"] == "payment_intent.requires_action":
#             # Ocurre cuando se necesita una acción extra del usuario, 
#             # como autenticación o verificación. Útil para notificar al usuario.
#             logging.info(f"PaymentIntent requiere acción: {payment_intent['id']}")
#             update_transaction_status(payment_intent_id, "REQUIRES_ACTION")
#             update_user_payment_history(payment_intent_id, "payment_intent.requires_action")

#         # PROCESSING en transactions.status
#         elif event["type"] == "payment_intent.processing":
#             # Indica que el pago está en proceso. Permite saber que el usuario está
#             # avanzando y que el pago se está procesando.
#             payment_intent = event["data"]["object"]
#             logging.info(f"PaymentIntent en proceso: {payment_intent['id']}")
#             update_transaction_status(payment_intent['id'], "PROCESSING")
#             update_user_payment_history(payment_intent_id, "payment_intent.processing")


#         # SUCCESSFUL en transactions.status
#         # PREPARING en orders.status
#         elif event["type"] == "payment_intent.succeeded":
#             # Marca un pago exitoso, confirmando que el usuario completó el pago.
#             payment_intent = event["data"]["object"]
#             logging.info(f"PaymentIntent exitoso: {payment_intent['id']}")
#             update_transaction_status(payment_intent['id'], "SUCCESSFUL")
#             create_order(payment_intent)
#             update_user_payment_history(payment_intent_id, "payment_intent.succeeded")


#         # FAILED en transactions.status
#         elif event["type"] == "payment_intent.payment_failed":
#             # Ocurre cuando un pago falla. Es útil para hacer seguimiento de pagos
#             # rechazados y notificar al usuario o intentar alternativas de pago.
#             payment_intent = event["data"]["object"]
#             logging.info(f"PaymentIntent fallido: {payment_intent['id']}")
#             update_transaction_status(payment_intent['id'], "FAILED")
#             update_user_payment_history(payment_intent_id, "payment_intent.payment_failed")

#         # CANCELED en transactions.status
#         elif event["type"] == "payment_intent.canceled":
#             # Indica que el usuario canceló el pago antes de completarlo.
#             payment_intent = event["data"]["object"]
#             logging.info(f"PaymentIntent cancelado: {payment_intent['id']}")
#             update_transaction_status(payment_intent['id'], "CANCELED")
#             update_user_payment_history(payment_intent_id, "payment_intent.canceled")

#         # REQUIRES_CONFIRMATION en transactions.status
#         elif event["type"] == "payment_intent.amount_capturable_updated":
#             # Este evento muestra cuando hay fondos que pueden ser capturados.
#             # Útil si necesitas capturar montos específicos en lugar de la totalidad.
#             payment_intent = event["data"]["object"]
#             logging.info(f"PaymentIntent fondos capturables: {payment_intent['id']}")
#             update_transaction_status(payment_intent['id'], "REQUIRES_CONFIRMATION")
#             update_user_payment_history(payment_intent_id, "payment_intent.amount_capturable_updated")




#         # Sesiones de Checkout
#         # TODO
#         elif event["type"] == "checkout.session.completed":
#             # Indica que el usuario ha completado la sesión de Stripe Checkout.
#             session = event["data"]["object"]
#             logging.info(f"Checkout completado: {session['id']}")
#             # update_order_status(session['id'], "Completed")
#             update_user_payment_history(payment_intent_id, "checkout.session.completed")



#         # SUCCESSFUL en transactions.status
#         elif event["type"] == "checkout.session.async_payment_succeeded":
#             # Evento para pagos asincrónicos como Afterpay. Marca que el pago se
#             # completó exitosamente en Stripe.
#             session = event["data"]["object"]
#             logging.info(f"Pago asincrónico exitoso: {session['id']}")
#             update_transaction_status(session['payment_intent'], "SUCCESSFUL")
#             update_user_payment_history(payment_intent_id, "checkout.session.async_payment_succeeded")


#         # FAILED en transactions.status
#         elif event["type"] == "checkout.session.async_payment_failed":
#             # Indica que un pago asi  asinncrónico falló, útil para Afterpay y similares.
#             session = event["data"]["object"]
#             logging.info(f"Pago asincrónico fallido: {session['id']}")
#             update_transaction_status(session['payment_intent'], "FAILED")
#             update_user_payment_history(payment_intent_id, "checkout.session.async_payment_failed")

#         # CANCELED en transactions,status
#         elif event["type"] == "checkout.session.expired":
#             # Marca que la sesión de pago ha expirado sin completarse.
#             session = event["data"]["object"]
#             logging.info(f"Checkout expirado: {session['id']}")
#             update_order_status(session['metadata']['order_id'], "CANCELED")
#             update_user_payment_history(payment_intent_id, "checkout.session.expired")


#         # Eventos de Clientes
#         # TODO
#         elif event["type"] == "customer.created":
#             # Notifica que se creó un cliente nuevo en Stripe.
#             # Útil para añadir el cliente a tus registros.
#             customer = event["data"]["object"]
#             logging.info(f"Cliente creado: {customer['id']}")
#             update_user_payment_history(payment_intent_id, "customer.created")


#         # TODO
#         elif event["type"] == "customer.deleted":
#             # Indica que el cliente ha sido eliminado.
#             customer = event["data"]["object"]
#             logging.info(f"Cliente eliminado: {customer['id']}")
#             update_user_payment_history(payment_intent_id, "customer.deleted")


#         # TODO
#         elif event["type"] == "customer.subscription.created":
#             # Muestra cuando se crea una nueva suscripción para el cliente.
#             subscription = event["data"]["object"]
#             logging.info(f"Suscripción creada: {subscription['id']}")
#             update_user_payment_history(payment_intent_id, "customer.subscription.created")

#         # TODO
#         elif event["type"] == "customer.subscription.deleted":
#             # Informa que una suscripción ha sido cancelada.
#             subscription = event["data"]["object"]
#             logging.info(f"Suscripción cancelada: {subscription['id']}")
#             update_user_payment_history(payment_intent_id, "customer.subscription.deleted")

#         # Eventos de Facturación (Invoices)
#         # TODO
#         elif event["type"] == "invoice.payment_succeeded":
#             # Marca el éxito de un pago de factura.
#             invoice = event["data"]["object"]
#             logging.info(f"Pago de factura exitoso: {invoice['id']}")
#             update_user_payment_history(payment_intent_id, "invoice.payment_succeeded")

#         # TODO
#         elif event["type"] == "invoice.payment_failed":
#             # Indica que el pago de la factura falló.
#             invoice = event["data"]["object"]
#             logging.info(f"Pago de factura fallido: {invoice['id']}")
#             # update_invoice_status(invoice['id'], "Failed")
#             update_user_payment_history(payment_intent_id, "invoice.payment_failed")



#         # Eventos de Reembolsos
#         # REFUND en transactions.status
#         # REFUNDED en orders.status
#         elif event["type"] == "charge.refunded":
#             # Notifica cuando se ha emitido un reembolso total o parcial.
#             charge = event["data"]["object"]
#             logging.info(f"Reembolso emitido: {charge['id']}")
#             update_transaction_status(charge['id'], "REFUND")
#             update_order_status(charge, "REFUNDED")
#             update_user_payment_history(payment_intent_id, "charge.refunded")


#         # TODO
#         elif event["type"] == "refund.updated":
#             # Informa si hay algún cambio en el estado de un reembolso.
#             refund = event["data"]["object"]
#             logging.info(f"Reembolso actualizado: {refund['id']}")
#             update_user_payment_history(payment_intent_id, "refund.updated")


#         # Eventos de Verificación de Identidad
#         # TODO
#         elif event["type"] == "identity.verification_session.verified":
#             # Indica que la verificación de identidad del usuario fue aprobada.
#             session = event["data"]["object"]
#             logging.info(f"Verificación de identidad completada: {session['id']}")
#             update_user_payment_history(payment_intent_id, "identity.verification_session.verified")

#         # TODO
#         elif event["type"] == "identity.verification_session.requires_action":
#             # Ocurre cuando el usuario debe realizar una acción adicional para
#             # completar la verificación de identidad.
#             session = event["data"]["object"]
#             logging.info(f"Verificación de identidad requiere acción: {session['id']}")
#             update_user_payment_history(payment_intent_id, "identity.verification_session.requires_action")

#         return jsonify(success=True), 200

#     except ValueError:
#         logging.error("Payload inválido")
#         return jsonify({"error": "Invalid payload"}), 400
#     except stripe.error.SignatureVerificationError:
#         logging.error("Firma de webhook inválida")
#         return jsonify({"error": "Invalid signature"}), 400




# def create_transaction(payment_intent, status):
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             INSERT INTO transactions (id, currency_id, amount, type, external_id, status, created_at)
#             VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
#         """, (
#             generate_ulid(),                       # generate new id
#             '01he2qdgggyeg4e05swctvtkvf',            # Currency ID
#             payment_intent['amount'] / 100,        # Convert amount to a usable value
#             "PAYMENT",                             # Transaction type
#             payment_intent['id'],                  # External ID, same as PaymentIntent ID
#             status                                 # Status, e.g., "PENDING"
#         ))
#         connection.commit()
#         logging.info(f"Transaction created for PaymentIntent {payment_intent['id']} with status {status}")



# def update_transaction_status(payment_intent_id, new_status):
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             UPDATE transactions
#             SET status = %s, updated_at = CURRENT_TIMESTAMP
#             WHERE id = %s
#         """, (new_status, payment_intent_id))
#         connection.commit()
#         logging.info(f"Transaction {payment_intent_id} updated to status {new_status}")


# def create_user_payment_history(user_id, payment_intent, status):
#     print(payment_intent)
#     initial_event = {
#         "type": "payment_intent.created",
#         "timestamp": payment_intent["created"]
#     }
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             INSERT INTO user_payment_history (user_id, payment_intent_id, status, events, created_at)
#             VALUES (%s, %s, %s, %s::jsonb, CURRENT_TIMESTAMP)
#         """, (
#             user_id,
#             payment_intent['id'],
#             status,
#             json.dumps([initial_event])  # Convert initial event to JSON array
#         ))
#         connection.commit()
#         logging.info(f"User payment history created for PaymentIntent {payment_intent['id']}")


# def update_user_payment_history(payment_intent_id, event_type):
#     new_event = {
#         "type": event_type,
#         "timestamp": "NOW()"  # Assumes Stripe sends a timestamp in the payload; otherwise, you can use datetime.now()
#     }
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             UPDATE user_payment_history
#             SET 
#                 events = events || %s::jsonb,
#                 status = %s,
#                 updated_at = CURRENT_TIMESTAMP
#             WHERE payment_intent_id = %s
#         """, (json.dumps([new_event]), event_type, payment_intent_id))
#         connection.commit()
#         logging.info(f"User payment history for PaymentIntent {payment_intent_id} updated with event {event_type}")


# def update_order_status(order_id, new_status):
#     with connection.cursor() as cursor:
#         cursor.execute("""
#             UPDATE orders
#             SET status = %s, updated_at = CURRENT_TIMESTAMP
#             WHERE id = %s
#         """, (new_status, order_id))
#         connection.commit()
#         logging.info(f"Order {order_id} updated to status {new_status}")


# from datetime import datetime


# def format_address(shipping):
#     """Formatea la dirección de envío en el formato esperado."""
#     line1 = shipping['address'].get('line1', '')
#     line2 = shipping['address'].get('line2', '')
#     state = shipping['address'].get('state', '')
#     city = shipping['address'].get('city', '')
#     postal_code = shipping['address'].get('postal_code', '')

#     # Concatenate parts of the address, omitting line2 if it's empty
#     address = f"{line1}, {line2}, {state}, {city}, {postal_code}"
    
#     return address


# def to_base36(s):
#     """Convierte un string a un número en base 36."""
#     # Convierte cada caracter a su representación ordinal en base 36 y los combina en un solo string
#     return int.from_bytes(s.encode(), 'big')

# def from_base36(num):
#     """Convierte un número en base 36 de vuelta a un string."""
#     # Convierte el número a bytes y luego decodifica a string
#     return num.to_bytes((num.bit_length() + 7) // 8, 'big').decode()

# import hashlib
# def stripe_id_to_int(payment_intent_id):
#     """Genera un número entero único y reversible a partir del ID de payment_intent."""
#     # Generar un hash MD5 (más corto que SHA-256 y adecuado para 10 dígitos)
#     hash_object = hashlib.md5(payment_intent_id.encode())
#     # Convertir el hash en un número entero y truncarlo a los primeros 18 dígitos
#     order_no = int(hash_object.hexdigest(), 16) % 10**18
#     return order_no
# # Ejemplo de uso
# # payment_intent_id = "pi_3QGCMiC070pu0s7s0SxFQjH7"
# # order_no = to_base36(payment_intent_id)
# # print("Número de orden en base 36:", order_no)

# # # Convertir de nuevo al ID original
# # original_payment_intent_id = from_base36(order_no)
# # print("ID de payment_intent recuperado:", original_payment_intent_id)

# from datetime import datetime, timedelta



# def create_order(payment_intent):
#     """Crea una orden por cada producto en `product_ids`."""
    
#     # Obtener el monto total del PaymentIntent y dividir entre 100 para convertir de centavos a dólares
#     total_amount = payment_intent['amount'] / 100
#     user_id = payment_intent['metadata']['user_id']
    
#     # Dividir los product_ids y calcular el monto proporcional para cada producto
#     product_ids = payment_intent['metadata']['product_ids'].split(",")

#     # delivery
#     shipping = payment_intent.get('shipping', {})
#     formatted_delivery_address = format_address(shipping)
#     print(formatted_delivery_address)

#     # Obtener la configuración de comisiones y el umbral de preparación desde app_settings
#     with connection.cursor() as cursor:
#         # Obtener las tarifas de comisión
#         cursor.execute("SELECT order_fees, order_preparation_threshold FROM app_settings LIMIT 1")
#         app_settings = cursor.fetchone()
#         order_fees = app_settings[0]["collection"]
#         preparation_threshold_days = app_settings[1]

#     # Fecha para `preparing_finished_at` sumando el umbral de días
#     preparing_finished_at = datetime.now() + timedelta(days=preparation_threshold_days)

#     order_no = stripe_id_to_int(payment_intent['id'])
#     # Iterar sobre cada producto, obtener el precio y crear una orden
#     for product_id in product_ids:
#         # Obtener el precio final de cada producto desde la tabla `products`
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT final_price FROM products WHERE id = %s", (product_id,))
#             result = cursor.fetchone()
#             if not result:
#                 logging.warning(f"Product ID {product_id} not found in products table.")
#                 continue
            
#             final_price = result[0]

#         # Determinar la comisión aplicable al precio del producto
#         commission_percentage = next(
#             (float(fee["fee"].replace("%", "")) for fee in order_fees 
#              if float(fee["from"]) <= final_price <= float(fee["to"])), 0
#         )
#         commission_fee_str = f"{commission_percentage:.0f}" 
        
#         # commission_amount = (commission_percentage / 100) * final_price
#         # commission_amount
#         # commission_fee_str = f"{commission_amount:.2f}" 
#         # commission_fee_str

#         # Insertar la orden en la tabla `orders`
#         order_no
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 INSERT INTO orders (
#                     id, user_id, product_id, order_no, status, 
#                     delivery_status, track_number, track_number_for_auth, 
#                     preparing_finished_at, address, billing_address, 
#                     shipped_at, delivered_at, delivered_for_auth_at, 
#                     created_at, updated_at, deleted_at, commission_fee, 
#                     warehouse_id, source
#                 ) VALUES (
#                     %s, %s, %s, %s, %s, 
#                     %s, %s, %s, %s, %s, 
#                     %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 
#                     NULL, %s, %s, %s
#                 )
#             """, (
#                 generate_ulid(),                               # id: nuevo ID generado
#                 user_id,                                       # user_id: ID de usuario
#                 product_id,                                    # product_id: ID del producto
#                 order_no,                                      # order_no: número de orden
#                 'PREPARING',                                   # status: estado inicial de la orden
#                 'PENDING',                                     # delivery_status: estado de entrega inicial
#                 None,                                          # track_number: valor inicial nulo
#                 None,                                          # track_number_for_auth: valor inicial nulo
#                 preparing_finished_at,                                          # preparing_finished_at: valor inicial nulo
#                 formatted_delivery_address,                    # address: dirección de envío
#                 formatted_delivery_address,                    # billing_address: dirección de facturación
#                 None,                                          # shipped_at: valor inicial nulo
#                 None,                                          # delivered_at: valor inicial nulo
#                 None,                                          # delivered_for_auth_at: valor inicial nulo
#                 commission_fee_str,                            # comisión en formato cadena
#                 None,                                          # warehouse_id: valor inicial nulo
#                 "WEB"                                          # source: fuente de la orden
#             ))
#             connection.commit()
#             logging.info(f"Order created for product {product_id} with commission fee {commission_fee_str}")

# def create_order(payment_intent):
#     """Inserta un nuevo pedido en la base de datos usando una consulta SQL."""
#     with connection.connect() as conn:
#         query = open("db/create_order.sql").read()
#         conn.execute(query, {
#             'id': payment_intent['id'],
#             'user_id': payment_intent['metadata']['user_id'],
#             'product_id': payment_intent['metadata']['product_ids'],
#             'order_no': 1,
#             'status': 'PREPARING',
#             'address': payment_intent['shipping']['address']['line1'],
#             'billing_address': payment_intent['shipping']['address']['line1'],
#             'source': "WEB",
#             'commission_fee': '{"collection":[{"from":"1","to":"250","fee":"10%"},{"from":"251","to":"500","fee":"20%"}]}'
#         })

# def update_order_status(order_id, new_status):
#     """Actualiza el estado de un pedido usando SQL."""
#     with connection.connect() as conn:
#         query = open("db/update_order_status.sql").read()
#         conn.execute(query, {'id': order_id, 'status': new_status})










# oder    c
# case PREPARING = 'PREPARING';
# case DELIVERY_OVERDUE = 'DELIVERY_OVERDUE';
# case ON_DELIVERY = 'ON_DELIVERY';
# case DELIVERED = 'DELIVERED';
# case ON_AUTH = 'ON_AUTH';
# case ON_DELIVERY_FOR_AUTH = 'ON_DELIVERY_FOR_AUTH';
# case COMPLAINT = 'COMPLAINT';
# case COMPLETED = 'COMPLETED';
# case NEED_TO_REFUND = 'NEED_TO_REFUND';
# case REFUNDED = 'REFUNDED';
# case AUTH_REJECTED = 'AUTH_REJECTED';


# transactions
# case FAILED = 'FAILED';
# case REFUND = 'REFUND';
# case PENDING = 'PENDING';
# case CANCELED = 'CANCELED';
# case SUCCESSFUL = 'SUCCESSFUL';
# case PROCESSING = 'PROCESSING';
# case REQUIRES_ACTION = 'REQUIRES_ACTION';
# case REQUIRES_CONFIRMATION = 'REQUIRES_CONFIRMATION';
# case REQUIRES_PAYMENT_METHOD = 'REQUIRES_PAYMENT_METHOD';



import logging
from flask import Blueprint, request, jsonify
import stripe
from config.config import Config
from dotenv import load_dotenv
from utils.generate_id import generate_ulid
from datetime import datetime, timedelta
import hashlib
import os
import json

# Cargar las variables de entorno directamente en webhook.py como depuración
load_dotenv()
if os.getenv("ENVIRONMENT") == "production":
    print('es con base de datos')
    from db.conection import connection

# Crear un Blueprint para el webhook de Stripe
webhook_bp = Blueprint("webhook", __name__)

# Manejo de Webhook de Stripe
@webhook_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    logging.info("Webhook recibido")
    payload = request.get_data(as_text=True)
    event = request.json

    try:
        logging.info(f"Evento de Stripe: {event['type']}")

        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]
        user_id = payment_intent.get("metadata", {}).get("user_id", "unknown_user")

        # Eventos de pago
        if event["type"] == "payment_intent.created":
            logging.info(f"PaymentIntent creado: {payment_intent['id']}")
            create_transaction(payment_intent, "PENDING")
            create_user_payment_history(user_id, payment_intent, "payment_intent.created")

        elif event["type"] == "payment_intent.requires_action":
            logging.info(f"PaymentIntent requiere acción: {payment_intent['id']}")
            update_transaction_status(payment_intent_id, "REQUIRES_ACTION")
            update_user_payment_history(payment_intent_id, "payment_intent.requires_action")

        elif event["type"] == "payment_intent.processing":
            logging.info(f"PaymentIntent en proceso: {payment_intent['id']}")
            update_transaction_status(payment_intent['id'], "PROCESSING")
            update_user_payment_history(payment_intent_id, "payment_intent.processing")

        elif event["type"] == "payment_intent.succeeded":
            logging.info(f"PaymentIntent exitoso: {payment_intent['id']}")
            update_transaction_status(payment_intent['id'], "SUCCESSFUL")
            create_order(payment_intent)
            update_user_payment_history(payment_intent_id, "payment_intent.succeeded")

        elif event["type"] == "payment_intent.payment_failed":
            logging.info(f"PaymentIntent fallido: {payment_intent['id']}")
            update_transaction_status(payment_intent['id'], "FAILED")
            update_user_payment_history(payment_intent_id, "payment_intent.payment_failed")

        elif event["type"] == "payment_intent.canceled":
            logging.info(f"PaymentIntent cancelado: {payment_intent['id']}")
            update_transaction_status(payment_intent['id'], "CANCELED")
            update_user_payment_history(payment_intent_id, "payment_intent.canceled")

        elif event["type"] == "payment_intent.amount_capturable_updated":
            logging.info(f"PaymentIntent fondos capturables: {payment_intent['id']}")
            update_transaction_status(payment_intent['id'], "REQUIRES_CONFIRMATION")
            update_user_payment_history(payment_intent_id, "payment_intent.amount_capturable_updated")

        # Sesiones de Checkout
        elif event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            logging.info(f"Checkout completado: {session['id']}")
            update_user_payment_history(payment_intent_id, "checkout.session.completed")

        elif event["type"] == "checkout.session.async_payment_succeeded":
            session = event["data"]["object"]
            logging.info(f"Pago asincrónico exitoso: {session['id']}")
            update_transaction_status(session['payment_intent'], "SUCCESSFUL")
            update_user_payment_history(payment_intent_id, "checkout.session.async_payment_succeeded")

        elif event["type"] == "checkout.session.async_payment_failed":
            session = event["data"]["object"]
            logging.info(f"Pago asincrónico fallido: {session['id']}")
            update_transaction_status(session['payment_intent'], "FAILED")
            update_user_payment_history(payment_intent_id, "checkout.session.async_payment_failed")

        elif event["type"] == "checkout.session.expired":
            session = event["data"]["object"]
            logging.info(f"Checkout expirado: {session['id']}")
            update_order_status(session['metadata']['order_id'], "CANCELED")
            update_user_payment_history(payment_intent_id, "checkout.session.expired")

        # Eventos de Clientes
        elif event["type"] == "customer.created":
            customer = event["data"]["object"]
            logging.info(f"Cliente creado: {customer['id']}")
            update_user_payment_history(payment_intent_id, "customer.created")

        elif event["type"] == "customer.deleted":
            customer = event["data"]["object"]
            logging.info(f"Cliente eliminado: {customer['id']}")
            update_user_payment_history(payment_intent_id, "customer.deleted")

        elif event["type"] == "customer.subscription.created":
            subscription = event["data"]["object"]
            logging.info(f"Suscripción creada: {subscription['id']}")
            update_user_payment_history(payment_intent_id, "customer.subscription.created")

        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            logging.info(f"Suscripción cancelada: {subscription['id']}")
            update_user_payment_history(payment_intent_id, "customer.subscription.deleted")

        # Eventos de Facturación
        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            logging.info(f"Pago de factura exitoso: {invoice['id']}")
            update_user_payment_history(payment_intent_id, "invoice.payment_succeeded")

        elif event["type"] == "invoice.payment_failed":
            invoice = event["data"]["object"]
            logging.info(f"Pago de factura fallido: {invoice['id']}")
            update_user_payment_history(payment_intent_id, "invoice.payment_failed")

        # Eventos de Reembolsos
        elif event["type"] == "charge.refunded":
            charge = event["data"]["object"]
            logging.info(f"Reembolso emitido: {charge['id']}")
            update_transaction_status(charge['id'], "REFUND")
            update_order_status(charge, "REFUNDED")
            update_user_payment_history(payment_intent_id, "charge.refunded")

        elif event["type"] == "refund.updated":
            refund = event["data"]["object"]
            logging.info(f"Reembolso actualizado: {refund['id']}")
            update_user_payment_history(payment_intent_id, "refund.updated")

        return jsonify(success=True), 200

    except ValueError:
        logging.error("Payload inválido")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        logging.error("Firma de webhook inválida")
        return jsonify({"error": "Invalid signature"}), 400

def create_transaction(payment_intent, status):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transactions (id, currency_id, amount, type, external_id, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (
                generate_ulid(),
                '01he2qdgggyeg4e05swctvtkvf',
                payment_intent['amount'] / 100,
                "PAYMENT",
                payment_intent['id'],
                status
            ))
            connection.commit()
            logging.info(f"Transaction created for PaymentIntent {payment_intent['id']} with status {status}")
    except Exception as e:
        logging.error(f"Error creating transaction: {e}")
        connection.rollback()

def update_transaction_status(payment_intent_id, new_status):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE transactions
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (new_status, payment_intent_id))
            connection.commit()
            logging.info(f"Transaction {payment_intent_id} updated to status {new_status}")
    except Exception as e:
        logging.error(f"Error updating transaction status for {payment_intent_id}: {e}")
        connection.rollback()

def create_user_payment_history(user_id, payment_intent, status):
    try:
        initial_event = {
            "type": "payment_intent.created",
            "timestamp": payment_intent["created"]
        }
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_payment_history (user_id, payment_intent_id, status, events, created_at)
                VALUES (%s, %s, %s, %s::jsonb, CURRENT_TIMESTAMP)
            """, (
                user_id,
                payment_intent['id'],
                status,
                json.dumps([initial_event])
            ))
            connection.commit()
            logging.info(f"User payment history created for PaymentIntent {payment_intent['id']}")
    except Exception as e:
        logging.error(f"Error creating user payment history: {e}")
        connection.rollback()

def update_user_payment_history(payment_intent_id, event_type):
    try:
        new_event = {
            "type": event_type,
            "timestamp": "NOW()"
        }
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE user_payment_history
                SET events = events || %s::jsonb, status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE payment_intent_id = %s
            """, (json.dumps([new_event]), event_type, payment_intent_id))
            connection.commit()
            logging.info(f"User payment history for PaymentIntent {payment_intent_id} updated with event {event_type}")
    except Exception as e:
        logging.error(f"Error updating user payment history: {e}")
        connection.rollback()

def update_order_status(order_id, new_status):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE orders
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (new_status, order_id))
            connection.commit()
            logging.info(f"Order {order_id} updated to status {new_status}")
    except Exception as e:
        logging.error(f"Error updating order status: {e}")
        connection.rollback()

def format_address(shipping):
    line1 = shipping['address'].get('line1', '')
    line2 = shipping['address'].get('line2', '')
    state = shipping['address'].get('state', '')
    city = shipping['address'].get('city', '')
    postal_code = shipping['address'].get('postal_code', '')
    address = f"{line1}, {line2}, {state}, {city}, {postal_code}"
    return address

def stripe_id_to_int(payment_intent_id):
    hash_object = hashlib.md5(payment_intent_id.encode())
    order_no = int(hash_object.hexdigest(), 16) % 10**18
    return order_no

def create_order(payment_intent):
    total_amount = payment_intent['amount'] / 100
    user_id = payment_intent['metadata']['user_id']
    product_ids = payment_intent['metadata']['product_ids'].split(",")
    shipping = payment_intent.get('shipping', {})
    formatted_delivery_address = format_address(shipping)

    with connection.cursor() as cursor:
        cursor.execute("SELECT order_fees, order_preparation_threshold FROM app_settings LIMIT 1")
        app_settings = cursor.fetchone()
        order_fees = app_settings[0]["collection"]
        preparation_threshold_days = app_settings[1]

    preparing_finished_at = datetime.now() + timedelta(days=preparation_threshold_days)
    order_no = stripe_id_to_int(payment_intent['id'])
    contador=0
    for product_id in product_ids:

        with connection.cursor() as cursor:
            cursor.execute("SELECT final_price FROM products WHERE id = %s", (product_id,))
            result = cursor.fetchone()
            if not result:
                logging.warning(f"Product ID {product_id} not found in products table.")
                continue
            final_price = result[0]
        commission_percentage = next(
            (float(fee["fee"].replace("%", "")) for fee in order_fees if float(fee["from"]) <= final_price <= float(fee["to"])), 0
        )
        commission_fee_str = f"{commission_percentage:.0f}"

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO orders (
                    id, user_id, product_id, order_no, status, 
                    delivery_status, track_number, track_number_for_auth, 
                    preparing_finished_at, address, billing_address, 
                    shipped_at, delivered_at, delivered_for_auth_at, 
                    created_at, updated_at, deleted_at, commission_fee, 
                    warehouse_id, source
                ) VALUES (
                    %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 
                    NULL, %s, %s, %s
                )
            """, (
                generate_ulid(), user_id, product_id, order_no+contador, 'PREPARING', 'PENDING', None, None,
                preparing_finished_at, formatted_delivery_address, formatted_delivery_address,
                None, None, None, commission_fee_str, None, "WEB"
            ))
            connection.commit()
            contador=1+contador
            logging.info(f"Order created for product {product_id} with commission fee {commission_fee_str}")
