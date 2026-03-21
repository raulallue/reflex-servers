import reflex as rx
import os
from .models import Server, Service
from typing import List, Optional

from pydantic import BaseModel

class ServiceDisplay(BaseModel):
    id: Optional[int] = None
    name: str
    url: str
    user: str = ""
    password: str = ""
    icon: str
    observations: str = ""
    is_visible: bool = False

class ServerDisplay(BaseModel):
    id: int
    name: str
    address: str
    user: str
    password: str
    location: str
    observations: str
    is_visible: bool
    parsed_services: List[ServiceDisplay]

class State(rx.State):
    """The app state."""
    servers: List[ServerDisplay] = []
    visible_passwords: dict[int, bool] = {}
    visible_service_passwords: dict[int, bool] = {}
    search_query: str = ""
    
    # Server Form fields
    server_name: str = ""
    address: str = ""
    user: str = ""
    password: str = ""
    location: str = ""
    observations: str = ""
    editing_server_id: int = -1
    
    # Service Form fields
    new_service_name: str = ""
    new_service_url: str = ""
    new_service_user: str = ""
    new_service_password: str = ""
    new_service_observations: str = ""
    editing_service_id: int = -1

    def set_search_query(self, query: str):
        self.search_query = query
        return State.get_servers

    def set_server_name(self, name: str):
        self.server_name = name

    def set_address(self, address: str):
        self.address = address

    def set_user(self, user: str):
        self.user = user

    def set_password(self, password: str):
        self.password = password

    def set_location(self, location: str):
        self.location = location

    def set_observations(self, observations: str):
        self.observations = observations

    def set_new_service_name(self, name: str):
        self.new_service_name = name

    def set_new_service_url(self, url: str):
        self.new_service_url = url

    def set_new_service_user(self, user: str):
        self.new_service_user = user

    def set_new_service_password(self, password: str):
        self.new_service_password = password

    def set_new_service_observations(self, observations: str):
        self.new_service_observations = observations

    def _infer_icon(self, url: str, name: str) -> str:
        lower_url = url.lower()
        lower_name = name.lower()
        if "portainer" in lower_url or "portainer" in lower_name:
            return "container"
        if lower_url.startswith("ssh") or "ssh" in lower_name or "terminal" in lower_name:
            return "terminal"
        if lower_url.startswith("http"):
            return "globe"
        return "external-link"

    def get_servers(self):
        """Get all servers and their services from the database, filtered by search."""
        with rx.session() as session:
            db_servers = session.exec(Server.select()).all()
            all_servers = []
            for s in db_servers:
                if s.id not in self.visible_passwords:
                    self.visible_passwords[s.id] = False
                
                # Fetch related services
                db_services = session.exec(Service.select().where(Service.server_id == s.id)).all()
                parsed_services = []
                for svc in db_services:
                    if svc.id not in self.visible_service_passwords:
                        self.visible_service_passwords[svc.id] = False
                    
                    parsed_services.append(
                        ServiceDisplay(
                            id=svc.id,
                            name=svc.name,
                            url=svc.url,
                            user=svc.user or "",
                            password=svc.password or "",
                            icon=svc.icon,
                            observations=svc.observations,
                            is_visible=self.visible_service_passwords.get(svc.id, False)
                        )
                    )
                
                server_display = ServerDisplay(
                    id=s.id,
                    name=s.name or "N/A",
                    address=s.address,
                    user=s.user,
                    password=s.password,
                    location=s.location or "N/A",
                    observations=s.observations,
                    is_visible=self.visible_passwords.get(s.id, False),
                    parsed_services=parsed_services
                )
                all_servers.append(server_display)

            if self.search_query:
                q = self.search_query.lower()
                filtered = []
                for s in all_servers:
                    server_matches = (
                        q in s.name.lower() or
                        q in s.address.lower() or
                        q in s.location.lower() or
                        q in s.observations.lower()
                    )
                    service_matches = any(
                        q in svc.name.lower() or
                        q in svc.url.lower() or
                        q in svc.observations.lower()
                        for svc in s.parsed_services
                    )
                    if server_matches or service_matches:
                        filtered.append(s)
                self.servers = filtered
            else:
                self.servers = all_servers

    def toggle_password(self, server_id: int):
        """Toggle password visibility for a specific server."""
        self.visible_passwords[server_id] = not self.visible_passwords.get(server_id, False)
        return State.get_servers

    def toggle_service_password(self, service_id: int):
        """Toggle password visibility for a specific service."""
        self.visible_service_passwords[service_id] = not self.visible_service_passwords.get(service_id, False)
        return State.get_servers

    def add_server(self):
        """Add a new server."""
        if not self.address or not self.user:
            return rx.window_alert("Dirección y usuario son obligatorios")
        with rx.session() as session:
            session.add(
                Server(
                    name=self.server_name,
                    address=self.address,
                    user=self.user,
                    password=self.password,
                    location=self.location,
                    observations=self.observations
                )
            )
            session.commit()
        self.clear_server_form()
        return [State.get_servers, rx.toast.success("Servidor añadido correctamente")]

    def clear_server_form(self):
        self.server_name = ""
        self.address = ""
        self.user = ""
        self.password = ""
        self.location = ""
        self.observations = ""
        self.editing_server_id = -1

    def load_server(self, server: ServerDisplay):
        self.editing_server_id = server.id
        self.server_name = server.name
        self.address = server.address
        self.user = server.user
        self.password = server.password
        self.location = server.location
        self.observations = server.observations

    def update_server(self):
        """Update an existing server."""
        if self.editing_server_id == -1: return
        with rx.session() as session:
            server = session.exec(Server.select().where(Server.id == self.editing_server_id)).first()
            if server:
                server.name = self.server_name
                server.address = self.address
                server.user = self.user
                server.password = self.password
                server.location = self.location
                server.observations = self.observations
                session.add(server)
                session.commit()
        self.clear_server_form()
        return [State.get_servers, rx.toast.success("Servidor actualizado")]

    def delete_server(self, server_id: int):
        """Delete a server and its services."""
        with rx.session() as session:
            server = session.exec(Server.select().where(Server.id == server_id)).first()
            if server:
                # Delete related services first
                svcs = session.exec(Service.select().where(Service.server_id == server_id)).all()
                for svc in svcs:
                    session.delete(svc)
                session.delete(server)
                session.commit()
        return [State.get_servers, rx.toast.success("Servidor eliminado")]

    # Authentication state
    authenticated: str = rx.Cookie("false", name="auth_status")
    login_user: str = ""
    login_password: str = ""

    @rx.var
    def is_authenticated(self) -> bool:
        """Helper to get the boolean state of authentication."""
        return self.authenticated == "true"

    def set_login_user(self, val: str):
        self.login_user = val

    def set_login_password(self, val: str):
        self.login_password = val

    # Server form setters
    def set_server_name(self, val: str): self.server_name = val
    def set_server_address(self, val: str): self.server_address = val
    def set_server_user(self, val: str): self.server_user = val
    def set_server_password(self, val: str): self.server_password = val
    def set_server_location(self, val: str): self.server_location = val
    def set_server_observations(self, val: str): self.server_observations = val

    # Service form setters
    def set_new_service_name(self, val: str): self.new_service_name = val
    def set_new_service_url(self, val: str): self.new_service_url = val
    def set_new_service_user(self, val: str): self.new_service_user = val
    def set_new_service_password(self, val: str): self.new_service_password = val
    def set_new_service_observations(self, val: str): self.new_service_observations = val

    # Search setter
    def set_search_query(self, val: str): self.search_query = val

    def on_load_check(self):
        """Check if user is authenticated on page load."""
        if not self.is_authenticated:
            return rx.redirect("/login")

    def login(self):
        """Verify credentials and authenticate session."""
        admin_user = os.getenv("ADMIN_USER", "admin")
        admin_pass = os.getenv("ADMIN_PASSWORD", "admin")
        
        if self.login_user == admin_user and self.login_password == admin_pass:
            self.authenticated = "true"
            self.login_user = ""
            self.login_password = ""
            return rx.redirect("/")
        else:
            return rx.toast.error("Credenciales incorrectas", position="top-center")

    def logout(self):
        """Clear authentication and redirect to login."""
        self.authenticated = "false"
        return rx.redirect("/login")
    expanded_servers: list[int] = []

    def toggle_server_expansion(self, server_id: int):
        if server_id in self.expanded_servers:
            self.expanded_servers.remove(server_id)
        else:
            self.expanded_servers.append(server_id)
    new_service_password_visible: bool = False
    is_server_password_visible: bool = False

    def toggle_new_service_password(self):
        self.new_service_password_visible = not self.new_service_password_visible

    def toggle_server_modal_password(self):
        self.is_server_password_visible = not self.is_server_password_visible

    def clear_service_form(self):
        self.new_service_name = ""
        self.new_service_url = ""
        self.new_service_user = ""
        self.new_service_password = ""
        self.new_service_observations = ""
        self.new_service_password_visible = False
        self.editing_service_id = -1
        self.login_user = ""
        self.login_password = ""

    def clear_server_form(self):
        self.server_name = ""
        self.address = ""
        self.user = ""
        self.password = ""
        self.location = ""
        self.observations = ""
        self.is_server_password_visible = False
        self.editing_server_id = -1

    def add_service(self, server_id: int):
        """Add a new service to a server."""
        if not self.new_service_name or not self.new_service_url:
            return rx.window_alert("Nombre y URL son obligatorios")
        with rx.session() as session:
            new_svc = Service(
                name=self.new_service_name,
                url=self.new_service_url,
                user=self.new_service_user,
                password=self.new_service_password,
                server_id=server_id,
                observations=self.new_service_observations,
                icon=self._infer_icon(self.new_service_url, self.new_service_name)
            )
            session.add(new_svc)
            session.commit()
        self.clear_service_form()
        return [State.get_servers, rx.toast.success("Servicio añadido")]

    def load_service(self, service: ServiceDisplay):
        self.editing_service_id = service.id
        self.new_service_name = service.name
        self.new_service_url = service.url
        self.new_service_user = service.user
        self.new_service_password = service.password
        self.new_service_observations = service.observations

    def update_service(self):
        """Update an existing service."""
        if self.editing_service_id == -1: return
        with rx.session() as session:
            svc = session.exec(Service.select().where(Service.id == self.editing_service_id)).first()
            if svc:
                svc.name = self.new_service_name
                svc.url = self.new_service_url
                svc.user = self.new_service_user
                svc.password = self.new_service_password
                svc.observations = self.new_service_observations
                svc.icon = self._infer_icon(self.new_service_url, self.new_service_name)
                session.add(svc)
                session.commit()
        self.clear_service_form()
        return [State.get_servers, rx.toast.success("Servicio actualizado")]

    def delete_service(self, service_id: int):
        """Delete a service."""
        with rx.session() as session:
            svc = session.exec(Service.select().where(Service.id == service_id)).first()
            if svc:
                session.delete(svc)
                session.commit()
        return [State.get_servers, rx.toast.success("Servicio eliminado")]

    def clear_service_form(self):
        self.new_service_name = ""
        self.new_service_url = ""
        self.new_service_observations = ""
        self.editing_service_id = -1

    def add_service(self, server_id: int):
        """Add a new service to a server."""
        if not self.new_service_name or not self.new_service_url:
            return rx.window_alert("Nombre y URL son obligatorios")
        with rx.session() as session:
            new_svc = Service(
                name=self.new_service_name,
                url=self.new_service_url,
                server_id=server_id,
                observations=self.new_service_observations,
                icon=self._infer_icon(self.new_service_url, self.new_service_name)
            )
            session.add(new_svc)
            session.commit()
        self.clear_service_form()
        return State.get_servers

    def load_service(self, service: ServiceDisplay):
        self.editing_service_id = service.id
        self.new_service_name = service.name
        self.new_service_url = service.url
        self.new_service_observations = service.observations

    def update_service(self):
        """Update an existing service."""
        if self.editing_service_id == -1: return
        with rx.session() as session:
            svc = session.exec(Service.select().where(Service.id == self.editing_service_id)).first()
            if svc:
                svc.name = self.new_service_name
                svc.url = self.new_service_url
                svc.observations = self.new_service_observations
                svc.icon = self._infer_icon(self.new_service_url, self.new_service_name)
                session.add(svc)
                session.commit()
        self.clear_service_form()
        return State.get_servers

    def delete_service(self, service_id: int):
        """Delete a service."""
        with rx.session() as session:
            svc = session.exec(Service.select().where(Service.id == service_id)).first()
            if svc:
                session.delete(svc)
                session.commit()
        return State.get_servers

