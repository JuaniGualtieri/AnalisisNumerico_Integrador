# -*- coding: utf-8 -*-
"""
============================================================================
  tema.py  --  Paleta de colores y utilidades de estilo para la interfaz
============================================================================
Centraliza los colores y los ayudantes de estilo para que toda la aplicación
tenga un aspecto coherente y profesional, tanto en modo OSCURO como CLARO.

Cada color se define como una tupla (claro, oscuro): CustomTkinter elige
automáticamente según el modo de apariencia activo.
============================================================================
"""

import customtkinter as ctk

# --- Colores principales (claro, oscuro) ---------------------------------
ACENTO        = ("#2563EB", "#3B82F6")   # azul de acción
ACENTO_HOVER  = ("#1D4ED8", "#2563EB")
EXITO         = ("#059669", "#10B981")   # verde
EXITO_HOVER   = ("#047857", "#059669")
PELIGRO       = ("#DC2626", "#EF4444")   # rojo
ADVERTENCIA   = ("#D97706", "#F59E0B")   # ámbar
VIOLETA       = ("#7C3AED", "#8B5CF6")

# Fondos
FONDO_APP     = ("#F1F5F9", "#0F172A")   # fondo general
FONDO_PANEL   = ("#FFFFFF", "#1E293B")   # tarjetas / paneles
FONDO_SUAVE   = ("#E2E8F0", "#334155")   # zonas secundarias
BORDE         = ("#CBD5E1", "#334155")

# Texto
TEXTO         = ("#0F172A", "#F1F5F9")
TEXTO_TENUE   = ("#475569", "#94A3B8")

# --- Tipografías ----------------------------------------------------------
def fuente(tam=13, peso="normal"):
    return ctk.CTkFont(family="Segoe UI", size=tam, weight=peso)

def fuente_mono(tam=12, peso="normal"):
    return ctk.CTkFont(family="Consolas", size=tam, weight=peso)


# --- Colores para los gráficos de Matplotlib según el modo ----------------
def colores_grafico():
    """Devuelve un diccionario de colores para estilizar las figuras según
    el modo de apariencia (claro/oscuro) actual de CustomTkinter."""
    modo = ctk.get_appearance_mode()  # 'Light' o 'Dark'
    if modo == "Dark":
        return {
            "fondo":   "#1E293B",
            "ejes":    "#1E293B",
            "texto":   "#E2E8F0",
            "grilla":  "#334155",
            "borde":   "#475569",
            "serie1":  "#3B82F6",   # azul (aproximación)
            "serie2":  "#10B981",   # verde (exacta)
            "serie3":  "#F59E0B",   # ámbar (interpolante)
            "punto":   "#EF4444",   # rojo (x0)
            "serie4":  "#8B5CF6",   # violeta
        }
    return {
        "fondo":   "#FFFFFF",
        "ejes":    "#FFFFFF",
        "texto":   "#0F172A",
        "grilla":  "#E2E8F0",
        "borde":   "#CBD5E1",
        "serie1":  "#2563EB",
        "serie2":  "#059669",
        "serie3":  "#D97706",
        "punto":   "#DC2626",
        "serie4":  "#7C3AED",
    }


def estilizar_figura(fig, ejes):
    """Aplica la paleta actual a una figura y sus ejes de Matplotlib."""
    c = colores_grafico()
    fig.patch.set_facecolor(c["fondo"])
    if not isinstance(ejes, (list, tuple)):
        ejes = [ejes]
    for ax in ejes:
        ax.set_facecolor(c["ejes"])
        ax.tick_params(colors=c["texto"], labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(c["borde"])
        ax.xaxis.label.set_color(c["texto"])
        ax.yaxis.label.set_color(c["texto"])
        ax.title.set_color(c["texto"])
        ax.grid(True, color=c["grilla"], linestyle="--", linewidth=0.6, alpha=0.7)
    return c


def estilizar_treeview(estilo):
    """Configura el estilo de un ttk.Treeview (tabla) para que combine con el
    modo de apariencia actual."""
    modo = ctk.get_appearance_mode()
    if modo == "Dark":
        fondo, texto, encab, sel = "#1E293B", "#E2E8F0", "#334155", "#3B82F6"
        fondo_alt = "#243449"
    else:
        fondo, texto, encab, sel = "#FFFFFF", "#0F172A", "#E2E8F0", "#2563EB"
        fondo_alt = "#F1F5F9"

    estilo.theme_use("default")
    estilo.configure("Tabla.Treeview",
                     background=fondo, foreground=texto, fieldbackground=fondo,
                     rowheight=26, borderwidth=0, font=("Consolas", 10))
    estilo.configure("Tabla.Treeview.Heading",
                     background=encab, foreground=texto,
                     relief="flat", font=("Segoe UI", 10, "bold"))
    estilo.map("Tabla.Treeview",
               background=[("selected", sel)],
               foreground=[("selected", "#FFFFFF")])
    estilo.map("Tabla.Treeview.Heading",
               background=[("active", sel)])
    return fondo_alt
