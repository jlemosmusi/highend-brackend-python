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
if os.getenv("ENVIRONMENT") != "local":
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
        logging.info(f"Evento de Stripe: {event['type']}")

        # Eventos de Pago
        if event["type"] == "payment_intent.created":
            # Este evento ocurre cuando se crea un PaymentIntent.
            # Ejemplo: el usuario inicia un proceso de pago, y se crea una intención de pago en estado "PENDING".
            
            # Actualizar el historial del usuario para registrar la creación del PaymentIntent
            
            # Crear transacción en el estado "PENDING"
            transaction_id = create_transaction(payment_intent, "PENDING")
            if transaction_id:
                create_user_payment_history(user_id, payment_intent, "payment_intent.created")    
                logging.info(f"PaymentIntent creado: {payment_intent['id']}")

        elif event["type"] == "payment_intent.requires_action":
            # Este evento ocurre cuando un PaymentIntent necesita acción adicional.
            # Ejemplo: el usuario necesita autenticarse o confirmar su pago antes de continuar.
            
            # Actualizar historial de pago y cambiar el estado de la transacción a "REQUIRES_ACTION"
            update_user_payment_history(payment_intent_id, "payment_intent.requires_action")
            update_transaction_status(payment_intent_id, "REQUIRES_ACTION")
            
            logging.info(f"PaymentIntent requiere acción: {payment_intent['id']}")

        elif event["type"] == "payment_intent.processing    ":
            # Este evento indica que el pago está en proceso.
            # Ejemplo: el sistema está validando o procesando los detalles de pago del usuario.
            
            # Actualizar historial y estado de la transacción a "PROCESSING"
            update_user_payment_history(payment_intent_id, "payment_intent.processing")
            update_transaction_status(payment_intent['id'], "PROCESSING")
            
            logging.info(f"PaymentIntent en proceso: {payment_intent['id']}")

        elif event["type"] == "payment_intent.succeeded":
            # Este evento se dispara cuando el pago es exitoso.
            # Ejemplo: el pago del usuario se completa correctamente, y el sistema confirma el cobro.
            
            # Lógica adicional para procesar el pago exitoso
            handle_payment_intent_succeeded(payment_intent)
            
            logging.info(f"PaymentIntent exitoso: {payment_intent['id']}")

        elif event["type"] == "payment_intent.payment_failed":
            # Este evento ocurre cuando falla un PaymentIntent.
            # Ejemplo: el pago del usuario no se puede procesar debido a fondos insuficientes o error de tarjeta.
            
            # Actualizar historial y estado a "FAILED"
            update_user_payment_history(payment_intent_id, "payment_intent.payment_failed")
            update_transaction_status(payment_intent['id'], "FAILED")
            
            logging.info(f"PaymentIntent fallido: {payment_intent['id']}")

        elif event["type"] == "payment_intent.canceled":
            # Este evento ocurre cuando se cancela un PaymentIntent.
            # Ejemplo: el usuario decide no completar la compra y el pago se cancela.
            
            # Actualizar historial y estado a "CANCELED"
            update_user_payment_history(payment_intent_id, "payment_intent.canceled")
            update_transaction_status(payment_intent['id'], "CANCELED")
            
            logging.info(f"PaymentIntent cancelado: {payment_intent['id']}")

        elif event["type"] == "payment_intent.amount_capturable_updated":
            # Este evento indica que el monto capturable se actualizó, y requiere confirmación.
            # Ejemplo: el sistema ajusta la cantidad que se puede capturar en el pago, esperando la confirmación final.
            
            # Actualizar historial y estado a "REQUIRES_CONFIRMATION"
            update_user_payment_history(payment_intent_id, "payment_intent.amount_capturable_updated")
            update_transaction_status(payment_intent['id'], "REQUIRES_CONFIRMATION")
            
            logging.info(f"PaymentIntent fondos capturables: {payment_intent['id']}")

        # Eventos de Sesiones de Checkout
        elif event["type"] == "checkout.session.completed":
            # Este evento se activa cuando una sesión de checkout se completa.
            # Ejemplo: el usuario ha completado su compra y el pago fue procesado correctamente.
            
            # Actualizar historial del usuario
            update_user_payment_history(payment_intent_id, "checkout.session.completed")
            
            logging.info(f"Checkout completado: {session['id']}")

        elif event["type"] == "checkout.session.async_payment_succeeded":
            # Este evento ocurre cuando un pago asincrónico de checkout se completa exitosamente.
            # Ejemplo: el sistema procesa un pago que toma más tiempo en completarse, como una transferencia.
            
            # Actualizar historial y estado de transacción a "SUCCESSFUL"
            update_user_payment_history(payment_intent_id, "checkout.session.async_payment_succeeded")
            update_transaction_status(payment_intent['id'], "SUCCESSFUL")
            
            logging.info(f"Pago asincrónico exitoso: {payment_intent['id']}")

        elif event["type"] == "checkout.session.async_payment_failed":
            # Este evento ocurre cuando un pago asincrónico de checkout falla.
            # Ejemplo: el sistema intenta procesar un pago pero falla después de varios intentos.
            
            # Actualizar historial y estado de transacción a "FAILED"
            update_user_payment_history(payment_intent_id, "checkout.session.async_payment_failed")
            update_transaction_status(payment_intent['id'], "FAILED")
            
            logging.info(f"Pago asincrónico fallido: {payment_intent['id']}")

        elif event["type"] == "checkout.session.expired":
            # Este evento ocurre cuando una sesión de checkout expira.
            # Ejemplo: el usuario tarda demasiado en completar la compra, y la sesión expira automáticamente.
            
            # Actualizar historial y estado de orden a "CANCELED"
            update_user_payment_history(payment_intent_id, "checkout.session.expired")
            update_transaction_status(payment_intent['id'], "CANCELED")
            
            logging.info(f"Checkout expirado: {payment_intent['id']}")

        # Eventos de Clientes
        elif event["type"] == "customer.created":
            # Este evento se dispara cuando se crea un nuevo cliente en Stripe.
            # Ejemplo: el usuario se registra en el sistema y crea un cliente en la cuenta de Stripe.
            
            # Actualizar historial del usuario
            update_user_payment_history(payment_intent_id, "customer.created")
            customer = event["data"]["object"]
            
            logging.info(f"Cliente creado: {customer['id']}")

        elif event["type"] == "customer.deleted":
            # Este evento ocurre cuando se elimina un cliente.
            # Ejemplo: el usuario decide eliminar su cuenta, y el cliente se borra de Stripe.
            
            # Actualizar historial del usuario
            update_user_payment_history(payment_intent_id, "customer.deleted")
            customer = event["data"]["object"]
            
            logging.info(f"Cliente eliminado: {customer['id']}")

        elif event["type"] == "customer.subscription.created":
            # Este evento ocurre cuando se crea una nueva suscripción para un cliente.
            # Ejemplo: el usuario se suscribe a un plan de servicio o suscripción en la plataforma.
            
            # Actualizar historial de suscripción
            update_user_payment_history(payment_intent_id, "customer.subscription.created")
            subscription = event["data"]["object"]
            
            logging.info(f"Suscripción creada: {subscription['id']}")

        elif event["type"] == "customer.subscription.deleted":
            # Este evento ocurre cuando se cancela una suscripción.
            # Ejemplo: el usuario cancela su suscripción a un servicio.
            
            # Actualizar historial de suscripción
            update_user_payment_history(payment_intent_id, "customer.subscription.deleted")
            subscription = event["data"]["object"]
            
            logging.info(f"Suscripción cancelada: {subscription['id']}")

        # Eventos de Facturación
        elif event["type"] == "invoice.payment_succeeded":
            # Este evento se activa cuando se completa un pago de factura.
            # Ejemplo: el usuario paga su factura, y el pago se confirma.
            
            # Actualizar historial del pago
            update_user_payment_history(payment_intent_id, "invoice.payment_succeeded")
            invoice = event["data"]["object"]
            
            logging.info(f"Pago de factura exitoso: {invoice['id']}")

        elif event["type"] == "invoice.payment_failed":
            # Este evento se activa cuando falla el pago de una factura.
            # Ejemplo: el pago de la factura no se procesa, posiblemente debido a fondos insuficientes.
            
            # Actualizar historial del pago
            update_user_payment_history(payment_intent_id, "invoice.payment_failed")
            invoice = event["data"]["object"]
            
            logging.info(f"Pago de factura fallido: {invoice['id']}")

        # Eventos de Reembolsos
        elif event["type"] == "charge.refunded":
            # Este evento ocurre cuando se emite un reembolso para un cargo.
            # Ejemplo: el usuario solicita un reembolso, y el sistema devuelve el monto.
            
            # Actualizar historial y estado a "REFUND"
            update_user_payment_history(payment_intent_id, "charge.refunded")
            charge = event["data"]["object"]
            update_transaction_status(charge['id'], "REFUND")
            update_order_status(charge, "REFUNDED")
            
            logging.info(f"Reembolso emitido: {charge['id']}")

        elif event["type"] == "refund.updated":
            # Este evento ocurre cuando un reembolso es actualizado.
            # Ejemplo: el reembolso cambia de estado en Stripe, y se refleja en el sistema.
            
            # Actualizar historial del reembolso
            update_user_payment_history(payment_intent_id, "refund.updated")
            refund = event["data"]["object"]
            logging.info(f"Reembolso actualizado: {refund['id']}")


        return jsonify(success=True), 200

    except ValueError:
        logging.error("Payload inválido")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        logging.error("Firma de webhook inválida")
        return jsonify({"error": "Invalid signature"}), 400

