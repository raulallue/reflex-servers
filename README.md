# Servers Reflex - Consola Cloud

Una aplicación web profesional y minimalista construida con [Reflex](https://reflex.dev) para gestionar servidores y sus servicios asociados.

![Dashboard](file:///Users/raul/.gemini/antigravity/brain/5df41892-1ff6-4547-9254-34e96ce97722/final_dashboard_view_1774032925714.png)

## 🐳 Despliegue con Docker (Producción)

Esta aplicación está configurada para ejecutarse en contenedores, ideal para despliegues en servidores remotos con **Portainer**.

docker buildx build --platform linux/amd64 -t rallue/reflex-servers:latest . --push
```

> [!TIP]
> **Imagen Universal**: Ya no necesitas pasar la IP durante la construcción. La misma imagen sirve para cualquier servidor.

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

1.  Compila y sube la imagen desde tu Mac (Paso 1).
2.  Copia este contenido en tu **Stack** de Portainer:

```yaml
version: '3'
services:
  app:
    image: rallue/reflex-servers:latest
    container_name: servers_reflex
    ports:
      - "3003:3003" # Frontend
      - "8003:8003" # Backend
    volumes:
      - reflex_data:/app
    environment:
      - API_URL=${API_URL:-http://localhost:8003}
      - ADMIN_USER=admin
      - ADMIN_PASSWORD=admin
    restart: always

volumes:
  reflex_data:
```

3.  **Configuración de IP**: En Portainer, ve a la pestaña **Env** de tu Stack y asegúrate de que `API_URL` apunte a la IP de tu servidor: `http://<IP-SERVIDOR>:8003`.

> [!IMPORTANT]
> - **Desarrollo Local**: Por defecto se usa el puerto `8000`. No es necesario configurar nada.
## Persistencia de Datos

La base de datos `reflex.db` está **excluida de Git** (`.gitignore`) por seguridad. Esto significa que cuando subas el código a GitHub, tus datos locales **no se harán públicos**.

### Cómo manejar los datos en Producción

1.  **Volumen de Docker**: El archivo `docker-compose.yml` utiliza un **volumen nombrado** (`reflex_data`) para la persistencia. Esto es más robusto y evita errores de montaje:
    ```yaml
    volumes:
      - reflex_data:/app
    ```
2.  **Migración de datos locales**: Si deseas llevar tus datos de desarrollo al servidor:
    - Sube el archivo `reflex.db` al servidor.
    - Puedes copiarlo al volumen de Docker usando comandos como `docker cp` o instalando el plugin de explorador de archivos en Portainer.
    - La base de datos en el contenedor se encuentra en `/app/reflex.db`.

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
