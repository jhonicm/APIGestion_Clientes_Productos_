#!/bin/bash

# Esperar a que el servidor SQL esté disponible
echo "Esperando a que el servidor SQL esté disponible..."
sleep 15

# Iniciar la API
echo "Iniciando la API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
