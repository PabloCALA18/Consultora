import flet as ft
from auth import AuthService
from theme import C, T, S, R, divider


class LoginScreen:
    """Pantalla de inicio de sesión — modo oscuro, pantalla completa."""

    # Paleta oscura local (no depende de C para el fondo)
    _BG        = "#0F1117"
    _SURFACE   = "#1A1D27"
    _BORDER    = "#2A2D3A"
    _PRIMARY   = "#3B82F6"
    _PRIMARY_D = "#2563EB"
    _TEXT      = "#F1F5F9"
    _TEXT_SUB  = "#64748B"
    _ERROR     = "#F87171"

    def __init__(self, page: ft.Page, conn, on_login_ok):
        self.page = page
        self.conn = conn
        self.on_login_ok = on_login_ok
        self._auth = AuthService(conn) if conn else None

        self.campo_user = ft.TextField(
            label="Usuario",
            label_style=ft.TextStyle(size=13, color=self._TEXT_SUB),
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            autofocus=True,
            border_color=self._BORDER,
            focused_border_color=self._PRIMARY,
            cursor_color=self._PRIMARY,
            bgcolor=self._SURFACE,
            text_style=ft.TextStyle(size=14, color=self._TEXT),
            filled=True,
            on_submit=self._intentar_login,
        )
        self.campo_pass = ft.TextField(
            label="Contraseña",
            label_style=ft.TextStyle(size=13, color=self._TEXT_SUB),
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_color=self._BORDER,
            focused_border_color=self._PRIMARY,
            cursor_color=self._PRIMARY,
            bgcolor=self._SURFACE,
            text_style=ft.TextStyle(size=14, color=self._TEXT),
            filled=True,
            on_submit=self._intentar_login,
        )
        self.error_txt = ft.Text("", color=self._ERROR, size=13)

    def _mostrar_error(self, mensaje: str):
        self.error_txt.value = mensaje
        self.page.update()

    def _intentar_login(self, _e=None):
        self.error_txt.value = ""
        usuario  = (self.campo_user.value or "").strip()
        password = self.campo_pass.value or ""

        if not usuario or not password:
            return self._mostrar_error("Completá usuario y contraseña.")
        if self._auth is None:
            return self._mostrar_error("Sin conexión a la base de datos.")

        datos = self._auth.login(usuario, password)
        if datos:
            self.on_login_ok(datos)
        else:
            self.campo_pass.value = ""
            self._mostrar_error("Usuario o contraseña incorrectos.")

    def build(self) -> ft.Container:
        # ── Card central ──────────────────────────────────────────────────
        card = ft.Container(
            content=ft.Column(
                controls=[
                    # Logo + título
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.BUSINESS_CENTER_OUTLINED,
                                    size=22, color=self._PRIMARY,
                                ),
                                bgcolor="#1E3A5F",
                                border_radius=10,
                                padding=ft.padding.all(10),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Sistema de Consultora",
                                        size=18,
                                        weight=ft.FontWeight.W_700,
                                        color=self._TEXT,
                                    ),
                                    ft.Text(
                                        "Iniciá sesión para continuar",
                                        size=12,
                                        color=self._TEXT_SUB,
                                    ),
                                ],
                                spacing=2,
                            ),
                        ],
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(color=self._BORDER, height=24),
                    # Campos
                    self.campo_user,
                    self.campo_pass,
                    # Error
                    ft.Container(content=self.error_txt, height=18),
                    ft.Container(height=4),
                    # Botón
                    ft.ElevatedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ARROW_FORWARD, size=18),
                                ft.Text("Ingresar", size=14, weight=ft.FontWeight.W_600),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        height=44,
                        style=ft.ButtonStyle(
                            bgcolor=self._PRIMARY,
                            color=self._TEXT,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            overlay_color=self._PRIMARY_D,
                        ),
                        on_click=self._intentar_login,
                    ),
                ],
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            width=400,
            bgcolor=self._SURFACE,
            border_radius=14,
            border=ft.border.all(1, self._BORDER),
            padding=ft.padding.symmetric(horizontal=36, vertical=32),
            shadow=ft.BoxShadow(
                blur_radius=40,
                color="#40000000",
                offset=ft.Offset(0, 8),
            ),
        )

        # ── Pantalla completa con fondo oscuro y card centrado ────────────
        return ft.Container(
            content=ft.Column(
                controls=[card],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=self._BG,
            expand=True,
            alignment=ft.Alignment(0, 0),
        )


def pantalla_login(page, conn, on_login_ok) -> ft.Container:
    return LoginScreen(page, conn, on_login_ok).build()