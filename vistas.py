import flet as ft
from theme import C, T, S, R, divider

# ── Clase base ────────────────────────────────────────────────────────────────

class BaseVista:
    """Clase base para todas las vistas de tabla."""

    TABLE_STYLE = dict(
        border=ft.border.all(1, C.BORDER),
        heading_row_color=C.PRIMARY_BG,
        data_row_min_height=40,
        heading_row_height=44,
        divider_thickness=1,
        column_spacing=24,
    )

    def __init__(self, conn, usuario=None):
        self.conn    = conn
        self.usuario = usuario
        self._todos_los_rows: list = []
        self._tabla: ft.DataTable | None = None

    def _fetch(self, sql: str, params=()) -> list:
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def _hacer_filas(self, rows: list) -> list[ft.DataRow]:
        raise NotImplementedError

    def _columnas(self) -> list[ft.DataColumn]:
        raise NotImplementedError

    def _sql_all(self) -> str:
        raise NotImplementedError

    # ── Helpers de celda ─────────────────────────────────────────────────────

    @staticmethod
    def _col(text: str) -> ft.DataColumn:
        return ft.DataColumn(
            ft.Text(text, size=T.SMALL, weight=ft.FontWeight.W_600,
                    color=C.TEXT_SUB)
        )

    @staticmethod
    def _cell(text: str, mono: bool = False) -> ft.DataCell:
        return ft.DataCell(
            ft.Text(str(text) if text is not None else "—",
                    size=T.BODY, color=C.TEXT,
                    font_family="monospace" if mono else None)
        )

    @staticmethod
    def _cell_muted(text: str) -> ft.DataCell:
        return ft.DataCell(
            ft.Text(str(text) if text else "—", size=T.BODY, color=C.TEXT_SUB)
        )

    # ── Barra de filtros ──────────────────────────────────────────────────────

    def _barra_filtros(
        self,
        *,
        dropdown_label: str,
        dropdown_opciones: list[str],
        on_dropdown: callable,
        on_fetchone: callable,
        on_fetchall: callable,
        campo_busqueda_label: str = "Buscar...",
    ) -> ft.Row:
        self._dd_label = ft.Text(
            dropdown_label if dropdown_label != "—" else "Filtrar",
            size=T.SMALL, color=C.TEXT, weight=ft.FontWeight.W_500,
        )

        def _hacer_item(opcion: str):
            def _handler(_e, op=opcion):
                self._dd_label.value = op
                self._dd_label.update()
                on_dropdown(op)
            return ft.PopupMenuItem(
                content=ft.Text(opcion, size=T.BODY, color=C.TEXT),
                on_click=_handler,
            )

        items = [_hacer_item(o) for o in dropdown_opciones]

        dd_btn = ft.PopupMenuButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.FILTER_LIST_OUTLINED, size=15, color=C.TEXT_SUB),
                    self._dd_label,
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=15, color=C.TEXT_SUB),
                ],
                spacing=4, tight=True,
            ),
            items=items or [ft.PopupMenuItem(content=ft.Text("Sin opciones", size=T.BODY))],
        )

        self._campo_busqueda = ft.TextField(
            label=campo_busqueda_label,
            label_style=ft.TextStyle(size=T.SMALL, color=C.TEXT_SUB),
            prefix_icon=ft.Icons.SEARCH,
            width=260,
            height=40,
            text_style=ft.TextStyle(size=T.BODY, color=C.TEXT),
            border_color=C.BORDER,
            focused_border_color=C.PRIMARY,
            cursor_color=C.PRIMARY,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
            on_submit=lambda e: on_fetchone(e.control.value),
        )

        def _reset(_):
            self._dd_label.value = dropdown_label if dropdown_label != "—" else "Filtrar"
            self._campo_busqueda.value = ""
            on_fetchall()

        buscar_btn = ft.IconButton(
            icon=ft.Icons.SEARCH,
            tooltip="Buscar",
            icon_color=C.PRIMARY,
            icon_size=18,
            style=ft.ButtonStyle(
                bgcolor=C.PRIMARY_BG,
                shape=ft.RoundedRectangleBorder(radius=R.SM),
                overlay_color=C.BORDER,
            ),
            on_click=lambda _: on_fetchone(self._campo_busqueda.value),
        )
        reset_btn = ft.IconButton(
            icon=ft.Icons.REFRESH_OUTLINED,
            tooltip="Mostrar todo",
            icon_color=C.TEXT_SUB,
            icon_size=18,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=R.SM),
                overlay_color=C.BORDER,
            ),
            on_click=_reset,
        )

        controls = []
        if items:
            controls.append(
                ft.Container(
                    content=dd_btn,
                    border=ft.border.all(1, C.BORDER),
                    border_radius=R.SM,
                    padding=ft.padding.symmetric(horizontal=S.SM, vertical=4),
                    bgcolor=C.SURFACE,
                )
            )
        controls += [self._campo_busqueda, buscar_btn, reset_btn]

        return ft.Row(controls=controls, spacing=S.SM, wrap=True)

    def _actualizar_tabla(self, rows: list):
        self._tabla.rows = self._hacer_filas(rows)
        if self._tabla.page:
            self._tabla.update()

    def build(self) -> ft.Column:
        raise NotImplementedError

    def __call__(self) -> ft.Column:
        return self.build()


