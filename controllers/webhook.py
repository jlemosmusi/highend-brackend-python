import logging
from flask import Blueprint, request, jsonify
import stripe
from dotenv import load_dotenv
from utils.generate_id import generate_ulid
from datetime import datetime, timedelta
import hashlib
import os
import json

import os
from dotenv import load_dotenv

load_dotenv()
if os.getenv("ENVIRONMENT") != "local":
    from db.conection import get_connection # Solo importa si no es "local"

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
        # logging.info(f"Eventoe de Stripe: {event['type']}")

        # Eventos de Pago
        if event["type"] == "payment_intent.created":
            # Este evento ocurre cuando se crea un PaymentIntent.
            # Ejemplo: el usuario inicia un proceso de pago, y se crea una intención de pago en estado "PENDING".
            
            # Actualizar el historial del usuario para registrar la creación del PaymentIntent
            
            # Crear transacción en el estado "PENDING"
            # transaction_id = create_transaction(payment_intent, "PENDING")
            # if transaction_id:
                #create_user_payment_history(user_id, payment_intent, "payment_intent.created")    
                logging.info(f"CONFIRMADO PaymentIntent creado: {payment_intent['id']}")

        elif event["type"] == "payment_intent.requires_action":
            # Este evento ocurre cuando un PaymentIntent necesita acción adicional.
            # Ejemplo: el usuario necesita autenticarse o confirmar su pago antes de continuar.
            
            # Actualizar historial de pago y cambiar el estado de la transacción a "REQUIRES_ACTION"
            #update_user_payment_history(payment_intent_id, "payment_intent.requires_action")
            #update_transaction_status(payment_intent_id, "REQUIRES_ACTION")
            
            logging.info(f"CONFIRMADO PaymentIntent requiere acción: {payment_intent['id']}")

        elif event["type"] == "payment_intent.processing":
            # Este evento indica que el pago está en proceso.
            # Ejemplo: el sistema está validando o procesando los detalles de pago del usuario.
            
            # Actualizar historial y estado de la transacción a "PROCESSING"
            #update_user_payment_history(payment_intent_id, "payment_intent.processing")
            #update_transaction_status(payment_intent['id'], "PROCESSING")
            
            logging.info(f"CONFIRMADO PaymentIntent en proceso: {payment_intent['id']}")

        elif event["type"] == "payment_intent.succeeded":
            # Este evento se dispara cuando el pago es exitoso.
            # Ejemplo: el pago del usuario se completa correctamente, y el sistema confirma el cobro.
            
            # Lógica adicional para procesar el pago exitoso
            # handle_payment_intent_succeeded(payment_intent)
            
            logging.info(f"CONFIRMADO PaymentIntent exitoso: {payment_intent['id']}")

        elif event["type"] == "payment_intent.payment_failed":
            # Este evento ocurre cuando falla un PaymentIntent.
            # Ejemplo: el pago del usuario no se puede procesar debido a fondos insuficientes o error de tarjeta.
            
            # Actualizar historial y estado a "FAILED"
            #update_user_payment_history(payment_intent_id, "payment_intent.payment_failed")
            #update_transaction_status(payment_intent['id'], "FAILED")
            
            logging.info(f"CONFIRMADO PaymentIntent fallido: {payment_intent['id']}")

        elif event["type"] == "payment_intent.canceled":
            # Este evento ocurre cuando se cancela un PaymentIntent.
            # Ejemplo: el usuario decide no completar la compra y el pago se cancela.
            
            # Actualizar historial y estado a "CANCELED"
            #update_user_payment_history(payment_intent_id, "payment_intent.canceled")
            #update_transaction_status(payment_intent['id'], "CANCELED")
            
            logging.info(f"CONFIRMADO PaymentIntent cancelado: {payment_intent['id']}")

        elif event["type"] == "payment_intent.amount_capturable_updated":
            # Este evento indica que el monto capturable se actualizó, y requiere confirmación.
            # Ejemplo: el sistema ajusta la cantidad que se puede capturar en el pago, esperando la confirmación final.
            
            # Actualizar historial y estado a "REQUIRES_CONFIRMATION"
            #update_user_payment_history(payment_intent_id, "payment_intent.amount_capturable_updated")
            #update_transaction_status(payment_intent['id'], "REQUIRES_CONFIRMATION")
            
            logging.info(f"CONFIRMADO PaymentIntent fondos capturables: {payment_intent['id']}")

        # Eventos de Sesiones de Checkout
        elif event["type"] == "checkout.session.completed":
            # Este evento se activa cuando una sesión de checkout se completa.
            # Ejemplo: el usuario ha completado su compra y el pago fue procesado correctamente.
            
            # Actualizar historial del usuario
            #update_user_payment_history(payment_intent_id, "checkout.session.completed")
            
            logging.info(f"CONFIRMADO Checkout completado: {payment_intent['id']}")

        elif event["type"] == "checkout.session.async_payment_succeeded":
            # Este evento ocurre cuando un pago asincrónico de checkout se completa exitosamente.
            # Ejemplo: el sistema procesa un pago que toma más tiempo en completarse, como una transferencia.
            
            # Actualizar historial y estado de transacción a "SUCCESSFUL"
            #update_user_payment_history(payment_intent_id, "checkout.session.async_payment_succeeded")
            #update_transaction_status(payment_intent['id'], "SUCCESSFUL")
            
            logging.info(f"CONFIRMADO Pago asincrónico exitoso: {payment_intent['id']}")

        elif event["type"] == "checkout.session.async_payment_failed":
            # Este evento ocurre cuando un pago asincrónico de checkout falla.
            # Ejemplo: el sistema intenta procesar un pago pero falla después de varios intentos.
            
            # Actualizar historial y estado de transacción a "FAILED"
            #update_user_payment_history(payment_intent_id, "checkout.session.async_payment_failed")
            #update_transaction_status(payment_intent['id'], "FAILED")
            
            logging.info(f"CONFIRMADO Pago asincrónico fallido: {payment_intent['id']}")

        elif event["type"] == "checkout.session.expired":
            # Este evento ocurre cuando una sesión de checkout expira.
            # Ejemplo: el usuario tarda demasiado en completar la compra, y la sesión expira automáticamente.
            
            # Actualizar historial y estado de orden a "CANCELED"
            #update_user_payment_history(payment_intent_id, "checkout.session.expired")
            #update_transaction_status(payment_intent['id'], "CANCELED")
            
            logging.info(f"CONFIRMADO Checkout expirado: {payment_intent['id']}")

        # Eventos de Clientes
        elif event["type"] == "customer.created":
            # Este evento se dispara cuando se crea un nuevo cliente en Stripe.
            # Ejemplo: el usuario se registra en el sistema y crea un cliente en la cuenta de Stripe.
            
            # Actualizar historial del usuario
            #update_user_payment_history(payment_intent_id, "customer.created")
            # customer = event["data"]["object"]
            
            logging.info(f"CONFIRMADO Cliente creado: {payment_intent['id']}")

        elif event["type"] == "customer.deleted":
            # Este evento ocurre cuando se elimina un cliente.
            # Ejemplo: el usuario decide eliminar su cuenta, y el cliente se borra de Stripe.
            
            # Actualizar historial del usuario
            #update_user_payment_history(payment_intent_id, "customer.deleted")
            # customer = event["data"]["object"]
            
            logging.info(f"CONFIRMADO Cliente eliminado: {payment_intent['id']}")

        elif event["type"] == "customer.subscription.created":
            # Este evento ocurre cuando se crea una nueva suscripción para un cliente.
            # Ejemplo: el usuario se suscribe a un plan de servicio o suscripción en la plataforma.
            
            # Actualizar historial de suscripción
            #update_user_payment_history(payment_intent_id, "customer.subscription.created")
            # subscription = event["data"]["object"]
            
            logging.info(f"CONFIRMADO Suscripción creada: {payment_intent['id']}")

        elif event["type"] == "customer.subscription.deleted":
            # Este evento ocurre cuando se cancela una suscripción.
            # Ejemplo: el usuario cancela su suscripción a un servicio.
            
            # Actualizar historial de suscripción
            #update_user_payment_history(payment_intent_id, "customer.subscription.deleted")
            # subscription = event["data"]["object"]
            
            logging.info(f"CONFIRMADO Suscripción cancelada: {payment_intent['id']}")

        # Eventos de Facturación
        elif event["type"] == "invoice.payment_succeeded":
            # Este evento se activa cuando se completa un pago de factura.
            # Ejemplo: el usuario paga su factura, y el pago se confirma.
            
            # Actualizar historial del pago
            #update_user_payment_history(payment_intent_id, "invoice.payment_succeeded")
            # invoice = event["data"]["object"]
            
            logging.info(f"CONFIRMADO Pago de factura exitoso: {payment_intent['id']}")

        elif event["type"] == "invoice.payment_failed":
            # Este evento se activa cuando falla el pago de una factura.
            # Ejemplo: el pago de la factura no se procesa, posiblemente debido a fondos insuficientes.
            
            # Actualizar historial del pago
            #update_user_payment_history(payment_intent_id, "invoice.payment_failed")
            # invoice = event["data"]["object"]
            
            logging.info(f"CONFIRMADO Pago de factura fallido: {payment_intent['id']}")

        # Eventos de Reembolsos
        elif event["type"] == "charge.refunded":
            # Este evento ocurre cuando se emite un reembolso para un cargo.
            # Ejemplo: el usuario solicita un reembolso, y el sistema devuelve el monto.
            
            # Actualizar historial y estado a "REFUND"
            #update_user_payment_history(payment_intent_id, "charge.refunded")
            # charge = event["data"]["object"]
            #update_transaction_status(charge['id'], "REFUND")
            # update_order_status(charge, "REFUNDED")
            
            logging.info(f"CONFIRMADO Reembolso emitido: {payment_intent['id']}")

        elif event["type"] == "refund.updated":
            # Este evento ocurre cuando un reembolso es actualizado.
            # Ejemplo: el reembolso cambia de estado en Stripe, y se refleja en el sistema.
            
            # Actualizar historial del reembolso
            #update_user_payment_history(payment_intent_id, "refund.updated")
            # refund = event["data"]["object"]
            logging.info(f"CONFIRMADO Reembolso actualizado: {payment_intent['id']}")


        return jsonify(success=True), 200

    except ValueError:
        logging.error("Payload inválido")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        logging.error("Firma de webhook inválida")
        return jsonify({"error": "Invalid signature"}), 400

def create_transaction(payment_intent, status):
    try:
        connection=get_connection()

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
        connection=get_connection()

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
        connection=get_connection()
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
        connection=get_connection()

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
        connection=get_connection()

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
        connection=get_connection()

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

    connection=get_connection()

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

