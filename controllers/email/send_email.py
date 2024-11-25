import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config.config import Config



def send_email(to_email, subject, dynamic_data, template_id):
    """
    Enviar un correo utilizando SendGrid y plantillas dinámicas.
    
    :param to_email: Dirección de correo del destinatario
    :param subject: Asunto del correo
    :param dynamic_data: Diccionario con datos dinámicos para la plantilla
    :param template_id: ID de la plantilla de SendGrid
    """
    try:
        # Configurar el correo
        message = Mail(
            from_email=(Config.MAIL_FROM_ADDRESS, Config.MAIL_FROM_NAME),
            to_emails=to_email,
        )
        message.dynamic_template_data = dynamic_data
        message.template_id = template_id
        message.subject = subject

        # Enviar el correo
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"Email enviado. Estado: {response.status_code}")
        print(f"Respuesta: {response.body}")
    except Exception as e:
        print(f"Error enviando el correo: {e}")

# Enviar correo para el comprador
def send_order_success_email_to_buyer(user, order):
    print(user)
    print(order)

    """
    Enviar el correo de confirmación de compra al comprador.
    
    :param user: Diccionario con datos del usuario (nombre, email, etc.)
    :param order: Diccionario con datos de la orden (número, fecha, etc.)
    """
    template_id = "d-daf895616f5f4de3aecda438a6edf8e8"  # ID de la plantilla para el comprador
    dynamic_data = {
        "User_name": str(user["name"]),
        "Item_name": f"{order['brand_name']} - {order['category_title']}",
        "Order_number": str(order["order_no"]),
        "Date_of_purchase": str(order["date_of_purchase"]),
        "Buyer_shipping_address": order["buyer_shipping_address"],
        "Seller_first_name": order["seller_first_name"],
        "Seller_second_name_initial": order["seller_second_name_initial"],
        "Item_overall_price": str(order["final_price"]),
        "Item_main_photo": order["product_image"][0],
        "Order_no": str(order["order_no"]),
    }
    send_email(
        to_email=user["email"],
        subject="¡Tu pedido ha sido confirmado!",
        dynamic_data=dynamic_data,
        template_id=template_id,
    )

# Enviar correo para el vendedor
def send_delivery_reminder_email_to_seller(user, product):
    """
    Enviar un recordatorio de envío al vendedor.
    
    :param user: Diccionario con datos del vendedor (nombre, email, etc.)
    :param product: Diccionario con datos del producto (nombre, categoría, etc.)
    """
    template_id = "d-ed10c142124e438d841406cd5efb4197"  # ID de la plantilla para el vendedor
    dynamic_data = {
        "User_name": user["name"],
        "Item_name": f"{product['brand_name']} - {product['category_title']}",
        "Date_of_purchase": str(product["date_of_purchase"]),
        "Buyer_first_name": product["buyer_first_name"],
        "Buyer_second_name": product["buyer_second_name"],
        "Buyer_email": product["buyer_email"],
        "shipping_address": product["buyer_shipping_address"],
        "Number_of_business_days": str(product["number_of_business_days"]),
        "Item_main_photo": product["product_image"][0],

        'Item_price': str(product['price']),
        'Commission_fee': str(product['commission_fee']),
        'Proccessing_fee': str(3),
        # 'Buyer_fee': str(product[''])
        'Shipping_cost': str(product['delivery_cost']),
        'Earned_money': str(product['earned_money'])
    }
    send_email(
        to_email=user["email"],
        subject="¡Prepárate para enviar el pedido!",
        dynamic_data=dynamic_data,
        template_id=template_id,
    )


# 01he9mdcpnbb5n58xcc3syy7rp lauren 


# 'User_name'
# 'Item_name'
# 'Date_of_purchase
# 'Buyer_first_name
# 'Buyer_second_name
# 'Buyer_email
# 'shipping_address
# 'Number_of_business_days
# 'Item_main_photo

# 'Item_price
# 'Commission_fee
# 'Proccessing_fee
# 'Buyer_fee
# 'Shipping_cost
# 'Earned_money


# user_buyer = {
#     "name": "Lauren Kennedy",
#     "email": "lauren@highend.app",
# }

# order = {
#     "brand_name": " X",
#     "category_title": " Y",
#     "order_no": "12345",
#     "date_of_purchase": "2024-11-23 20:12:00",
#     "buyer_shipping_address": "24 Stanmore Street, WA, Shenton Park, 6008",
#     "seller_first_name": "Carlos",
#     "seller_second_name_initial": "G",
#     "item_price": "500.00",
#     "item_main_photo": "https://assets.highend.app/ocixuq1u-img2709.webp",
# }

# send_order_success_email_to_buyer(user_buyer, order)


# user_seller = {
#     "name": "Lauren Kennedy",
#     "email": "lauren@highend.app",
# }

# product = {
#     "brand_name": "Marca X",
#     "category_title": "Categoría Y",
#     "item_main_photo": "https://assets.highend.app/ocixuq1u-img2709.webp",
#     "date_of_purchase": "2024-11-23 20:12:00",
#     "buyer_first_name": "Juan",
#     "buyer_second_name": "Pérez",
#     "buyer_email": "lemos.ema@gmail.com",
#     "shipping_address": "24 Stanmore Street, WA, Shenton Park, 6008",
#     "number_of_business_days": "5",
# }

# send_delivery_reminder_email_to_seller(user_seller, product)
