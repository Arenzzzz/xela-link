"""Menú principal: Mis amigos, Buscar usuario, Validar cadena, Cerrar sesión.

Responsable: Ángel.
"""
import customtkinter as ctk

from modelo.dijkstra import dijkstra
from modelo.automata import Automata
from interfaz.vista_grafo import dibujar_grafo


class VentanaPrincipal(ctk.CTkToplevel):
    def __init__(self, master, grafo, usuario):
        super().__init__(master)
        self.grafo = grafo
        self.usuario = usuario  # q0
        self.title(f"Xela Link — {usuario}")
        self.geometry("1000x650")
        # TODO Ángel:
        # - Pestaña "Mis amigos": agregar (con cercanía 1-3), eliminar, sugerencias.
        # - Pestaña "Buscar": dijkstra(grafo, usuario, buscado) -> ruta, intermediarios,
        #   peso, tabla de pasos y dibujar_grafo(frame, grafo, ruta).
        #   Sin ruta -> mostrar grafo.sugerencias(usuario).
        # - Pestaña "Validar cadena": Automata(grafo, usuario, destino).validar(cadena).
