"""Punto de entrada de Xela Link.

Responsable: Arenz (integración).
"""
from modelo.grafo import Grafo
from datos.gestor_json import cargar, guardar
from interfaz.login import VentanaLogin

RUTA_DATOS = "datos/usuarios.json"


def main():
    grafo = cargar(RUTA_DATOS)          # devuelve un Grafo con usuarios y amistades
    app = VentanaLogin(grafo)           # el login abre la ventana principal al entrar
    app.mainloop()
    guardar(grafo, RUTA_DATOS)          # guarda los cambios al cerrar


if __name__ == "__main__":
    main()
