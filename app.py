from flask import Flask, jsonify
from flask_cors import CORS
from config.config import Config
from controllers.auth.auth_by_email import loginByEmail
from controllers.payment_intent import payment_intent_bp
from controllers.webhook import webhook_bp
from controllers.get_oder import getOrder
from controllers.get_user_history_transaction import get_user_hist
from controllers.insert_order_transaction import insert_order_transaction

from config.logging_config import setup_logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
setup_logging()

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Registrar Blueprints
app.register_blueprint(loginByEmail)
app.register_blueprint(payment_intent_bp)
app.register_blueprint(webhook_bp)
app.register_blueprint(getOrder)
app.register_blueprint(get_user_hist)

app.register_blueprint(insert_order_transaction)


# 
# Endpoint para verificar el estado de la API
@app.route('/api/microservicio/working', methods=['GET'])
def check_working():
    return jsonify({"new v2": True}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)

