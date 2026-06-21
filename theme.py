"""
theme.py — Sistema de tokens visuales. Dark theme.
"""
import flet as ft

# ── Paleta oscura ─────────────────────────────────────────────────────────────

class C:
    """Colors — dark mode."""
    BG          = "#0F1117"   # fondo de página
    SURFACE     = "#1A1D27"   # cards, paneles, topbar
    BORDER      = "#2A2D3A"   # bordes sutiles
    DIVIDER     = "#22253A"   # separadores internos

    PRIMARY     = "#3B82F6"   # azul principal
    PRIMARY_DIM = "#2563EB"   # hover / acento oscuro
    PRIMARY_BG  = "#1E3A5F"   # fondo tint primario

    TEXT        = "#F1F5F9"   # texto principal
    TEXT_SUB    = "#64748B"   # texto secundario / labels
    TEXT_HINT   = "#475569"   # placeholders

    SUCCESS     = "#22C55E"
    ERROR       = "#F87171"
    ERROR_BG    = "#2D1515"

    WHITE       = "#F1F5F9"
    ACCENT_BAR  = "#3B82F6"   # franja decorativa


# ── Tipografía ────────────────────────────────────────────────────────────────

class T:
    """Type scale."""
    DISPLAY = 24
    TITLE   = 18
    BODY    = 14
    SMALL   = 12
    MICRO   = 11


# ── Espaciado ─────────────────────────────────────────────────────────────────

class S:
    """Spacing."""
    XS  = 4
    SM  = 8
    MD  = 16
    LG  = 24
    XL  = 32
    XXL = 48


# ── Radios ────────────────────────────────────────────────────────────────────

class R:
    """Border radius."""
    SM = 4
    MD = 6
    LG = 10


# ── Helpers ───────────────────────────────────────────────────────────────────

def label(text: str, size: int = T.BODY, color: str = C.TEXT_SUB,
          weight=ft.FontWeight.NORMAL) -> ft.Text:
    return ft.Text(text, size=size, color=color, weight=weight)


def divider() -> ft.Divider:
    return ft.Divider(height=1, color=C.BORDER)


def badge(texto: str, color_bg: str = C.PRIMARY) -> ft.Container:
    return ft.Container(
        content=ft.Text(texto, size=T.MICRO, color="#FFFFFF", weight=ft.FontWeight.W_600),
        bgcolor=color_bg,
        border_radius=R.SM,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
    )