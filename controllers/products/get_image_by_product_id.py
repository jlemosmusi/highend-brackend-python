
from db.conection import get_connection # Solo importa si no es "local"


def get_main_photo_urls(product_id):
    # Configurar la conexión a PostgreSQL
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            # Consulta para obtener las URLs de "Main photo"
            query = """
            SELECT a.url
            FROM product_images pi
            JOIN category_asset_groups cag ON pi.category_asset_group_id = cag.id
            JOIN product_asset_groups pag ON cag.product_asset_group_id = pag.id
            JOIN assets a ON pi.asset_id = a.id
            WHERE pag.name = 'Main photo' AND pi.product_id = %s;
            """
            
            # Ejecutar la consulta
            cursor.execute(query, (product_id,))
            
            # Recuperar los resultados
            urls = [row[0] for row in cursor.fetchall()]
            
            return urls  # Lista de URLs de imágenes principales

    except Exception as e:
        print(f"Error retrieving main photo URLs: {e}")
        return []

    finally:
        connection.close()