def server_form() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus"),
                "Añadir Servidor",
                variant="solid",
                color_scheme="blue",
                cursor="pointer",
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Nuevo Servidor", size="6", weight="bold"),
            rx.dialog.description("Introduce los detalles técnicos del servidor principal.", size="2", margin_bottom="1.5em"),
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Nombre del Servidor", size="2", weight="bold"),
                        rx.input(placeholder="ej: Producción Web", on_change=State.set_server_name, value=State.server_name, width="100%", variant="soft"),
                        align_items="start",
                        spacing="1",
                        flex="1",
                    ),
                    rx.vstack(
                        rx.text("Ubicación", size="2", weight="bold"),
                        rx.input(placeholder="ej: Madrid DC1", on_change=State.set_location, value=State.location, width="100%", variant="soft"),
                        align_items="start",
                        spacing="1",
                        flex="1",
                    ),
                    width="100%",
                    spacing="4",
                ),
                rx.vstack(
                    rx.text("Dirección IP / Host", size="2", weight="bold"),
                    rx.input(placeholder="ej: 172.17.17.20", on_change=State.set_address, value=State.address, width="100%", variant="soft"),
                    width="100%",
                    align_items="start",
                    spacing="1",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Usuario", size="2", weight="bold"),
                        rx.input(placeholder="root", on_change=State.set_user, value=State.user, variant="soft"),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Contraseña", size="2", weight="bold"),
                        rx.input(type="password", placeholder="••••••••", on_change=State.set_password, value=State.password, variant="soft"),
                        align_items="start",
                        spacing="1",
                    ),
                    width="100%",
                    spacing="4",
                ),
                rx.vstack(
                    rx.text("Observaciones", size="2", weight="bold"),
                    rx.text_area(placeholder="Notas sobre hardware, función, etc.", on_change=State.set_observations, value=State.observations, width="100%", variant="soft", height="100px"),
                    width="100%",
                    align_items="start",
                    spacing="1",
                ),
                spacing="4",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancelar", variant="ghost", color_scheme="gray", cursor="pointer"),
                ),
                rx.dialog.close(
                    rx.button("Guardar Servidor", on_click=State.add_server, variant="solid", color_scheme="blue", cursor="pointer"),
                ),
                padding_top="2em",
                justify="end",
                spacing="3",
            ),
            max_width="550px",
            padding="2em",
            border_radius="15px",
        ),
    )

