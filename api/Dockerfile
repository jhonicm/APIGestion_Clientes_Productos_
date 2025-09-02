FROM python:3.9

WORKDIR /app

# Instalar dependencias del sistema y ODBC para SQL Server (Azure SQL)
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    unixodbc \
    unixodbc-dev \
    gnupg2

# Agregar repositorio de Microsoft y clave (sin apt-key)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]