# ── VistaConsultores ──────────────────────────────────────────────────────────

class VistaConsultores(BaseVista):

    _SQL = """
        SELECT c.cod_empleado, c.nombre, c.sueldo,
               cat.nombre AS categoria, j.nombre AS jefe
        FROM consultor c
        JOIN categoria cat ON cat.id_categoria = c.id_categoria
        LEFT JOIN consultor j ON j.cod_empleado = c.jefe
        {where}
        ORDER BY c.cod_empleado
    """

    def _columnas(self):
        return [
            self._col("CÓD."),
            self._col("NOMBRE"),
            self._col("SUELDO"),
            self._col("CATEGORÍA"),
            self._col("JEFE"),
        ]

    def _hacer_filas(self, rows):
        return [
            ft.DataRow(cells=[
                self._cell(r[0], mono=True),
                self._cell(r[1]),
                self._cell(f"${r[2]:,.2f}"),
                self._cell(r[3]),
                self._cell_muted(r[4]),
            ]) for r in rows
        ]

    def _sql_all(self):
        return self._SQL.format(where="")

    def _categorias(self) -> list[str]:
        rows = self._fetch("SELECT nombre FROM categoria ORDER BY nombre")
        return [r[0] for r in rows]

    def _on_dropdown(self, categoria: str):
        if not categoria:
            return
        rows = self._fetch(self._SQL.format(where="WHERE cat.nombre = %s"), (categoria,))
        self._actualizar_tabla(rows)

    def _on_fetchone(self, texto: str):
        texto = (texto or "").strip()
        if not texto:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE c.nombre LIKE %s OR c.cod_empleado LIKE %s"),
            (f"%{texto}%", f"%{texto}%"),
        )
        self._actualizar_tabla(rows)

    def _on_fetchall(self):
        self._actualizar_tabla(self._todos_los_rows)

    def build(self) -> ft.Column:
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(columns=self._columnas(),
                                   rows=self._hacer_filas(self._todos_los_rows),
                                   **self.TABLE_STYLE)
        barra = self._barra_filtros(
            dropdown_label="Categoría", dropdown_opciones=self._categorias(),
            on_dropdown=self._on_dropdown, on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            campo_busqueda_label="Buscar por nombre o cód.",
        )
        return ft.Column(controls=[barra, self._tabla], spacing=S.MD)


# ── VistaCategorias ───────────────────────────────────────────────────────────