def delete_confirm_dialog(item_id: int, name: str, on_confirm: rx.event.EventChain, is_server: bool = True) -> rx.Component:
    item_type = "servidor" if is_server else "servicio"
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            rx.icon(
                "trash-2",
                size=18 if is_server else 14,
                cursor="pointer",
                color=rx.color("red", 9),
                _hover={"opacity": 0.7},
            ),
        ),
        rx.alert_dialog.content(
            rx.alert_dialog.title(f"¿Eliminar {item_type}?"),
            rx.alert_dialog.description(
                f"¿Estás seguro de que deseas eliminar '{name}'? Esta acción no se puede deshacer.",
                size="2"
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Cancelar", variant="soft", color_scheme="gray", cursor="pointer"),
                ),
                rx.alert_dialog.action(
                    rx.button("Eliminar", variant="solid", color_scheme="red", on_click=on_confirm, cursor="pointer"),
                ),
                spacing="3",
                margin_top="4",
                justify="end",
            ),
            max_width="400px",
            border_radius="12px",
        ),
    )

def add_service_dialog(server_id: int) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus"),
                size="1",
                variant="soft",
                color_scheme="green",
                cursor="pointer",
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Nuevo Servicio", size="5", weight="bold"),
            rx.dialog.description("Añade un servicio o URL asociada a este servidor.", size="2", margin_bottom="1em"),
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Nombre", size="2", weight="bold"),
                        rx.input(placeholder="ej: Portainer", on_change=State.set_new_service_name, value=State.new_service_name, variant="soft"),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("URL / Acceso", size="2", weight="bold"),
                        rx.input(placeholder="https://...", on_change=State.set_new_service_url, value=State.new_service_url, variant="soft"),
                        align_items="start",
                        spacing="1",
                    ),
                    width="100%",
                    spacing="4",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Usuario", size="2", weight="bold"),
                        rx.input(placeholder="admin", on_change=State.set_new_service_user, value=State.new_service_user, variant="soft"),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Contraseña", size="2", weight="bold"),
                        rx.hstack(
                            rx.input(
                                type=rx.cond(State.new_service_password_visible, "text", "password"),
                                placeholder="••••••••",
                                on_change=State.set_new_service_password,
                                value=State.new_service_password,
                                variant="soft",
                                flex="1",
                            ),
                            rx.icon(
                                rx.cond(State.new_service_password_visible, "eye-off", "eye"),
                                size=16,
                                cursor="pointer",
                                on_click=State.toggle_new_service_password,
                                color_scheme="gray",
                            ),
                            align="center",
                            width="100%",
                            spacing="2",
                        ),
                        align_items="start",
                        spacing="1",
                    ),
                    width="100%",
                    spacing="4",
                ),
                rx.vstack(
                    rx.text("Observaciones del Servicio", size="2", weight="bold"),
                    rx.text_area(placeholder="Notas específicas...", on_change=State.set_new_service_observations, value=State.new_service_observations, width="100%", variant="soft", height="80px"),
                    width="100%",
                    align_items="start",
                    spacing="1",
                ),
                spacing="4",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancelar", variant="ghost", color_scheme="gray", cursor="pointer", on_click=State.clear_service_form),
                ),
                rx.dialog.close(
                    rx.button("Añadir Servicio", on_click=lambda: State.add_service(server_id), variant="solid", color_scheme="green", cursor="pointer"),
                ),
                padding_top="1.5em",
                justify="end",
                spacing="3",
            ),
            max_width="450px",
            padding="1.5em",
            border_radius="12px",
        ),
    )

