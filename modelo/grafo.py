"""Grafo no dirigido y ponderado de usuarios y amistades.

Responsable: Arenz.
Peso de cada amistad = nivel de cercanía (1 mejor amigo, 2 amigo, 3 conocido).
"""

CERCANIA = {1: "Mejor amigo", 2: "Amigo", 3: "Conocido"}


class Grafo:
    def __init__(self):
        # {"arenz": {"nombre": "Arenz Peláez", "clave": "1234"}}
        self.usuarios = {}
        # {"arenz": {"luis": 1, "ana": 3}}  (lista de adyacencia)
        self.adyacencia = {}

    # ---------- usuarios (nodos / estados) ----------
    def agregar_usuario(self, usuario, nombre, clave):
        """Devuelve False si el usuario ya existe."""
        # TODO Arenz
        raise NotImplementedError

    def existe(self, usuario):
        return usuario in self.usuarios

    def verificar_login(self, usuario, clave):
        # TODO Arenz
        raise NotImplementedError

    # ---------- amistades (aristas / transiciones) ----------
    def agregar_amistad(self, u, v, peso):
        """Crea la arista u-v en ambos sentidos. Valida: existen, u != v, no duplicada, peso 1-3."""
        # TODO Arenz
        raise NotImplementedError

    def eliminar_amistad(self, u, v):
        # TODO Arenz
        raise NotImplementedError

    def son_amigos(self, u, v):
        return v in self.adyacencia.get(u, {})

    def amigos(self, u):
        """Devuelve {amigo: peso}."""
        return dict(self.adyacencia.get(u, {}))

    def peso(self, u, v):
        return self.adyacencia[u][v]

    def sugerencias(self, u):
        """Amigos de amigos que aún no son amigos de u ("Conocer personas")."""
        # TODO Arenz
        raise NotImplementedError
