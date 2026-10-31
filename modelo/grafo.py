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

    def agregar_usuario(self, usuario, nombre, clave):
        """ Registra un usuario. Devuelve False si está vacío o ya existe """

        usuario = self._normalizar(usuario)

        # No se permite un usuario vacío, sin contraseña o que ya exista
        if not usuario or not clave or usuario in self.usuarios:
            return False

        # Si no se escribió un nombre completo, se usa el nombre de usuario
        self.usuarios[usuario] = {"nombre": (nombre or usuario).strip(), "clave": clave}
        self.adyacencia[usuario] = {}   # Todo usuario nuevo empieza sin anigos (sin transiciones)

        return True

    def existe(self, usuario):
        """ Indica si un usuario ya está registrado """

        return self._normalizar(usuario) in self.usuarios

    def verificar_login(self, usuario, clave):
        """ Validación del inicio de sesión """

        usuario = self._normalizar(usuario)

        return usuario in self.usuarios and self.usuarios[usuario]["clave"] == clave

    def nombre(self, usuario):
        """ Devuelve el nombre completo del usuario """

        return self.usuarios[self._normalizar(usuario)]["nombre"]