def edit_server_dialog(server: ServerDisplay) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon(
                "pencil",
                size=18,
                cursor="pointer",
                color_scheme="blue",
                on_click=lambda: State.load_server(server),
                _hover={"opacity": 0.7},
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Editar Servidor", size="6", weight="bold"),
            rx.dialog.description("Modifica los detalles del servidor principal.", size="2", margin_bottom="1.5em"),
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Nombre del Servidor", size="2", weight="bold"),
                        rx.input(on_change=State.set_server_name, value=State.server_name, width="100%", variant="soft"),
                        align_items="start",
                        spacing="1",
                        flex="1",
                    ),
                    rx.vstack(
                        rx.text("Ubicación", size="2", weight="bold"),
                        rx.input(on_change=State.set_location, value=State.location, width="100%", variant="soft"),
                        align_items="start",
                        spacing="1",
                        flex="1",
                    ),
                    width="100%",
                    spacing="4",
                ),
                rx.vstack(
                    rx.text("Dirección IP / Host", size="2", weight="bold"),
                    rx.input(on_change=State.set_address, value=State.address, width="100%", variant="soft"),
                    width="100%",
                    align_items="start",
                    spacing="1",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Usuario", size="2", weight="bold"),
                        rx.input(on_change=State.set_user, value=State.user, variant="soft"),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Contraseña", size="2", weight="bold"),
                        rx.hstack(
                            rx.input(
                                type=rx.cond(State.is_server_password_visible, "text", "password"),
                                on_change=State.set_password,
                                value=State.password,
                                variant="soft",
                                flex="1",
                            ),
                            rx.icon(
                                rx.cond(State.is_server_password_visible, "eye-off", "eye"),
                                size=16,
                                cursor="pointer",
                                on_click=State.toggle_server_modal_password,
                                color_scheme="gray",
                            ),
                            align="center",
                            width="100%",
                            spacing="2",
                        ),
                        align_items="start",
                        spacing="1",
                    ),
                    width="100%",
                    spacing="4",
                ),
                rx.vstack(
                    rx.text("Observaciones", size="2", weight="bold"),
                    rx.text_area(on_change=State.set_observations, value=State.observations, width="100%", variant="soft", height="100px"),
                    width="100%",
                    align_items="start",
                    spacing="1",
                ),
                spacing="4",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancelar", variant="ghost", color_scheme="gray", cursor="pointer", on_click=State.clear_server_form),
                ),
                rx.dialog.close(
                    rx.button("Guardar Cambios", on_click=State.update_server, variant="solid", color_scheme="blue", cursor="pointer"),
                ),
                padding_top="2em",
                justify="end",
                spacing="3",
            ),
            max_width="550px",
            padding="2em",
            border_radius="15px",
        ),
    )

