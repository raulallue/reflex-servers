#!/bin/sh

# Si no se proporciona API_URL, usar localhost:8003 por defecto
if [ -z "$API_URL" ]; then
  API_URL="http://localhost:8003"
fi

echo "Inyectando API_URL: $API_URL"

# Reemplazar el marcador de posición en los archivos JS compilados del frontend
# Esto permite que la imagen sea genérica y la IP se configure en el despliegue (Portainer)
find .web -type f -name "*.js" -exec sed -i "s|__REFLEX_API_URL__|$API_URL|g" {} +

# Ejecutar migraciones y arrancar la aplicación
echo "Ejecutando migraciones de base de datos..."
reflex db migrate

echo "Arrancando Servers Reflex en modo producción..."
exec reflex run --env prod --frontend-port 3003 --backend-port 8003
