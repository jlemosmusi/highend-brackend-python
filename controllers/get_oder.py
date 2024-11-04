import logging
from flask import jsonify, request, Blueprint
from psycopg2.extras import RealDictCursor
from db.conection import connection

getOrder = Blueprint("getOrder", __name__)

# fetch_order_details_by_payment_intent('pi_3QGCMiC070pu0s7s0SxFQjH7')
def fetch_order_details_by_payment_intent(payment_intent_id):
    response = {"data": {"createOrderOnCharge": []}}

    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT id FROM transactions
            WHERE external_id = %s
        """, (payment_intent_id,))
        transaction = cursor.fetchone()

        if not transaction:
            return {"error": "Transaction not found"}, 404

        transaction_id = transaction["id"]

        cursor.execute("""
            SELECT order_id FROM order_transactions
            WHERE transaction_id = %s
        """, (transaction_id,))
        order_ids = cursor.fetchall()

        if not order_ids:
            return {"error": "No orders found for the given transaction"}, 404

        for order in order_ids:
            order_id = order["order_id"]

            cursor.execute("""
                SELECT o.id AS order_id, o.order_no, o.status AS order_status, 
                       o.delivery_status, o.address, o.billing_address, 
                       p.id AS product_id, p.description AS product_description, 
                       p.final_price AS product_final_price, p.delivery_cost, 
                       p.price AS product_price, p.condition AS product_condition,
                       p.status AS product_status, u.id AS user_id, u.name AS user_name, 
                       u.surname AS user_surname, u.email AS user_email,
                       c.symbol AS currency_symbol, c.code AS currency_code,
                       b.name AS brand_name, cat.title AS category_title,
                       cat.size_guide_type
                FROM orders o
                JOIN products p ON o.product_id = p.id
                JOIN users u ON o.user_id = u.id
                JOIN currencies c ON p.currency_id = c.id
                JOIN brands b ON p.brand_id = b.id
                JOIN categories cat ON p.category_id = cat.id
                WHERE o.id = %s
            """, (order_id,))
            order_data = cursor.fetchone()

            if not order_data:
                continue

            order_detail = {
                "id": order_data["order_id"],
                "order_no": order_data["order_no"],
                "status": order_data["order_status"],
                "delivery_status": order_data["delivery_status"],
                "billing_address": order_data["billing_address"],
                "address": order_data["address"],
                "user": {
                    "id": order_data["user_id"],
                    "name": order_data["user_name"],
                    "surname": order_data["user_surname"],
                    "email": order_data["user_email"]
                },
                "product": {
                    "id": order_data["product_id"],
                    "description": order_data["product_description"],
                    "finalPrice": float(order_data["product_final_price"]),
                    "price": float(order_data["product_price"]),
                    "condition": order_data["product_condition"],
                    "status": order_data["product_status"],
                    "delivery_cost": float(order_data["delivery_cost"]),
                    "currency": {
                        "symbol": order_data["currency_symbol"],
                        "code": order_data["currency_code"]
                    },
                    "brand": {
                        "name": order_data["brand_name"]
                    },
                    "category": {
                        "title": order_data["category_title"],
                        "size_guide_type": order_data["size_guide_type"]
                    }
                }
            }

            # Obtener el campo de `fields`
            cursor.execute("""
                SELECT f.id, f.name, f.type, fv.name AS field_value_name
                FROM fields f
                JOIN field_values fv ON f.id = fv.field_id
                JOIN product_field_values pfv ON pfv.field_value_id = fv.id
                WHERE pfv.product_id = %s
            """, (order_data["product_id"],))

            fields = {}
            for field in cursor.fetchall():
                field_type = field["type"].lower()
                if field_type not in fields:
                    fields[field_type] = []
                fields[field_type].append(field["field_value_name"])

            order_detail["product"]["fields"] = [{"name": key, "values": value} for key, value in fields.items()]

            # Obtener los activos de imagen
            cursor.execute("""
                SELECT a.id AS asset_id, a.url, a.thumbs, pag.position AS position, pag.name
                FROM product_images pi
                JOIN assets a ON pi.asset_id = a.id
                JOIN category_asset_groups cag ON pi.category_asset_group_id = cag.id
                JOIN product_asset_groups pag ON cag.product_asset_group_id = pag.id
                WHERE pi.product_id = %s
                ORDER BY pag.position
            """, (order_data["product_id"],))

            assets = []
            for asset in cursor.fetchall():
                asset_entry = {
                    "id": asset["asset_id"],
                    "url": asset["url"],
                    "thumbs": asset["thumbs"],
                    "category_asset_group": {
                        "id": asset["position"],
                        "productAssetGroup": {
                            "position": asset["position"]
                        }
                    }
                }
                assets.append(asset_entry)

            order_detail["product"]["productImages"] = assets

            # Agregar el campo `productMainAsset` usando el primer activo de imagen
            if assets:
                order_detail["product"]["productMainAsset"] = {
                    "id": assets[0]["id"],
                    "url": assets[0]["url"],
                    "thumbs": assets[0]["thumbs"]
                }
            else:
                order_detail["product"]["productMainAsset"] = None  # En caso de que no haya imágenes

            response["data"]["createOrderOnCharge"].append(order_detail)

    return response

@getOrder.route("/api/orders/by_payment_intent", methods=["GET"])
def get_orders_by_payment_intent():
    payment_intent_id = request.args.get("paymentIntentId")
    if not payment_intent_id:
        return jsonify({"error": "Payment Intent ID is required"}), 400
    try:
        order_details = fetch_order_details_by_payment_intent(payment_intent_id)
        return jsonify(order_details)
    except Exception as e:
        logging.error(f"Error fetching order details: {e}")
        return jsonify({"error": "Internal server error"}), 500