def create_transaction(payment_intent, status):
    try:
        # Primero verifica si el external_id ya existe en la base de datos
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM transactions WHERE external_id = %s
            """, (payment_intent['id'],))
            existing_transaction = cursor.fetchone()
            
            # Si la transacción ya existe, registra un log y no inserta nada
            if existing_transaction:
                logging.info(f"Transaction with PaymentIntent {payment_intent['id']} already exists with ID {existing_transaction[0]}")
                # return existing_transaction[0]
                return None
            
            # Si no existe, procede con la inserción
            cursor.execute("""
                INSERT INTO transactions (id, currency_id, amount, type, external_id, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id
            """, (
                generate_ulid(),
                '01he2qdgggyeg4e05swctvtkvf',
                payment_intent['amount'] / 100,
                "PAYMENT",
                payment_intent['id'],
                status
            ))
            transaction_id = cursor.fetchone()[0]
            connection.commit()
            logging.info(f"Transaction created for PaymentIntent {payment_intent['id']} with status {status}")
            return transaction_id
    except Exception as e:
        logging.error(f"Error creating transaction: {e}")
        connection.rollback()



def create_relation_order_transaction(order_id, transaction_id):
    """
    Inserta una relación entre order_id y transaction_id en la tabla order_transactions.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO order_transactions (id, order_id, transaction_id)
                VALUES (%s, %s, %s)
            """, (
                generate_ulid(),
                order_id,
                transaction_id
            ))
            connection.commit()
            logging.info(f"Relation created between order {order_id} and transaction {transaction_id}")
    except Exception as e:
        logging.error(f"Error creating relation between order and transaction: {e}")
        connection.rollback()

def update_transaction_status(payment_intent_id, new_status):
    """
    Actualiza el estado de una transacción y devuelve su ID para futuras referencias.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE transactions
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE external_id = %s
                RETURNING id
            """, (new_status, payment_intent_id))
            transaction_id = cursor.fetchone()[0]
            connection.commit()
            logging.info(f"Transaction {payment_intent_id} updated to status {new_status}")
            return transaction_id
    except Exception as e:
        logging.error(f"Error updating transaction status for {payment_intent_id}: {e}")
        connection.rollback()
        return None

def create_user_payment_history(user_id, payment_intent, status):
    try:
        user_id = payment_intent.get("metadata", {}).get("user_id", "unknown_user")
        products = payment_intent.get("metadata", {}).get("product_ids", "unknown_products")

        initial_event = {
            "type": "payment_intent.created",
            "timestamp": payment_intent["created"],
            "products":products
        }
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM user_payment_history WHERE payment_intent_id = %s
            """, (payment_intent['id'],))
            existing_payment_history = cursor.fetchone()
            
            # Si la transacción ya existe, registra un log y no inserta nada
            if existing_payment_history:
                logging.info(f"existing_payment_history with PaymentIntent {payment_intent['id']}")
                # return existing_transaction[0]
                return None
            
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

