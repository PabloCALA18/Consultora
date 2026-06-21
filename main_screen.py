import flet as ft
from vistas import (
    VistaConsultores,
    VistaCategorias,
    VistaEmpresas,
    VistaProyectos,
    VistaVentas,
)
from theme import C, T, S, R, badge, divider


class MainScreen:
    """Pantalla principal — diseño minimalista con barra superior compacta."""

    def __init__(self, page: ft.Page, conn, usuario: dict, on_logout):
        self.page     = page
        self.conn     = conn
        self.usuario  = usuario
        self.on_logout = on_logout

        self.es_admin: bool = usuario["rol"] == "admin"
        self.nombre_display: str = usuario.get("nombre_empleado") or usuario["username"]

        self._contenido = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
        self._mostrar_bienvenida()

    # ── Navegación ─────────────────────────────────────────────────────────

    def _mostrar_vista(self, clase_vista, titulo: str):
        vista_col = clase_vista(self.conn, self.usuario).build()
        self._contenido.controls.clear()
        self._contenido.controls.extend([
            ft.Container(
                content=ft.Text(titulo, size=T.DISPLAY,
                                weight=ft.FontWeight.W_700, color=C.TEXT),
                padding=ft.padding.only(bottom=S.SM),
            ),
            divider(),
            ft.Container(content=vista_col, padding=ft.padding.only(top=S.MD)),
        ])
        self.page.update()

    def _mostrar_bienvenida(self):
        self._contenido.controls.clear()
        self._contenido.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.WAVING_HAND_OUTLINED,
                                            size=36, color=C.PRIMARY),
                            bgcolor=C.PRIMARY_BG,
                            border_radius=R.MD,
                            padding=S.MD,
                            width=64, height=64,
                        ),
                        ft.Text(f"Bienvenido/a, {self.nombre_display}",
                                size=T.DISPLAY, weight=ft.FontWeight.W_700,
                                color=C.TEXT),
                        ft.Text("Seleccioná una sección desde el menú superior.",
                                size=T.BODY, color=C.TEXT_SUB),
                    ],
                    spacing=S.MD,
                ),
                padding=ft.padding.only(top=S.XL),
            )
        )

    # ── Menú archivo ───────────────────────────────────────────────────────

    def _menu_archivo(self) -> ft.PopupMenuButton:
        return ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Archivo", size=T.SMALL,
                                color=C.TEXT, weight=ft.FontWeight.W_500),
                        ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16, color=C.TEXT_SUB),
                    ],
                    spacing=2, tight=True,
                ),
                padding=ft.padding.symmetric(horizontal=S.SM, vertical=S.XS),
            ),
            items=[
                ft.PopupMenuItem(
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.LOGOUT, size=16, color=C.TEXT_SUB),
                        ft.Text("Cerrar sesión", size=T.BODY, color=C.TEXT),
                    ], spacing=S.SM),
                    on_click=lambda _: self.on_logout(),
                ),
            ],
        )

    # ── Menú herramientas ─────────────────────────────────────────────────

    def _menu_herramientas(self) -> ft.PopupMenuButton:
        def item(texto, icono, vista, titulo):
            return ft.PopupMenuItem(
                content=ft.Row(controls=[
                    ft.Icon(icono, size=16, color=C.TEXT_SUB),
                    ft.Text(texto, size=T.BODY, color=C.TEXT),
                ], spacing=S.SM),
                on_click=lambda _: self._mostrar_vista(vista, titulo),
            )

        items = [
            item("Consultores",      ft.Icons.PEOPLE_OUTLINE,        VistaConsultores, "Consultores"),
            item("Proyectos",        ft.Icons.FOLDER_OPEN_OUTLINED,   VistaProyectos,   "Proyectos"),
            item("Ventas",           ft.Icons.RECEIPT_LONG_OUTLINED,  VistaVentas,      "Ventas"),
        ]
        if self.es_admin:
            items.insert(1, item("Categorías",      ft.Icons.LABEL_OUTLINE,  VistaCategorias, "Categorías"))
            items.insert(3, item("Empresas Clientes", ft.Icons.BUSINESS_OUTLINED, VistaEmpresas, "Empresas Clientes"))

        return ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Herramientas", size=T.SMALL,
                                color=C.TEXT, weight=ft.FontWeight.W_500),
                        ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16, color=C.TEXT_SUB),
                    ],
                    spacing=2, tight=True,
                ),
                padding=ft.padding.symmetric(horizontal=S.SM, vertical=S.XS),
            ),
            items=items,
        )

    # ── Botones rápidos ───────────────────────────────────────────────────

    def _btn(self, icono, tooltip, vista, titulo) -> ft.IconButton:
        return ft.IconButton(
            icon=icono,
            tooltip=tooltip,
            icon_color=C.TEXT_SUB,
            icon_size=20,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=R.SM),
                overlay_color=C.PRIMARY_BG,
            ),
            on_click=lambda _: self._mostrar_vista(vista, titulo),
        )

    def _botones_rapidos(self) -> list[ft.IconButton]:
        botones = [
            self._btn(ft.Icons.PEOPLE_OUTLINE,       "Consultores",       VistaConsultores, "Consultores"),
            self._btn(ft.Icons.FOLDER_OPEN_OUTLINED,  "Proyectos",         VistaProyectos,   "Proyectos"),
            self._btn(ft.Icons.RECEIPT_LONG_OUTLINED, "Ventas",            VistaVentas,      "Ventas"),
        ]
        if self.es_admin:
            botones.insert(1, self._btn(ft.Icons.LABEL_OUTLINE,      "Categorías",        VistaCategorias,  "Categorías"))
            botones.insert(3, self._btn(ft.Icons.BUSINESS_OUTLINED,  "Empresas Clientes", VistaEmpresas,    "Empresas Clientes"))
        return botones

    # ── UI ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Column:
        es_admin = self.usuario["rol"] == "admin"
        color_badge = C.PRIMARY if es_admin else C.SUCCESS

        topbar = ft.Container(
            content=ft.Row(
                controls=[
                    # Logo / nombre app
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.BUSINESS_CENTER_OUTLINED,
                                                size=18, color=C.PRIMARY),
                                bgcolor=C.PRIMARY_BG,
                                border_radius=R.SM,
                                padding=ft.padding.symmetric(horizontal=6, vertical=4),
                            ),
                            ft.Text("Consultora", size=T.BODY,
                                    weight=ft.FontWeight.W_700, color=C.TEXT),
                        ],
                        spacing=S.SM,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    # Menús
                    ft.Container(width=S.MD),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self._menu_archivo(),
                                self._menu_herramientas(),
                            ],
                            spacing=S.XS,
                        ),
                        border=ft.border.all(1, C.BORDER),
                        border_radius=R.SM,
                        padding=ft.padding.symmetric(horizontal=S.XS, vertical=2),
                    ),
                    ft.Container(expand=True),
                    # Accesos rápidos
                    ft.Container(
                        content=ft.Row(controls=self._botones_rapidos(), spacing=2),
                        border=ft.border.all(1, C.BORDER),
                        border_radius=R.SM,
                        padding=ft.padding.symmetric(horizontal=S.XS, vertical=2),
                    ),
                    ft.Container(width=S.SM),
                    # Usuario + badge
                    ft.Row(
                        controls=[
                            ft.Text(f"👤  {self.nombre_display}",
                                    size=T.SMALL, color=C.TEXT_SUB),
                            badge(self.usuario["rol"].upper(), color_bg=color_badge),
                        ],
                        spacing=S.SM,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=S.XS,
            ),
            bgcolor=C.SURFACE,
            border=ft.border.only(bottom=ft.BorderSide(1, C.BORDER)),
            padding=ft.padding.symmetric(horizontal=S.LG, vertical=S.SM),
            height=52,
        )

        contenido_wrapper = ft.Container(
            content=self._contenido,
            expand=True,
            padding=ft.padding.symmetric(horizontal=S.XL, vertical=S.LG),
            bgcolor=C.BG,
        )

        return ft.Column(
            controls=[topbar, contenido_wrapper],
            expand=True,
            spacing=0,
        )


def pantalla_principal(page, conn, usuario, on_logout) -> ft.Column:
    return MainScreen(page, conn, usuario, on_logout).build()