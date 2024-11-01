import logging
from flask import Blueprint, request, jsonify
import stripe
from config.config import Config
# from db.conection import engine
# from db.conection import connection
import os
if os.getenv("ENVIRONMENT") == "production":
    from db.conection import connection

# Crear un Blueprint para el webhook de Stripe
webhook_bp = Blueprint("webhook", __name__)

# Manejo de Webhook de Stripe
@webhook_bp.route("/webhook", methods=["POST"])
def stripe_webhook():
    logging.info("Webhook recibido")
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, Config.WEBHOOK_SECRET)
        logging.info(f"Evento de Stripe: {event['type']}")

        # Lógica para manejar cada evento de Stripe
        if event["type"] == "payment_intent.created":
            payment_intent = event["data"]["object"]
            logging.info(f"PaymentIntent creado: {payment_intent['id']}")
            # create_order(payment_intent)

        elif event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            logging.info(f"PaymentIntent exitoso: {payment_intent['id']}")
            # update_order_status(payment_intent['id'], "Paid")

        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            logging.info(f"PaymentIntent fallido: {payment_intent['id']}")
            # update_order_status(payment_intent['id'], "Failed")

        elif event["type"] == "payment_intent.requires_action":
            payment_intent = event["data"]["object"]
            logging.info(f"PaymentIntent requiere acción: {payment_intent['id']}")
            # update_order_status(payment_intent['id'], "Requires Action")

        elif event["type"] == "payment_intent.processing":
            payment_intent = event["data"]["object"]
            logging.info(f"PaymentIntent en proceso: {payment_intent['id']}")
            # update_order_status(payment_intent['id'], "Processing")

        elif event["type"] == "payment_intent.canceled":
            payment_intent = event["data"]["object"]
            logging.info(f"PaymentIntent cancelado: {payment_intent['id']}")
            # update_order_status(payment_intent['id'], "Canceled")

        elif event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            logging.info(f"Checkout completado: {session['id']}")
            # update_order_status(session['id'], "Completed")

        elif event["type"] == "checkout.session.expired":
            session = event["data"]["object"]
            logging.info(f"Checkout expirado: {session['id']}")
            # update_order_status(session['id'], "Expired")

        
        # Eventos adicionales para seguimiento
        elif event["type"] == "customer.created":
            logging.info(f"Cliente creado en Stripe: {event['data']['object']['id']}")

        elif event["type"] == "customer.deleted":
            logging.info(f"Cliente eliminado en Stripe: {event['data']['object']['id']}")

        elif event["type"] == "invoice.payment_succeeded":
            logging.info(f"Pago de factura exitoso: {event['data']['object']['id']}")

        elif event["type"] == "invoice.payment_failed":
            logging.info(f"Pago de factura fallido: {event['data']['object']['id']}")

        elif event["type"] == "invoice.finalized":
            logging.info(f"Factura finalizada: {event['data']['object']['id']}")

        elif event["type"] == "customer.subscription.created":
            subscription = event["data"]["object"]
            logging.info(f"Suscripción creada: {subscription['id']}")
            # Aquí podrías manejar registros específicos de suscripciones si fuera necesario

        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            logging.info(f"Suscripción cancelada: {subscription['id']}")
            # Actualizar el estado a 'Subscription Cancelled'
            # Descomentar para producción
            # update_order_status(subscription['id'], "Subscription Cancelled")

        return jsonify(success=True), 200

    except ValueError:
        logging.error("Payload inválido")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        logging.error("Firma de webhook inválida")
        return jsonify({"error": "Invalid signature"}), 400

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