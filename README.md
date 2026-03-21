# Servers Reflex - Consola Cloud

Una aplicación web profesional y minimalista construida con [Reflex](https://reflex.dev) para gestionar servidores y sus servicios asociados.

## 🐳 Despliegue con Docker (Producción v1.3)

Esta aplicación está configurada para ejecutarse en contenedores, mapeando los puertos **3003** y **8003** de forma idéntica interna y externamente.

### 1. Compilar y Subir la Imagen

Desde tu Mac, ejecuta:
```bash
docker buildx build --platform linux/amd64 -t rallue/reflex-servers:v1.3 . --push
```

### 2. Configuración en Portainer (Stack)

Copia este contenido en tu **Stack** de Portainer:

```yaml
version: '3'
services:
  app:
    image: rallue/reflex-servers:v1.4
    container_name: servers_reflex
    ports:
      - "3003:3003" # Frontend (1:1)
      - "8003:8003" # Backend (1:1)
    volumes:
      - reflex_data:/app/data # Persistencia SEGURA de BBDD
    environment:
      - API_URL=${API_URL:-http://localhost:8003}
      - ADMIN_USER=admin
      - ADMIN_PASSWORD=admin
    restart: always
    healthcheck:
      test: [ "CMD", "curl", "-f", "http://localhost:8003/ping" ]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  reflex_data:
```

### 3. Configuración de IP

En Portainer, ve a la pestaña **Env** de tu Stack y asegúrate de que `API_URL` apunte a la IP de tu servidor: `http://<IP-SERVIDOR>:8003`.

---

## 🛠️ Depuración y Diagnóstico

Si la página aparece en blanco o hay problemas de comunicación:

1.  **Logs de Portainer**: Busca el bloque `--- REFLEX CONFIG DEBUG ---` al inicio de los logs para verificar la IP detectada.
2.  **Consola del Navegador (F12)**: Busca el mensaje `REFLEX_DEBUG_FRONTEND_API` para ver qué URL está usando el cliente.
3.  **Prueba Directa**: Intenta acceder a `http://<TU-IP>:8003/ping`. Si no responde, revisa el firewall del servidor.

## ⚙️ Instalación Local (Desarrollo)

1. **Instalar dependencias**: `pip install -r requirements.txt`
2. **Inicializar DB**: `reflex db migrate`
3. **Ejecutar**: `reflex run` (disponible en localhost:3000 por defecto).
