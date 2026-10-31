""" Grafo no dirigido y ponderado de usuarios y amistades """
""" Cada usuario es un estado (Q) y cada amistad una transición (δ) con su peso (w) """

CERCANIA = {1: "Mejor amigo", 2: "Amigo", 3: "Conocido"}    # Asociación de peso del usuario con su nombre

class Grafo:
    def __init__(self):
        self.usuarios = {}      # {"arenz": "Arenz Peláez", "clave": "1234"}
        self.adyacencia = {}    # Lista de adyacencia: {"arenz": {"luis": 1, "ana": 3}}

    # ---- usuarios (nodos / estados) ----
    @staticmethod
    def _normalizar(usuario):
        """ Los usuarios se guardan en minúsculas y sin espacios a los lados """

        return (usuario or "").strip().lower()