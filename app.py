
from flask import Flask, jsonify
from flask_cors import CORS
from config.config import Config
from controllers.payment_intent import payment_intent_bp
from controllers.webhook import webhook_bp
from config.logging_config import setup_logging

# Configuración de logging
setup_logging()

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Registrar Blueprints
app.register_blueprint(payment_intent_bp)
app.register_blueprint(webhook_bp)

# Endpoint para verificar el estado de la API
@app.route('/working', methods=['GET'])
def check_working():
    return jsonify({"working": True}), 200

if __name__ == "__main__":
    app.run(port=Config.PORT, debug=Config.DEBUG)
