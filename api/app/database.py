import os
import urllib.parse
import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

AZURE_SQL_SERVER = os.getenv("AZURE_SQL_SERVER", "")
AZURE_SQL_DATABASE = os.getenv("AZURE_SQL_DATABASE", "")
AZURE_SQL_USERNAME = os.getenv("AZURE_SQL_USERNAME", "")
AZURE_SQL_PASSWORD = os.getenv("AZURE_SQL_PASSWORD", "")
AZURE_SQL_DRIVER = os.getenv("AZURE_SQL_DRIVER", "ODBC Driver 17 for SQL Server")


connection_string = (
    f"DRIVER={{{AZURE_SQL_DRIVER}}};"
    f"SERVER={AZURE_SQL_SERVER};"
    f"DATABASE={AZURE_SQL_DATABASE};"
    f"UID={AZURE_SQL_USERNAME};"  
    f"PWD={AZURE_SQL_PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)
try:
    # Intentar una conexión de prueba
    test_conn = pyodbc.connect(connection_string)
    test_conn.close()
    print("Conexión de prueba exitosa")
except pyodbc.Error as e:
    print(f"Error de conexión: {str(e)}")
    print(f"Cadena de conexión utilizada: {connection_string}")

# Crear la URL de SQLAlchemy usando la conexión ODBC
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()