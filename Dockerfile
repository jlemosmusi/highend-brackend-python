# Usa una imagen base de Python ligera
FROM python:3.9-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requerimientos y ajusta psycopg2 a psycopg2-binary para simplificar la instalación
COPY requirements.txt .
RUN sed -i 's/psycopg2/psycopg2-binary/' requirements.txt

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación
COPY . .

# Configura las variables de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=5000

# Exponer el puerto utilizado por Flask
EXPOSE 5000

# Comando para iniciar la aplicación
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
