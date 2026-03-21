import reflex as rx
import os

# Fallback para desarrollo local si no se define API_URL
api_url_env = os.getenv("API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="servers_reflex",
    api_url=api_url_env,
    db_url="sqlite:///data/reflex.db",
    show_built_with_reflex=False,
    state_auto_setters=True,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)

print(f"--- REFLEX CONFIG DEBUG ---")
print(f"API_URL: {config.api_url}")
print(f"---------------------------")