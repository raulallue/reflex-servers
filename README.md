# Servers Reflex - Consola Cloud

Una aplicación web profesional y minimalista construida con [Reflex](https://reflex.dev) para gestionar servidores y sus servicios asociados.

![Dashboard](file:///Users/raul/.gemini/antigravity/brain/5df41892-1ff6-4547-9254-34e96ce97722/final_dashboard_view_1774032925714.png)

## 🐳 Despliegue con Docker (Producción)

Esta aplicación está configurada para ejecutarse en contenedores, ideal para despliegues en servidores remotos con **Portainer**.

### 1. Construir y Subir a Docker Hub

Para subir la imagen a tu repositorio de Docker Hub:

```bash
# Construir y subir para arquitectura amd64 (común en servidores remotos)
# Especialmente importante si estás en un Mac con chip Apple (arm64)
docker buildx build --platform linux/amd64 -t raulallue/reflex-servers:latest . --push
```

### 2. Cómo cambiar la contraseña del Administrador

La seguridad de la aplicación se gestiona mediante variables de entorno, lo que permite cambiar las credenciales sin necesidad de recompilar la imagen:

- **ADMIN_USER**: Nombre de usuario (por defecto: `admin`).
- **ADMIN_PASSWORD**: Contraseña (por defecto: `admin`).

#### En local (docker-compose.yml):
Modifica la sección `environment`:
```yaml
environment:
  - ADMIN_USER=mi_nuevo_usuario
  - ADMIN_PASSWORD=mi_nueva_contraseña
```

#### En Portainer:
Ve a la configuración del **Stack** o del **Contenedor**, busca la pestaña **Env** (Variables de entorno) y actualiza los valores de `ADMIN_USER` y `ADMIN_PASSWORD`. Reinicia el contenedor para aplicar los cambios.

### 3. Despliegue en Portainer (Stacks)

Si usas Portainer, puedes desplegar la aplicación usando un **Stack**. Copia el contenido de `docker-compose.yml` y ajusta las variables de entorno:

```yaml
version: '3'
services:
  app:
    image: raulallue/reflex-servers:latest
    container_name: servers_reflex
    ports:
      - "3003:3003" # Frontend
      - "8003:8003" # Backend
    volumes:
      - servers_reflex_data:/app/
    environment:
      - API_URL=http://<IP-DE-TU-SERVIDOR>:8003
      - ADMIN_USER=admin
      - ADMIN_PASSWORD=admin
    restart: always

volumes:
  servers_reflex_data:
```

> [!IMPORTANT]
> - **Desarrollo Local**: Por defecto se usa el puerto `8000`. No es necesario configurar nada.
## Persistencia de Datos

La base de datos `reflex.db` está **excluida de Git** (`.gitignore`) por seguridad. Esto significa que cuando subas el código a GitHub, tus datos locales **no se harán públicos**.

### Cómo manejar los datos en Producción

1.  **Volumen de Docker**: El archivo `docker-compose.yml` ya está configurado para persistir los datos en un volumen:
    ```yaml
    volumes:
      - ./reflex.db:/app/reflex.db
    ```
2.  **Migración de datos locales**: Si deseas llevar tus datos de desarrollo al servidor:
    - **No uses GitHub**.
    - Sube el archivo `reflex.db` directamente a la carpeta del servidor donde se encuentra el `docker-compose.yml` (mediante SCP, FTP o la interfaz de Portainer).
    - Al reiniciar el contenedor, Reflex detectará tu base de datos con todos los servidores y servicios configurados.

---

## 🚀 Características

- **Gestión de Servidores**: Seguimiento de IPs, credenciales (con toggle de visibilidad) y SSH rápido.
- **Servicios Plegables**: Organiza tus servicios (Portainer, DBs, Apps) bajo cada servidor.
- **Seguridad**: Diálogos de confirmación para borrados y credenciales enmascaradas.
- **Búsqueda Global**: Encuentra cualquier servidor o servicio al instante.

## ⚙️ Instalación Local (Desarrollo)

1. **Instalar dependencias**: `pip install -r requirements.txt`
2. **Inicializar DB**: `reflex db migrate`
3. **Ejecutar**: `reflex run` (disponible en localhost:3000 por defecto en desarrollo).

## 📖 Uso

- **Añadir/Editar**: Usa los iconos de lápiz o el botón superior.
- **Expandir**: Usa el chevron (`>`) para ver los servicios de un servidor.
- **Ver Contraseñas**: Usa el icono del ojo dentro de los modales.