def edit_service_dialog(service: ServiceDisplay) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon(
                "pencil",
                size=14,
                cursor="pointer",
                color_scheme="blue",
                on_click=lambda: State.load_service(service),
                _hover={"opacity": 0.7},
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Editar Servicio", size="5", weight="bold"),
            rx.dialog.description("Modifica los detalles del servicio o URL.", size="2", margin_bottom="1em"),
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Nombre", size="2", weight="bold"),
                        rx.input(on_change=State.set_new_service_name, value=State.new_service_name, variant="soft"),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("URL / Acceso", size="2", weight="bold"),
                        rx.input(on_change=State.set_new_service_url, value=State.new_service_url, variant="soft"),
                        align_items="start",
                        spacing="1",
                    ),
                    width="100%",
                    spacing="4",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Usuario", size="2", weight="bold"),
                        rx.input(on_change=State.set_new_service_user, value=State.new_service_user, variant="soft"),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Contraseña", size="2", weight="bold"),
                        rx.hstack(
                            rx.input(
                                type=rx.cond(State.new_service_password_visible, "text", "password"),
                                on_change=State.set_new_service_password,
                                value=State.new_service_password,
                                variant="soft",
                                flex="1",
                            ),
                            rx.icon(
                                rx.cond(State.new_service_password_visible, "eye-off", "eye"),
                                size=16,
                                cursor="pointer",
                                on_click=State.toggle_new_service_password,
                                color_scheme="gray",
                            ),
                            align="center",
                            width="100%",
                            spacing="2",
                        ),
                        align_items="start",
                        spacing="1",
                    ),
                    width="100%",
                    spacing="4",
                ),
                rx.vstack(
                    rx.text("Observaciones del Servicio", size="2", weight="bold"),
                    rx.text_area(on_change=State.set_new_service_observations, value=State.new_service_observations, width="100%", variant="soft", height="80px"),
                    width="100%",
                    align_items="start",
                    spacing="1",
                ),
                spacing="4",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancelar", variant="ghost", color_scheme="gray", cursor="pointer", on_click=State.clear_service_form),
                ),
                rx.dialog.close(
                    rx.button("Guardar Cambios", on_click=State.update_service, variant="solid", color_scheme="blue", cursor="pointer"),
                ),
                padding_top="1.5em",
                justify="end",
                spacing="3",
            ),
            max_width="450px",
            padding="1.5em",
            border_radius="12px",
        ),
    )

