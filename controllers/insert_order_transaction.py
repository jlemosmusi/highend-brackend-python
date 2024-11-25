from flask import Blueprint, jsonify, request
import stripe
import logging
from config.config import Config
import os
from dotenv import load_dotenv
from controllers.get_cart_products_by_user import obtener_productos_usuario
from datetime import datetime, timedelta
from utils.generate_id import generate_ulid
from controllers.products.get_image_by_product_id import get_main_photo_urls
from controllers.user.get_data_user_by_id import get_user_with_address
from controllers.email.send_email import send_delivery_reminder_email_to_seller,send_order_success_email_to_buyer


load_dotenv()
if os.getenv("ENVIRONMENT") != "local":
    from utils.auth import sanctum_auth_required
    from db.conection import get_connection # Solo importa si no es "local"

# Configuración de Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

# Crear un blueprint para el PaymentIntent
insert_order_transaction = Blueprint("insert_order_transaction", __name__)

# Conditionally apply the decorator if in development
if os.getenv("ENVIRONMENT") != "local":
    print('ENVIRONMENT')
    @insert_order_transaction.route("/insert_order_succeeded", methods=["POST"])
    # @sanctum_auth_required
    def create_order_transaction():
        data = request.json
        buyer_user_id = data.get("buyer_user_id")
        payment_intent_id= data.get("payment_intent_id")
        try:
            products_id=data.get("products_id")
        except:
            products_id=[]

        return insert_new_order_new_transaction(buyer_user_id,payment_intent_id,products_id)
else:
    @insert_order_transaction.route("/insert_order_succeeded-payment-intent", methods=["POST"])
    def create_order_transaction():
        data = request.json
        buyer_user_id = data.get("buyer_user_id")
        payment_intent_id= data.get("payment_intent_id")
        try:
            products_id=data.get("products_id")
        except:
            products_id=[]
        return insert_new_order_new_transaction(buyer_user_id,payment_intent_id,products_id)
    



def get_products_by_ids(product_ids):
    """
    Obtiene información de productos desde la base de datos para los IDs proporcionados,
    incluyendo la marca y la categoría asociada.

    Args:
        product_ids (list): Lista de IDs de productos.

    Returns:
        list: Lista de diccionarios con información de los productos.
    """
    query = """
        SELECT 
            p.id, 
            p.brand_id, 
            b.name AS brand_name, 
            p.user_id,
            p.category_id, 
            c.title AS category_title,
            p.status, 
            p.price, 
            p.delivery_cost, 
            p.final_price
        FROM 
            public.products p
        LEFT JOIN 
            public.brands b ON p.brand_id = b.id
        LEFT JOIN 
            public.categories c ON p.category_id = c.id
        WHERE 
            p.id = ANY(%s);
    """

    try:
        # Obtener la conexión
        connection = get_connection()
        
        # Usar el cursor dentro del contexto `with`
        with connection.cursor() as cursor:
            # Ejecutar la consulta
            cursor.execute(query, (product_ids,))
            
            # Recuperar los resultados como diccionarios
            columns = [desc[0] for desc in cursor.description]  # Obtener nombres de las columnas
            products = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Combinar columnas y filas
            
            return products

    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        if connection:
            connection.close() 

