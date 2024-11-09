from db.conection import get_connection

def obtener_productos_usuario(user_id):
    try:
        conexion = get_connection()
        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor()

        # Consulta para obtener los ids de los carritos del usuario en la tabla carts
        consulta_carts = """
            SELECT id 
            FROM carts 
            WHERE user_id = %s AND deleted_at IS NULL
        """
        cursor.execute(consulta_carts, (user_id,))
        cart_ids = [row[0] for row in cursor.fetchall()]

        # Si no hay carritos para el usuario, devolvemos una lista vacía
        if not cart_ids:
            return []

        # Consulta para obtener los product_id de los cart_id encontrados en la tabla cart_products
        consulta_productos = """
            SELECT product_id 
            FROM cart_products 
            WHERE cart_id = ANY(%s)
        """
        cursor.execute(consulta_productos, (cart_ids,))
        product_ids = [row[0] for row in cursor.fetchall()]

        return product_ids

    except Exception as e:
        print("Error al realizar la consulta:", e)
        return []
    
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()

# Ejemplo de uso
# user_id = '01j7jt0v75gxhdp7ff3ana3jrw'  # Reemplaza por el user_id que deseas consultar
# productos = obtener_productos_usuario(user_id)
# print("IDs products:", productos)