def render_service_row(service: ServiceDisplay):
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.icon("corner-down-right", size=14, color_scheme="gray", margin_left="1.5em"),
                rx.text(service.name, weight="medium", color=rx.color("gray", 11)),
                spacing="2",
                align="center",
            )
        ),
        rx.table.cell(
            rx.link(
                rx.hstack(
                    rx.icon(service.icon, size=16),
                    rx.text(service.url, size="1"),
                    spacing="2",
                    align="center",
                    color=rx.color("blue", 10),
                ),
                href=service.url,
                is_external=True,
            )
        ),
        rx.table.cell(
            rx.text(service.user, size="1", color=rx.color("gray", 11))
        ),
        rx.table.cell(""), # Location
        rx.table.cell(rx.text(service.observations, size="1", color=rx.color("gray", 10), italic=True)),
        rx.table.cell(""), # Services grouped
        rx.table.cell(
            rx.hstack(
                edit_service_dialog(service),
                delete_confirm_dialog(service.id, service.name, State.delete_service(service.id), is_server=False),
                spacing="3",
                align="center",
            ),
        ),
        bg=rx.color("gray", 2),
    )

def render_server(server: ServerDisplay):
    return rx.fragment(
        rx.table.row(
            rx.table.cell(
                rx.hstack(
                    rx.icon(
                        rx.cond(State.expanded_servers.contains(server.id), "chevron-down", "chevron-right"),
                        size=18,
                        cursor="pointer",
                        on_click=lambda: State.toggle_server_expansion(server.id),
                        color_scheme="gray",
                    ),
                    rx.vstack(
                        rx.text(server.name, weight="bold", color=rx.color("blue", 11)),
                        rx.text(server.address, size="1", color=rx.color("gray", 11)),
                        spacing="0",
                    ),
                    align="center",
                    spacing="2",
                )
            ),
            rx.table.cell(server.user),
            rx.table.cell(
                rx.hstack(
                    rx.text(
                        server.password,
                        style={
                            "-webkit-text-security": rx.cond(
                                server.is_visible, "none", "disc"
                            )
                        },
                    ),
                    rx.icon(
                        rx.cond(server.is_visible, "eye-off", "eye"),
                        size=14,
                        cursor="pointer",
                        on_click=lambda: State.toggle_password(server.id),
                        color_scheme="gray",
                    ),
                    spacing="2",
                    align="center",
                )
            ),
            rx.table.cell(rx.badge(server.location, color_scheme="gray", variant="surface")),
            rx.table.cell(rx.text(server.observations, size="2")),
            rx.table.cell(
                rx.hstack(
                    # Quick SSH link
                    rx.tooltip(
                        rx.link(
                            rx.icon("terminal", size=18, color=rx.color("blue", 9)),
                            href=f"ssh://{server.user}@{server.address}",
                        ),
                        content=f"SSH rápido: {server.user}@{server.address}",
                    ),
                    # Add new service button
                    add_service_dialog(server.id),
                    spacing="3",
                    align="center",
                )
            ),
            rx.table.cell(
                rx.hstack(
                    edit_server_dialog(server),
                    delete_confirm_dialog(server.id, server.name, State.delete_server(server.id)),
                    spacing="3",
                    align="center",
                ),
            ),
            bg=rx.color("gray", 1),
        ),
        rx.cond(
            State.expanded_servers.contains(server.id),
            rx.foreach(
                server.parsed_services,
                render_service_row
            ),
            rx.fragment()
        ),
    )