class VistaCategorias(BaseVista):

    _SQL = """
        SELECT id_categoria, nombre, salario_rec
        FROM categoria
        {where}
        ORDER BY id_categoria
    """

    def _columnas(self):
        return [self._col("ID"), self._col("NOMBRE"), self._col("SALARIO REC.")]

    def _hacer_filas(self, rows):
        return [
            ft.DataRow(cells=[
                self._cell(r[0], mono=True),
                self._cell(r[1]),
                self._cell(f"${r[2]:,.2f}"),
            ]) for r in rows
        ]

    def _sql_all(self):
        return self._SQL.format(where="")

    def _on_dropdown(self, _valor): pass

    def _on_fetchone(self, texto: str):
        texto = (texto or "").strip()
        if not texto:
            return
        rows = self._fetch(self._SQL.format(where="WHERE nombre LIKE %s"), (f"%{texto}%",))
        self._actualizar_tabla(rows)

    def _on_fetchall(self):
        self._actualizar_tabla(self._todos_los_rows)

    def build(self) -> ft.Column:
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(columns=self._columnas(),
                                   rows=self._hacer_filas(self._todos_los_rows),
                                   **self.TABLE_STYLE)
        barra = self._barra_filtros(
            dropdown_label="—", dropdown_opciones=[],
            on_dropdown=self._on_dropdown, on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            campo_busqueda_label="Buscar por nombre",
        )
        return ft.Column(controls=[barra, self._tabla], spacing=S.MD)


# ── VistaEmpresas ─────────────────────────────────────────────────────────────

class VistaEmpresas(BaseVista):

    _SQL = """
        SELECT ec.cif, ec.nombre, ec.direccion,
               GROUP_CONCAT(tc.telefono SEPARATOR ' / ') AS telefonos
        FROM empresa_cliente ec
        LEFT JOIN telefono_cliente tc ON tc.cif = ec.cif
        {where}
        GROUP BY ec.cif, ec.nombre, ec.direccion
        ORDER BY ec.nombre
    """

    def _columnas(self):
        return [self._col("CIF"), self._col("EMPRESA"), self._col("DIRECCIÓN"), self._col("TELÉFONOS")]

    def _hacer_filas(self, rows):
        return [
            ft.DataRow(cells=[
                self._cell(r[0], mono=True),
                self._cell(r[1]),
                self._cell(r[2]),
                self._cell_muted(r[3]),
            ]) for r in rows
        ]

    def _sql_all(self):
        return self._SQL.format(where="")

    def _on_dropdown(self, _valor): pass

    def _on_fetchone(self, texto: str):
        texto = (texto or "").strip()
        if not texto:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE ec.nombre LIKE %s OR ec.cif LIKE %s"),
            (f"%{texto}%", f"%{texto}%"),
        )
        self._actualizar_tabla(rows)

    def _on_fetchall(self):
        self._actualizar_tabla(self._todos_los_rows)

    def build(self) -> ft.Column:
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(columns=self._columnas(),
                                   rows=self._hacer_filas(self._todos_los_rows),
                                   **self.TABLE_STYLE)
        barra = self._barra_filtros(
            dropdown_label="—", dropdown_opciones=[],
            on_dropdown=self._on_dropdown, on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            campo_busqueda_label="Buscar por nombre o CIF",
        )
        return ft.Column(controls=[barra, self._tabla], spacing=S.MD)


# ── VistaProyectos ────────────────────────────────────────────────────────────

