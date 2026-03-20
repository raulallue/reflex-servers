import reflex as rx
from typing import List, Optional
from sqlmodel import Field

class Server(rx.Model, table=True):
    """The server model."""
    name: str = ""
    address: str
    user: str
    password: str
    location: str = ""
    observations: str

class Service(rx.Model, table=True):
    """The service model."""
    name: str
    url: str
    user: str = ""
    password: str = ""
    icon: str = "globe"
    observations: str = ""
    server_id: int = Field(foreign_key="server.id")