def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.hstack(
                rx.icon("server", size=40, color=rx.color("blue", 9)),
                rx.heading("Cloud Console", size="8", weight="bold"),
                rx.spacer(),
                rx.hstack(
                    rx.input(
                        rx.input.slot(rx.icon("search", size=16)),
                        placeholder="Buscar por nombre, ip, servicios...",
                        on_change=State.set_search_query,
                        width="250px",
                        variant="soft",
                        size="2",
                    ),
                    server_form(),
                    rx.tooltip(
                        rx.button(
                            rx.icon("log-out", size=18),
                            on_click=State.logout,
                            variant="ghost",
                            color_scheme="gray",
                            cursor="pointer",
                        ),
                        content="Cerrar Sesión",
                    ),
                    spacing="3",
                    align="center",
                ),
                align="center",
                spacing="3",
                width="100%",
                margin_bottom="2em",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Servidor / IP"),
                        rx.table.column_header_cell("Usuario / URL"),
                        rx.table.column_header_cell("Seguridad"),
                        rx.table.column_header_cell("Ubicación"),
                        rx.table.column_header_cell("Observaciones"),
                        rx.table.column_header_cell("Servicios"),
                        rx.table.column_header_cell("Eliminar"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(State.servers, render_server)
                ),
                variant="surface",
                size="3",
                width="100%",
            ),
            on_mount=State.get_servers,
            spacing="5",
            width="100%",
        ),
        padding="3em",
        size="4",
    )

