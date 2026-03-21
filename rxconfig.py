import reflex as rx
import os

config = rx.Config(
    app_name="servers_reflex",
    api_url=os.getenv("API_URL", "__REFLEX_API_URL__"),
    state_auto_setters=True,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)