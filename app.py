import flet as ft
from database import DatabaseConnection
from login_screen import LoginScreen
from main_screen import MainScreen
from theme import C


class App:
    TITLE  = "Sistema de Consultora"
    WIDTH  = 1200
    HEIGHT = 740

    def __init__(self, page: ft.Page):
        self.page = page
        self.conn = None
        self._configurar_pagina()
        self._conectar_db()
        self.mostrar_login()

    def _configurar_pagina(self):
        self.page.title         = self.TITLE
        self.page.window_width  = self.WIDTH
        self.page.window_height = self.HEIGHT
        self.page.bgcolor       = C.BG
        self.page.padding       = 0
        self.page.theme_mode    = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(
            color_scheme_seed=C.PRIMARY,
            use_material3=True,
        )
        self.page.dark_theme = ft.Theme(
            color_scheme_seed=C.PRIMARY,
            use_material3=True,
        )

    def _conectar_db(self):
        self.conn = DatabaseConnection().connect()

    def mostrar_login(self):
        self.page.bgcolor = C.BG
        self.page.controls.clear()
        self.page.add(LoginScreen(self.page, self.conn, on_login_ok=self.mostrar_app).build())
        self.page.update()

    def mostrar_app(self, usuario: dict):
        self.page.bgcolor = C.BG
        self.page.controls.clear()
        self.page.add(MainScreen(self.page, self.conn, usuario, on_logout=self.mostrar_login).build())
        self.page.update()


def main(page: ft.Page):
    App(page)


ft.app(target=main)