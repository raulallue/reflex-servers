# Imagen base de Python
FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y permitir que los logs lleguen al terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Variables de entorno por defecto para el administrador
ENV ADMIN_USER=admin
ENV ADMIN_PASSWORD=admin

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl -sL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Inicializar Reflex y preparar el frontend
RUN reflex init

# Exponer los puertos solicitados (8003 backend, 3003 frontend)
EXPOSE 8003 3003

# Comando para arrancar en modo producción, igual que en el proyecto overlay
CMD ["reflex", "run", "--env", "prod", "--frontend-port", "3003", "--backend-port", "8003"]
