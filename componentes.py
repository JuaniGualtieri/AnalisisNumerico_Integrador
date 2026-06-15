# -*- coding: utf-8 -*-
"""
============================================================================
  componentes.py  --  Widgets y ayudantes reutilizables de la interfaz
============================================================================
Funciones para crear tarjetas, campos de entrada etiquetados y tablas
(ttk.Treeview) con un estilo consistente. Se usan en las dos vistas.
============================================================================
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

import tema


class Tarjeta(ctk.CTkFrame):
    """Panel con título, usado para agrupar controles o resultados."""

    def __init__(self, master, titulo="", icono="", **kwargs):
        super().__init__(master, fg_color=tema.FONDO_PANEL,
                         corner_radius=14, border_width=1,
                         border_color=tema.BORDE, **kwargs)
        if titulo:
            cab = ctk.CTkFrame(self, fg_color="transparent")
            cab.pack(fill="x", padx=16, pady=(14, 4))
            texto = f"{icono}  {titulo}" if icono else titulo
            ctk.CTkLabel(cab, text=texto, font=tema.fuente(15, "bold"),
                         text_color=tema.TEXTO, anchor="w").pack(side="left")
            sep = ctk.CTkFrame(self, height=2, fg_color=tema.FONDO_SUAVE)
            sep.pack(fill="x", padx=16, pady=(2, 8))

    def cuerpo(self):
        """Devuelve un contenedor interno con padding para colocar widgets."""
        c = ctk.CTkFrame(self, fg_color="transparent")
        c.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        return c


def campo(master, etiqueta, valor_inicial="", ancho=120, ayuda=""):
    """Crea una fila «etiqueta + entrada» y devuelve el CTkEntry."""
    fila = ctk.CTkFrame(master, fg_color="transparent")
    fila.pack(fill="x", pady=5)
    lab = ctk.CTkLabel(fila, text=etiqueta, font=tema.fuente(13),
                       text_color=tema.TEXTO, anchor="w")
    lab.pack(side="left")
    ent = ctk.CTkEntry(fila, width=ancho, font=tema.fuente_mono(12),
                       justify="right")
    ent.pack(side="right")
    if valor_inicial != "":
        ent.insert(0, str(valor_inicial))
    if ayuda:
        Tooltip(lab, ayuda)
        Tooltip(ent, ayuda)
    return ent


def boton(master, texto, comando, color=None, hover=None, ancho=140, icono=""):
    """Crea un CTkButton estilizado."""
    return ctk.CTkButton(
        master, text=(f"{icono}  {texto}" if icono else texto),
        command=comando, width=ancho, height=38,
        font=tema.fuente(13, "bold"), corner_radius=10,
        fg_color=color or tema.ACENTO, hover_color=hover or tema.ACENTO_HOVER,
    )


class Tabla(ctk.CTkFrame):
    """Tabla con encabezados, basada en ttk.Treeview, con scrollbars y filas
    alternadas. Pensada para mostrar pasos / iteraciones."""

    def __init__(self, master, columnas, anchos=None, altura=10, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.columnas = columnas
        self.estilo = ttk.Style()
        self.fondo_alt = tema.estilizar_treeview(self.estilo)

        cont = tk.Frame(self, bg=self._fondo_actual())
        cont.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(cont, columns=columnas, show="headings",
                                 style="Tabla.Treeview", height=altura)
        anchos = anchos or [max(70, 700 // len(columnas))] * len(columnas)
        for col, an in zip(columnas, anchos):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=an, anchor="center", stretch=True)

        vsb = ttk.Scrollbar(cont, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(cont, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        cont.grid_rowconfigure(0, weight=1)
        cont.grid_columnconfigure(0, weight=1)

        self.tree.tag_configure("par", background=self._fondo_actual())
        self.tree.tag_configure("impar", background=self.fondo_alt)

    def _fondo_actual(self):
        modo = ctk.get_appearance_mode()
        return "#1E293B" if modo == "Dark" else "#FFFFFF"

    def cargar(self, filas):
        """Reemplaza el contenido por la lista de filas (cada fila = tupla)."""
        self.tree.delete(*self.tree.get_children())
        for i, fila in enumerate(filas):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=fila, tags=(tag,))

    def refrescar_tema(self):
        self.fondo_alt = tema.estilizar_treeview(self.estilo)
        self.tree.tag_configure("par", background=self._fondo_actual())
        self.tree.tag_configure("impar", background=self.fondo_alt)


class Tooltip:
    """Globo de ayuda que aparece al pasar el mouse sobre un widget."""

    def __init__(self, widget, texto, retardo=450):
        self.widget = widget
        self.texto = texto
        self.retardo = retardo
        self.tip = None
        self._after = None
        widget.bind("<Enter>", self._programar)
        widget.bind("<Leave>", self._ocultar)
        widget.bind("<ButtonPress>", self._ocultar)

    def _programar(self, _=None):
        self._cancelar()
        self._after = self.widget.after(self.retardo, self._mostrar)

    def _cancelar(self):
        if self._after:
            self.widget.after_cancel(self._after)
            self._after = None

    def _mostrar(self):
        if self.tip or not self.texto:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        modo = ctk.get_appearance_mode()
        bg = "#334155" if modo == "Dark" else "#1E293B"
        lbl = tk.Label(self.tip, text=self.texto, justify="left",
                       background=bg, foreground="#FFFFFF",
                       relief="solid", borderwidth=0,
                       font=("Segoe UI", 9), padx=10, pady=6, wraplength=320)
        lbl.pack()

    def _ocultar(self, _=None):
        self._cancelar()
        if self.tip:
            self.tip.destroy()
            self.tip = None
