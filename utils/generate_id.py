import time
import random

def generate_ulid():
    """
    Genera un ULID usando el timestamp actual (en milisegundos) 
    y entropía aleatoria para garantizar unicidad.
    """
    # Paso 1: Obtener el tiempo actual en milisegundos desde la época Unix
    timestamp = int(time.time() * 1000)
    
    # Paso 2: Convertir el timestamp a una cadena en Base32 (primeros 10 caracteres del ULID)
    base32_alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    timestamp_str = ""
    
    # Convertir timestamp a Base32 manualmente
    for _ in range(10):
        timestamp_str = base32_alphabet[timestamp % 32] + timestamp_str
        timestamp //= 32

    # Paso 3: Generar 16 caracteres aleatorios en Base32 para la entropía
    entropy_str = ''.join(random.choice(base32_alphabet) for _ in range(16))
    
    # Paso 4: Combinar timestamp y entropía para formar el ULID
    ulid = timestamp_str + entropy_str
    return ulid

