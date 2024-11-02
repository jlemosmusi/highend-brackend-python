from flask import Blueprint, jsonify, request
import stripe
import logging
import os
from config.config import Config
if os.getenv("ENVIRONMENT") == "production":
    from utils.auth import sanctum_auth_required
    from db.conection import connection  # Adjusted to your `connection` path

from controllers.webhook import create_transaction,create_user_payment_history

# Configuración de Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Crear un blueprint para el PaymentIntent
payment_intent_bp = Blueprint("payment_intent", __name__)

# Conditionally apply the decorator if in development
if os.getenv("ENVIRONMENT") == "production":
    @payment_intent_bp.route("/create-payment-intent", methods=["POST"])
    @sanctum_auth_required
    def create_payment_intent(user_id=None):
        return process_payment_intent(user_id)
else:
    @payment_intent_bp.route("/create-payment-intent", methods=["POST"])
    def create_payment_intent():
        return process_payment_intent()
    

def process_payment_intent(user_id=None):
    try:
        data = request.json
        amount = data.get("amount")
        products = data.get("products")

        if amount is None:
            logging.error("No amount provided")
            return jsonify({"error": "No amount provided"}), 400
        
        if os.getenv("ENVIRONMENT") == "production":
            print('busco en base de datos user_id:: '+ user_id)
        # Consulta a la base de datos para obtener la dirección del usuario
            cursor = connection.cursor()
            cursor.execute("""
                SELECT name, surname, phone, state, suburb, address_1, address_2, zip 
                FROM addresses 
                WHERE user_id = %s
            """, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            name, surname, phone, state, suburb, address_1, address_2, zipCode = result

            if not result:
                logging.error("User address not found")
                return jsonify({"error": "User address not found"}), 404
    
        else:
            # Datos de usuario ficticios o reemplazar por datos reales
            name, surname, phone = "Test", "User", "123456789"
            address_1, address_2, suburb, state, zipCode = "123 Test St", "Apt 4B", "Test City", "NSW", "2000"
            user_id='01j7jt0v75gxhdp7ff3ana3jrw'

        # Crear el PaymentIntent en Stripe
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Monto en centavos
            currency="aud",
            payment_method_types=["afterpay_clearpay"],
            shipping={
                'name': f"{name} {surname}",
                'phone': phone,
                'address': {
                    'line1': address_1,
                    'line2': address_2 or "",  # Opcional
                    'city': suburb,
                    'state': state,
                    'postal_code': zipCode,
                    'country': 'AU'
                },
            },
            metadata={
                'user_id': user_id,
                'product_ids': ','.join([product["id"] for product in products])
            }
        )
        print(intent)

        logging.info(f"PaymentIntent creado: {intent['id']}")
        create_transaction(intent,"PENDING")
        create_user_payment_history(user_id,intent,"PENDING")
        return jsonify({"clientSecret": intent["client_secret"]})

    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {e}")
        return jsonify(error=str(e)), 403
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify(error=str(e)), 403