import time

def update_user_payment_history(payment_intent_id, event_type):
    try:
        new_event = {
            "type": event_type,
            "timestamp": int(time.time())
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
    """
    Crea una o más órdenes basadas en un payment_intent y devuelve los order_id generados.
    """
    total_amount = payment_intent['amount'] / 100
    user_id = payment_intent['metadata']['user_id']
    product_ids = payment_intent['metadata']['product_ids'].split(",")
    shipping = payment_intent.get('shipping', {})
    formatted_delivery_address = format_address(shipping)

    # Obtener configuración de comisiones y umbral de preparación
    with connection.cursor() as cursor:
        cursor.execute("SELECT order_fees, order_preparation_threshold FROM app_settings LIMIT 1")
        app_settings = cursor.fetchone()
        order_fees = app_settings[0]["collection"]
        preparation_threshold_days = app_settings[1]

    preparing_finished_at = datetime.now() + timedelta(days=preparation_threshold_days)
    order_no = stripe_id_to_int(payment_intent['id'])
    order_ids = []

    for index, product_id in enumerate(product_ids):
        with connection.cursor() as cursor:
            
            # Verificar si ya existe una orden para el producto
            cursor.execute("SELECT id FROM orders WHERE product_id = %s", (product_id,))
            existing_order = cursor.fetchone()
            if existing_order:
                logging.info(f"Order already exists for product ID {product_id} with order ID {existing_order[0]}")
                continue  # Si ya existe, omitir y pasar al siguiente producto
            
            cursor.execute("SELECT final_price FROM products WHERE id = %s", (product_id,))
            result = cursor.fetchone()
            if not result:
                logging.warning(f"Product ID {product_id} not found in products table.")
                continue
            final_price = result[0]

        # Calcular comisión aplicable
        commission_percentage = next(
            (float(fee["fee"].replace("%", "")) for fee in order_fees if float(fee["from"]) <= final_price <= float(fee["to"])), 0
        )
        commission_fee_str = f"{commission_percentage:.0f}"

        # Crear la orden y obtener el ID
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
                RETURNING id
            """, (
                generate_ulid(), user_id, product_id, order_no + index, 'PREPARING', 'PENDING', None, None,
                preparing_finished_at, formatted_delivery_address, formatted_delivery_address,
                None, None, None, commission_fee_str, None, "WEB"
            ))
            order_id = cursor.fetchone()[0]
            connection.commit()
            order_ids.append(order_id)
            logging.info(f"Order created for product {product_id} with commission fee {commission_fee_str}")
    
    return order_ids



# Ejemplo de cómo integrarlos en la lógica de webhook
def handle_payment_intent_succeeded(payment_intent):
    logging.info(f"PaymentIntent exitoso: {payment_intent['id']} guardando proceso en base de datos..")
    # Actualizar historial de pagos del usuario
    update_user_payment_history(payment_intent['id'], "payment_intent.succeeded")


    # Actualizar el estado de la transacción y obtener el ID de la transacción
    transaction_id = update_transaction_status(payment_intent['id'], "SUCCESSFUL")
    if not transaction_id:
        logging.error("Failed to update transaction status.")
        return

    # Crear órdenes y obtener los IDs de las órdenes creadas
    order_ids = create_order(payment_intent)
    if not order_ids:
        logging.error("Failed to create orders.")
        return

    # Crear relaciones entre las órdenes y la transacción
    for order_id in order_ids:
        create_relation_order_transaction(order_id, transaction_id)

