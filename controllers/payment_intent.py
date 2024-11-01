# from flask import Blueprint, jsonify, request
# import stripe
# import logging
# from utils.auth import sanctum_auth_required

# # Crear un blueprint para el PaymentIntent
# payment_intent_bp = Blueprint("payment_intent", __name__)

# # Ruta para crear un PaymentIntent
# @payment_intent_bp.route("/create-payment-intent", methods=["POST"])
# @sanctum_auth_required
# def create_payment_intent(user_id):
#     try:
#         data = request.json
#         amount = data.get("amount")
#         products = data.get("products")

#         # Validar que el monto esté presente
#         if amount is None:
#             logging.error("No amount provided")
#             return jsonify({"error": "No amount provided"}), 400

#         # Consulta a la base de datos para obtener la dirección del usuario
#         # cursor = connection.cursor()
#         # cursor.execute("""
#         #     SELECT name, surname, phone, state, suburb, address_1, address_2, zip 
#         #     FROM addresses 
#         #     WHERE user_id = %s
#         # """, (user_id,))
#         # result = cursor.fetchone()
#         # cursor.close()

#         # if not result:
#         #     logging.error("User address not found")
#         #     return jsonify({"error": "User address not found"}), 404

#         # # Asignar variables con datos de la dirección
#         # name, surname, phone, state, suburb, address_1, address_2, zipCode = result

#         # Datos ficticios para pruebas
#         name, surname, phone = "Test", "User", "123456789"
#         address_1, address_2, suburb, state, zipCode = "123 Test St", "Apt 4B", "Test City", "NSW", "2000"


#         # Crear el PaymentIntent
#         intent = stripe.PaymentIntent.create(
#             amount=int(amount * 100),  # Monto en centavos
#             currency="aud",
#             payment_method_types=["afterpay_clearpay"],
#             shipping={
#                 'name': f"{name} {surname}",
#                 'phone': phone,
#                 'address': {
#                     'line1': address_1,
#                     'line2': address_2 or "",  # Opcional
#                     'city': suburb,
#                     'state': state,
#                     'postal_code': zipCode,
#                     'country': 'AU'
#                 },
#             },
#             metadata={
#                 'user_id': user_id,
#                 'product_ids': ','.join([product["id"] for product in products])
#             }
#         )

#         logging.info(f"PaymentIntent creado: {intent['id']}")
#         return jsonify({"clientSecret": intent["client_secret"]})

#     except stripe.error.StripeError as e:
#         logging.error(f"Stripe error: {e}")
#         return jsonify(error=str(e)), 403
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")
#         return jsonify(error=str(e)), 403

from flask import Blueprint, jsonify, request
import stripe
import logging
from utils.auth import sanctum_auth_required
from config.config import Config

# Configuración de Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Crear un blueprint para el PaymentIntent
payment_intent_bp = Blueprint("payment_intent", __name__)

@payment_intent_bp.route("/create-payment-intent", methods=["POST"])
# @sanctum_auth_required
def create_payment_intent(user_id= None):
    try:
        # print('asd')
        data = request.json
        amount = data.get("amount")
        products = data.get("products")

        if amount is None:
            logging.error("No amount provided")
            return jsonify({"error": "No amount provided"}), 400

        # Consulta a la base de datos para obtener la dirección del usuario
        #         # cursor = connection.cursor()
        #         # cursor.execute("""
        #         #     SELECT name, surname, phone, state, suburb, address_1, address_2, zip 
        #         #     FROM addresses 
        #         #     WHERE user_id = %s
        #         # """, (user_id,))
        #         # result = cursor.fetchone()
        #         # cursor.close()

        #         # if not result:
        #         #     logging.error("User address not found")
        #         #     return jsonify({"error": "User address not found"}), 404
        
        
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

        logging.info(f"PaymentIntent creado: {intent['id']}")
        return jsonify({"clientSecret": intent["client_secret"]})

    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {e}")
        return jsonify(error=str(e)), 403
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify(error=str(e)), 403