# user_id="01jc7b4q9as2ckd73890zbzy07"
def getProductFromCartByUserId(user_id):
    try:
        connection=get_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM carts WHERE user_id = %s
            """, (user_id,))
            cart_id = cursor.fetchone()

            cursor.execute("""
                SELECT product_id FROM cart_products WHERE cart_id = %s
            """, (cart_id,))
            products_id = cursor.fetchall()
            finalProducts=[]
            if products_id:
                for p in products_id:
                    finalProducts.append(p[0])
            logging.info(f"User products in cart {products_id}")
            return finalProducts
    except Exception as e:  
        logging.error(f"Error products in cart: {e}")
        connection.rollback()
    
    finally:
        if connection:
            connection.close()

def generate_unique_order_number(max_value=999999999):
    connection=get_connection()

    with connection.cursor() as cursor:
        while True:  # Loop para generar un número único
            # Obtener el número total de órdenes y generar un nuevo número
            cursor.execute("SELECT COUNT(*) FROM orders;")
            row_count = cursor.fetchone()[0]
            order_number = row_count + 1

            # Verificar si el número ya existe
            cursor.execute("SELECT 1 FROM orders WHERE order_no = %s", (order_number,))
            exists = cursor.fetchone()

            if not exists:  # Si no existe, lo utilizamos
                print(f"Generated unique order number: {order_number}")
                break  # Salimos del loop

    
    return order_number

def get_app_settings_order_fees_and_threshold_days():
    connection=get_connection()
    # Obtener configuración de comisiones y umbral de preparación
    with connection.cursor() as cursor:
        cursor.execute("SELECT order_fees, order_preparation_threshold FROM app_settings LIMIT 1")
        app_settings = cursor.fetchone()
        order_fees = app_settings[0]["collection"]
        preparation_threshold_days = app_settings[1]
    return order_fees, preparation_threshold_days

def find_fee(final_price, order_fees):
    for fee in order_fees:
        # Convertir los límites a Decimal
        range_from = float(fee['from'])
        range_to = float(fee['to'])
        
        if range_from <= final_price <= range_to:
            return fee['fee']
    return None

# user_id='01hzp7y46x5syt3yr97j5yyxkv'
def user_addresses(user_id):
    query = """
        SELECT 
            id, 
            user_id,
            type,
            name, 
            surname, 
            phone,
            state, 
            suburb, 
            address_1,
            address_2,
            zip
        FROM 
            public.addresses
        WHERE 
            user_id = %s;
    """

    try:
        # Obtener la conexión
        connection = get_connection()
        
        # Usar el cursor dentro del contexto `with`
        with connection.cursor() as cursor:
            # Ejecutar la consulta
            cursor.execute(query, (user_id,))
            # Recuperar los resultados como diccionarios
            columns = [desc[0] for desc in cursor.description]  # Obtener nombres de columnas
            addresses = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convertir filas en diccionarios
            
            return addresses  # Devolver las direcciones

    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return []  # Devuelve una lista vacía en caso de error
    finally:
        if connection:
            connection.close()  


# {
#     "orders":[
#         {
#             "product_id":
#         }
#     ]
# }

# buyer_user_id='01j7jt0v75gxhdp7ff3ana3jrw'
# products_id=['01hrr9xt57k0fyc45kf4adv8vx','01j1k2e6p75ydr7kya394m7t1a']
# stripe_id= "pi_3PaxGYCUpuUR1Oe91PtmUK3v"
def insert_new_order_new_transaction(buyer_user_id, stripe_id, products_id: list = None):
    try:
        # Si no se proporcionan products_id, los obtiene del carrito del usuario
        if products_id is None:
            products_id_from_cart = getProductFromCartByUserId(buyer_user_id)
            if not products_id_from_cart:
                print('no hay nada en el carrito')
                return {"response":"no hay nada en el carrito"}
        else:
            products_id_from_cart = products_id
            if not products_id_from_cart:
                print('no existe el o los productos')
                return {"response":"no existe el o los productos"}

        order_fees, preparation_threshold_days=get_app_settings_order_fees_and_threshold_days()
        
        orders= {
            "orders": {
                "products": get_products_by_ids(products_id_from_cart)
            }
        }


        # address_user=user_addresses(buyer_user_id)
        buyer_info=get_user_with_address(buyer_user_id)

        full_address = ', '.join(filter(None, [
                    buyer_info['delivery_address'].get('address_1'),  # Obtén 'address_1' o None
                    buyer_info['delivery_address'].get('address_2'),  # Obtén 'address_2' o None
                    buyer_info['delivery_address'].get('state'),      # Obtén 'state' o None
                    buyer_info['delivery_address'].get('suburb'),     # Obtén 'suburb' o None
                    buyer_info['delivery_address'].get('zip')         # Obtén 'zip' o None
                ]))
        
        full_billing_address = ', '.join(filter(None, [
                    buyer_info['billing_address'].get('address_1'),  # Obtén 'address_1' o None
                    buyer_info['billing_address'].get('address_2'),  # Obtén 'address_2' o None
                    buyer_info['billing_address'].get('state'),      # Obtén 'state' o None
                    buyer_info['billing_address'].get('suburb'),     # Obtén 'suburb' o None
                    buyer_info['billing_address'].get('zip')         # Obtén 'zip' o None
                ]))
        
        

        
        total_price_transaction=0
        counter_for_orders_num=0
        for p in orders['orders']['products']:
            # check if the prodct its in other stage not "ACTIVE"
            # if p['status'] != "ACTIVE":
            #     print(f'el {p['id']} producto  no esta activo')
                # return print(f'el {p['id']} producto  no esta activo')
            p['order_id']=generate_ulid()
            p['seller_user_id']=p['user_id']
            p['buyer_user_id']=buyer_user_id
            p['product_id']=p['id']
            p['product_image']= get_main_photo_urls(p['product_id'])
            p['order_no']=generate_unique_order_number()+counter_for_orders_num
            p['status']='PREPARING'
            p['delivery_status']='AWAITING_SENDING'
            p['preparing_finished_at']= datetime.now() + timedelta(days=preparation_threshold_days)
            p['address']= full_address
            p['billing_address']= full_billing_address
            p['created_at']= datetime.now()
            p['date_of_purchase']= datetime.now()
            p['commission_fee']= find_fee(float(p['final_price']),order_fees)
            p['final_price_in_cent']= p['final_price']*100
            
            # buyer info
            p['buyer_first_name']=buyer_info['name']
            p['buyer_second_name']=buyer_info['surname']
            p['buyer_email']=buyer_info['email']
            p['buyer_shipping_address']= full_address
            p['number_of_business_days']=str(preparation_threshold_days)

            # seller info 
            seller_info=get_user_with_address(p['seller_user_id'])
            p['seller_info']=seller_info
            p['seller_first_name']=seller_info['name']
            p['seller_second_name_initial']=seller_info['surname'][0]
            descuento = 3 / 100  # 3% como decimal

            p['earned_money'] = str(float(p['price']) - (float(p['price']) * descuento))

            # p['Earned_money']=str(p['price']*0.97)
            

            total_price_transaction+=p['final_price_in_cent']
            counter_for_orders_num+=1



        # Creación de Transacción
        orders['transaction']={
            "transaction_id":generate_ulid(),
            "currency_id": "01he2qdgggyeg4e05swctvtkvf",
            "amount":total_price_transaction,
            "type":"PAYMENT",
            "external_id":stripe_id,
            "status": "SUCCESSFUL",
            "created_at": datetime.now()
        }

        response=insertOrderAndTransaction(orders)
        
        # envio emails
        if response:
            for prod in orders['orders']['products']:
                send_order_success_email_to_buyer({
                    "name":prod['buyer_first_name'],
                    "email":prod['buyer_email']
                    }, prod)
                send_delivery_reminder_email_to_seller({
                    "name":prod['seller_first_name'],
                    "email":prod['seller_info']['email']
                    }, prod)


        return {
            # "response":response,
            "data":orders
        }

        # calculo el carrito
            

    except:
        return False

        # creo el numero de orden

        # validacion de direcciones
        # validacion de productos

        # validacion de intencion de pagos
        # Creación de Pedidos
        # Eventos y Limpieza
         #=>OrderPremiumVerifiedShippedSellerMail
         # Usa una plantilla de SendGrid (TEMPLATE_ID: d-97cc412a54fb47dba13a053d62a92047).



# {
#     "orders": {
#         "products": [
#             {
#                 "address": "24 Stanmore Street, WA, Shenton Park, 6008",
#                 "billing_address": "24 Stanmore Street, WA, Shenton Park, 6008",
#                 "brand_id": "01heaa90cds3286mq4c8p1713f",
#                 "buyer_user_id": "01hzp7y46x5syt3yr97j5yyxkv",
#                 "commission_fee": "20%",
#                 "created_at": "Sat, 23 Nov 2024 20:12:00 GMT",
#                 "delivery_cost": "20.00",
#                 "delivery_status": "AWAITING_SENDING",
#                 "final_price": "500.00",
#                 "final_price_in_cent": "50000.00",
#                 "id": "01hrr9xt57k0fyc45kf4adv8vx",
#                 "order_id": "01JDC4NNNN164XVWR7NX4NA70Z",
#                 "order_no": 793,
#                 "preparing_finished_at": "Sat, 30 Nov 2024 20:12:00 GMT",
#                 "price": "480.00",
#                 "product_id": "01hrr9xt57k0fyc45kf4adv8vx",
#                 "seller_user_id": "01hgf249vmk8n7w7zbbcgb4pfk",
#                 "status": "PREPARING",
#                 "user_id": "01hgf249vmk8n7w7zbbcgb4pfk"
#             },
#             {
#                 "address": "24 Stanmore Street, WA, Shenton Park, 6008",
#                 "billing_address": "24 Stanmore Street, WA, Shenton Park, 6008",
#                 "brand_id": "01heaa90cds3286mq4c8p1713f",
#                 "buyer_user_id": "01hzp7y46x5syt3yr97j5yyxkv",
#                 "commission_fee": "18%",
#                 "created_at": "Sat, 23 Nov 2024 20:12:00 GMT",
#                 "delivery_cost": "25.00",
#                 "delivery_status": "AWAITING_SENDING",
#                 "final_price": "825.00",
#                 "final_price_in_cent": "82500.00",
#                 "id": "01j1k2e6p75ydr7kya394m7t1a",
#                 "order_id": "01JDC4NP000SQ9G2RPYX8X1MAZ",
#                 "order_no": 794,
#                 "preparing_finished_at": "Sat, 30 Nov 2024 20:12:00 GMT",
#                 "price": "800.00",
#                 "product_id": "01j1k2e6p75ydr7kya394m7t1a",
#                 "seller_user_id": "01hnd7y7b5q25epj4cfr1ph2b1",
#                 "status": "PREPARING",
#                 "user_id": "01hnd7y7b5q25epj4cfr1ph2b1"
#             }
#         ]
#     },
#     "transaction": {
#         "amount": "132500.00",
#         "created_at": "Sat, 23 Nov 2024 20:12:00 GMT",
#         "external_id": "pi_3PaxGYCUpuUR1Oe91PtmUK3v",
#         "status": "SUCCESSFUL",
#         "type": "PAYMENT"
#     }
# }
def insertOrderAndTransaction(jsonData):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Inserta transacción primero
            transaction = jsonData['transaction']
            cursor.execute("""
                INSERT INTO transactions (id, currency_id, amount, created_at, external_id, status, type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                transaction['transaction_id'],
                transaction['currency_id'],
                transaction['amount'],
                transaction['created_at'],
                transaction['external_id'],
                transaction['status'],
                transaction['type']
            ))

            print(f'transactions {transaction["transaction_id"]}')
 
            # Iterar sobre los productos y crear órdenes
            for product in jsonData['orders']['products']:
                cursor.execute("""
                    INSERT INTO orders (id, user_id, product_id, order_no, status, delivery_status, preparing_finished_at, address, billing_address, created_at, commission_fee)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    product['order_id'],
                    product['buyer_user_id'],
                    product['product_id'],
                    product['order_no'],
                    product['status'],
                    product['delivery_status'],
                    product['preparing_finished_at'],
                    product['address'],
                    product['billing_address'],
                    product['created_at'],
                    product['commission_fee']
                ))
                
                print(f'order {product["order_id"]}')

                # Inserción en order_transactions
                cursor.execute("""
                    INSERT INTO order_transactions (id, order_id, transaction_id)
                    VALUES (%s, %s, %s)
                """, (generate_ulid(), product['order_id'], transaction['transaction_id']))

                print('order_transactions')

                # cambio el estado del producto
                cursor.execute("""
                UPDATE products
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """, ('BOUGHT', product['id']))

                print('products')


            # Eliminar los productos del carrito del comprador
            try:
                buyer_user_id = jsonData['orders']['products'][0]['buyer_user_id']
                cursor.execute("""
                    DELETE FROM carts
                    WHERE user_id = %s
                """, (buyer_user_id,))
                print(f"Cart items for user {buyer_user_id} deleted successfully.")
            except Exception as e:
                print(f"Error deleting cart items: {e}")
            
            # Confirmar transacción
            connection.commit()
            connection.close()
            print("Orders and transaction inserted successfully!")
            return "Orders and transaction inserted successfully"

    except Exception as e:
        connection.rollback()
        print(f"Error occurred: {e}")
        return f"Error occurred: {e}"

    finally:
        connection.close()
        # Inserto cambio de estado del producto "BOUGHT"




