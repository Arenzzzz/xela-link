"""Ventana de login y registro (CustomTkinter).

Responsable: Ángel.
"""
import customtkinter as ctk


class VentanaLogin(ctk.CTk):
    def __init__(self, grafo):
        super().__init__()
        self.grafo = grafo
        self.title("Xela Link — Iniciar sesión")
        self.geometry("400x420")
        # TODO Ángel: campos usuario/clave, botones "Entrar" y "Registrarse".
        # Al entrar: usar grafo.verificar_login(...) y abrir VentanaPrincipal(self, grafo, usuario).