class VistaProyectos(BaseVista):

    _SQL = """
        SELECT id_proyecto, descripcion, coste
        FROM proyecto
        {where}
        ORDER BY id_proyecto
    """

    def _columnas(self):
        return [self._col("ID"), self._col("DESCRIPCIÓN"), self._col("COSTE INTERNO")]

    def _hacer_filas(self, rows):
        return [
            ft.DataRow(cells=[
                self._cell(r[0], mono=True),
                self._cell(r[1]),
                self._cell(f"${r[2]:,.2f}"),
            ]) for r in rows
        ]

    def _sql_all(self):
        return self._SQL.format(where="")

    def _on_dropdown(self, _valor): pass

    def _on_fetchone(self, texto: str):
        texto = (texto or "").strip()
        if not texto:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE descripcion LIKE %s OR id_proyecto LIKE %s"),
            (f"%{texto}%", f"%{texto}%"),
        )
        self._actualizar_tabla(rows)

    def _on_fetchall(self):
        self._actualizar_tabla(self._todos_los_rows)

    def build(self) -> ft.Column:
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(columns=self._columnas(),
                                   rows=self._hacer_filas(self._todos_los_rows),
                                   **self.TABLE_STYLE)
        barra = self._barra_filtros(
            dropdown_label="—", dropdown_opciones=[],
            on_dropdown=self._on_dropdown, on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            campo_busqueda_label="Buscar por descripción o ID",
        )
        return ft.Column(controls=[barra, self._tabla], spacing=S.MD)


# ── VistaVentas ───────────────────────────────────────────────────────────────

class VistaVentas(BaseVista):

    _SQL = """
        SELECT v.id_venta, ec.nombre, p.id_proyecto,
               c.nombre, v.precio, v.fecha_inicio, v.fecha_fin
        FROM venta v
        JOIN empresa_cliente ec ON ec.cif         = v.cif
        JOIN proyecto         p  ON p.id_proyecto  = v.id_proyecto
        JOIN consultor        c  ON c.cod_empleado = v.cod_empleado
        {where}
        ORDER BY v.id_venta
    """

    def _columnas(self):
        return [
            self._col("ID"),
            self._col("EMPRESA"),
            self._col("PROY."),
            self._col("CONSULTOR"),
            self._col("PRECIO"),
            self._col("INICIO"),
            self._col("FIN"),
        ]

    def _hacer_filas(self, rows):
        return [
            ft.DataRow(cells=[
                self._cell(r[0], mono=True),
                self._cell(r[1]),
                self._cell(r[2], mono=True),
                self._cell(r[3]),
                self._cell(f"${r[4]:,.2f}"),
                self._cell_muted(r[5]),
                self._cell_muted(r[6]),
            ]) for r in rows
        ]

    def _sql_all(self):
        return self._SQL.format(where="")

    def _empresas(self) -> list[str]:
        rows = self._fetch("SELECT nombre FROM empresa_cliente ORDER BY nombre")
        return [r[0] for r in rows]

    def _on_dropdown(self, empresa: str):
        if not empresa:
            return
        rows = self._fetch(self._SQL.format(where="WHERE ec.nombre = %s"), (empresa,))
        self._actualizar_tabla(rows)

    def _on_fetchone(self, texto: str):
        texto = (texto or "").strip()
        if not texto:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE v.id_venta LIKE %s OR c.nombre LIKE %s OR ec.nombre LIKE %s"),
            (f"%{texto}%", f"%{texto}%", f"%{texto}%"),
        )
        self._actualizar_tabla(rows)

    def _on_fetchall(self):
        self._actualizar_tabla(self._todos_los_rows)

    def build(self) -> ft.Column:
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(columns=self._columnas(),
                                   rows=self._hacer_filas(self._todos_los_rows),
                                   **self.TABLE_STYLE)
        barra = self._barra_filtros(
            dropdown_label="Empresa", dropdown_opciones=self._empresas(),
            on_dropdown=self._on_dropdown, on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            campo_busqueda_label="Buscar por ID, consultor o empresa",
        )
        return ft.Column(controls=[barra, self._tabla], spacing=S.MD)


# ── Helpers de módulo ─────────────────────────────────────────────────────────

def vista_consultores(conn, u): return VistaConsultores(conn, u).build()
def vista_categorias(conn, u):  return VistaCategorias(conn, u).build()
def vista_empresas(conn, u):    return VistaEmpresas(conn, u).build()
def vista_proyectos(conn, u):   return VistaProyectos(conn, u).build()
def vista_ventas(conn, u):      return VistaVentas(conn, u).build()