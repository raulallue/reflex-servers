import reflex as rx
import os

config = rx.Config(
    app_name="servers_reflex",
    api_url=os.getenv("API_URL"),
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