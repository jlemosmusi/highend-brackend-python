import psycopg2
import json
from db.conection import get_connection # Solo importa si no es "local"

def get_user_with_address(user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Consulta SQL para obtener los datos
            query = """
            SELECT 
                u.id,
                u.email,
                u.name,
                u.surname,
                u.phone AS user_phone,
                delivery.state AS delivery_state,
                delivery.suburb AS delivery_suburb,
                delivery.address_1 AS delivery_address_1,
                delivery.address_2 AS delivery_address_2,
                delivery.zip AS delivery_zip,
                billing.state AS billing_state,
                billing.suburb AS billing_suburb,
                billing.address_1 AS billing_address_1,
                billing.address_2 AS billing_address_2,
                billing.zip AS billing_zip
            FROM users u
            LEFT JOIN addresses delivery ON u.id = delivery.user_id AND delivery.type = 'DELIVERY'
            LEFT JOIN addresses billing ON u.id = billing.user_id AND billing.type = 'BILLING'
            WHERE u.id = %s;
            """
            
            # Ejecutar la consulta con el user_id proporcionado
            cursor.execute(query, (user_id,))
            
            # Obtener los resultados
            result = cursor.fetchone()
            
            if result:
                # Construir el JSON con ambas direcciones
                user_data = {
                    "id": result[0],
                    "email": result[1],
                    "name": result[2],
                    "surname": result[3],
                    "phone": result[4],
                    "delivery_address": {
                        "state": result[5],
                        "suburb": result[6],
                        "address_1": result[7],
                        "address_2": result[8],
                        "zip": result[9]
                    },
                    "billing_address": {
                        "state": result[10],
                        "suburb": result[11],
                        "address_1": result[12],
                        "address_2": result[13],
                        "zip": result[14]
                    }
                }
                return user_data # Convertir a JSON
            else:
                return json.dumps({"error": "User not found."})
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return json.dumps({"error": "An error occurred."})
    
    finally:
        connection.close()




# get_user_with_address('01j7jt0v75gxhdp7ff3ana3jrw')