def login_page():
    return rx.center(
        rx.vstack(
            rx.box(
                rx.vstack(
                    rx.center(
                        rx.box(
                            rx.icon("lock", size=32, color=rx.color("blue", 9)),
                            padding="12px",
                            bg=rx.color("blue", 3),
                            border_radius="12px",
                            margin_bottom="16px",
                        ),
                        width="100%",
                    ),
                    rx.vstack(
                        rx.heading("Acceso Cloud Console", size="6", weight="bold", align="center"),
                        rx.text("Introduce tus credenciales para continuar", size="2", color=rx.color("gray", 11), align="center"),
                        spacing="1",
                        width="100%",
                        align="center",
                        margin_bottom="24px",
                    ),
                    rx.vstack(
                        rx.vstack(
                            rx.text("Usuario", size="2", weight="medium", margin_bottom="4px"),
                            rx.input(
                                on_change=State.set_login_user, 
                                value=State.login_user, 
                                width="100%", 
                                variant="surface", 
                                placeholder="Tu usuario",
                                on_key_down=lambda e: rx.cond(e == "Enter", State.login, rx.noop()),
                            ),
                            width="100%",
                            spacing="0",
                        ),
                        rx.vstack(
                            rx.text("Contraseña", size="2", weight="medium", margin_bottom="4px"),
                            rx.input(
                                type="password", 
                                on_change=State.set_login_password, 
                                value=State.login_password, 
                                width="100%", 
                                variant="surface", 
                                placeholder="••••••••",
                                on_key_down=lambda e: rx.cond(e == "Enter", State.login, rx.noop()),
                            ),
                            width="100%",
                            spacing="0",
                        ),
                        rx.button(
                            "Entrar", 
                            on_click=State.login, 
                            width="100%", 
                            color_scheme="blue", 
                            size="3",
                            cursor="pointer",
                            margin_top="8px",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    spacing="0",
                    width="100%",
                ),
                padding="32px",
                width="400px",
                bg=rx.color("gray", 1),
                border=f"1px solid {rx.color('gray', 4)}",
                border_radius="24px",
                box_shadow="0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
            ),
            rx.vstack(
                rx.text(
                    "© 2026 Servers Reflex. Sistema Protegido.",
                    size="1",
                    color=rx.color("gray", 8),
                ),
                rx.text(
                    f"Debug API: {rx.config.api_url}",
                    size="1",
                    color=rx.color("blue", 8),
                    opacity=0.6,
                ),
                spacing="1",
                align="center",
                margin_top="16px",
            ),
            align="center",
        ),
        height="100vh",
        width="100%",
        bg=rx.color("gray", 2), # Simple background for compatibility
        on_mount=rx.script(f"console.log('REFLEX_DEBUG_FRONTEND_API:', '{rx.config.api_url}')"),
    )

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="blue",
    ),
    html_lang="es",
)
app.add_page(index, on_load=State.on_load_check)
app.add_page(login_page, route="/login")
