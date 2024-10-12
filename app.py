import stripe
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os

app = Flask(__name__)
CORS(app)

# Configurar logging para ver todos los eventos en la consola
logging.basicConfig(level=logging.INFO)

# Clave secreta de Stripe (usa tu clave de prueba)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_51Q8dwTC070pu0s7sHBWMvS648iOWCsJNkSFdZXVLzW1LHDlEFWCuBCw7rkmucyNf9ZJUaqIoSp0oZc86FZmP4vRG00hMzigEDo')

# Endpoint para crear PaymentIntent
@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    try:
        # Obtenemos el monto desde el frontend
        data = request.json
        logging.info(f'Datos recibidos: {data}')
        amount = data.get('amount', None)

        # Verificamos que el monto no esté vacío
        if amount is None:
            logging.error('No amount provided')
            return jsonify({"error": "No amount provided"}), 400

        # Creamos el PaymentIntent con Afterpay como método de pago y la dirección hardcodeada
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # El monto debe estar en centavos
            currency='aud',  # Afterpay soporta AUD
            payment_method_types=['afterpay_clearpay'],  # Afterpay
            shipping={
                'name': 'John Doe',  # Nombre fijo (hardcoded)
                'address': {
                    'line1': '123 Main St',  # Dirección fija
                    'line2': 'Apt 4B',  # Segunda línea de dirección opcional
                    'city': 'Sydney',  # Ciudad fija
                    'state': 'NSW',  # Estado fijo
                    'postal_code': '2000',  # Código postal fijo
                    'country': 'AU'  # País (Australia) con código ISO
                }
            }
        )

        logging.info(f'PaymentIntent creado: {intent["id"]}')
        return jsonify({
            'clientSecret': intent['client_secret']
        })

    except stripe.error.StripeError as e:
        # Capturar errores de Stripe y mostrar información en el servidor
        body = e.json_body
        err = body.get('error', {})
        logging.error(f"Error de Stripe: {err.get('message')}")
        return jsonify(error=err.get('message')), 403

    except Exception as e:
        # Capturar cualquier otro error
        logging.error(f"Error inesperado: {str(e)}")
        return jsonify(error=str(e)), 403


# Endpoint para manejar Webhooks de Stripe
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    logging.info('Recibida solicitud de webhook')  # Imprimir mensaje cuando se recibe el webhook
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('WEBHOOK_SECRET', 'whsec_...')  # Coloca aquí tu webhook secret desde el Dashboard de Stripe

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        logging.info(f"Evento recibido: {event['type']}")
    except ValueError:
        logging.error('Payload inválido')
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        logging.error('Firma inválida del webhook')
        return jsonify({"error": "Invalid signature"}), 400

    # Manejar el evento de pago exitoso
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logging.info(f"PaymentIntent fue exitoso: {payment_intent['id']}")
    # Manejar el evento de pago fallido
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        logging.info(f"PaymentIntent falló: {payment_intent['id']}")

    return jsonify(success=True)


# Endpoint para verificar el estado del pago
@app.route('/check-payment-status', methods=['GET'])
def check_payment_status():
    payment_intent_id = request.args.get('payment_intent')
    logging.info(f'Chequeando estado del PaymentIntent: {payment_intent_id}')

    if payment_intent_id is None:
        logging.error('No payment_intent provided')
        return jsonify({"error": "No payment_intent provided"}), 400

    try:
        # Recuperar el PaymentIntent de Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        status = payment_intent['status']

        # Imprimir el estado en la consola del servidor
        logging.info(f"Estado del PaymentIntent {payment_intent_id}: {status}")

        # Devolver el estado al frontend
        return jsonify({"status": status})

    except stripe.error.StripeError as e:
        logging.error(f"Error al recuperar PaymentIntent: {str(e)}")
        return jsonify({"error": str(e)}), 400


# Endpoint para verificar de la api
@app.route('/working', methods=['GET'])
def check_working():
    return jsonify({"working": True}), 200

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # Usar el puerto proporcionado por el entorno, o 5000 por defecto
    app.run(port=port, debug=True)

