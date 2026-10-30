"""Guardar y cargar el grafo en JSON.

Responsable: Pedro.
Formato de usuarios.json:
{
  "usuarios": {"arenz": {"nombre": "...", "clave": "..."}},
  "amistades": [["arenz", "luis", 1], ...]
}
"""
import json

from modelo.grafo import Grafo


def cargar(ruta):
    """Devuelve un Grafo. Si el archivo no existe, devuelve un Grafo vacío."""
    # TODO Pedro
    raise NotImplementedError


def guardar(grafo, ruta):
    # TODO Pedro (cada amistad se guarda una sola vez)
    raise NotImplementedError
