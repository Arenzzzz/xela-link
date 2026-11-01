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
    grafo = Grafo()
    try:
        with open(ruta, encoding="utf-8") as f:
            datos = json.load(f)

        # Poblar nodos: {"arenz": {"nombre": "...", "clave": "..."}, ...}
        for usuario, info in datos.get("usuarios", {}).items():
            grafo.usuarios[usuario] = {"nombre": info["nombre"], "clave": info["clave"]}
            grafo.adyacencia[usuario] = {}

        # Poblar aristas: [["arenz", "luis", 1], ...]
        for u, v, peso in datos.get("amistades", []):
            grafo.adyacencia.setdefault(u, {})[v] = peso
            grafo.adyacencia.setdefault(v, {})[u] = peso

    except FileNotFoundError:
        pass  # Archivo inexistente → grafo vacío

    return grafo


def guardar(grafo, ruta):
    """Serializa el grafo al formato de usuarios.json (cada amistad una sola vez)."""
    # Usuarios: reconstruir diccionario {"usuario": {"nombre": ..., "clave": ...}}
    usuarios = {
        usuario: {"nombre": info["nombre"], "clave": info["clave"]}
        for usuario, info in grafo.usuarios.items()
    }

    # Amistades: recorrer adyacencia y guardar solo cuando u < v (evita duplicados)
    amistades = [
        [u, v, peso]
        for u, vecinos in grafo.adyacencia.items()
        for v, peso in vecinos.items()
        if u < v
    ]

    datos = {"usuarios": usuarios, "amistades": amistades}

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
