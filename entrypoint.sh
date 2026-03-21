#!/bin/sh

# Si no se proporciona API_URL, usar localhost:8003 por defecto
if [ -z "$API_URL" ]; then
  API_URL="http://localhost:8003"
fi

echo "Inyectando API_URL: $API_URL"

# Reemplazar el marcador de posición en los archivos JS compilados del frontend
# Esto permite que la imagen sea genérica y la IP se configure en el despliegue (Portainer)
echo "Procesando reemplazos de API_URL en .web/..."
find .web -type f -name "*.js" -print0 | xargs -0 -r sed -i "s|__REFLEX_API_URL__|$API_URL|g" || echo "No se encontraron archivos JS para procesar en esta etapa."

# Ejecutar migraciones y arrancar la aplicación
echo "Ejecutando migraciones de base de datos..."
reflex db migrate

echo "Arrancando Servers Reflex en modo producción..."
exec reflex run --env prod --frontend-port 3003 --backend-port 8003
