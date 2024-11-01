import os
import psycopg2

if os.getenv("ENVIRONMENT") == "production":
    connection = psycopg2.connect(
        host="127.0.0.1",
        port="5432",
        database="dbCopyAWSHighEnd",
        user="postgres",
        password="Aa.111Aa.111"
    )
else:
    connection = None  # Set to None if in production