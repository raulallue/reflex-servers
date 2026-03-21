import reflex as rx
import os

config = rx.Config(
    app_name="servers_reflex",
    show_built_with_reflex=False,
    state_auto_setters=True,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)