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

    # ---- amistades (aristas / transiciones) ----
    def agregar_amistad(self, u, v, peso):
        """ Crea una amistad entre u y v con un nivel de cercanía (peso) """
        """ Como la amistad es mutua, se guarda en ambos sentidos: δ(u, v) = v y δ(v, u) = u """

        u, v = self._normalizar(u), self._normalizar(v)

        # Validaciones antes de crear la amistad
        if u not in self.usuarios or v not in self.usuarios:
            return False, ">> Ese usuario no existe."

        if u == v:
            return False, ">> No puedes agregarte a ti mismo."

        if self.son_amigos(u, v):
            return False, ">> Ya son amigos."

        if peso not in CERCANIA:
            return False, ">> El nivel de cercanía debe ser 1, 2 o 3."

        # Se guarda la transición en los dos sentidos con el mismo peso
        self.adyacencia[u][v] = peso
        self.adyacencia[v][u] = peso

        return True, f"{v} agregado como {CERCANIA[peso].lower()}"

    def eliminar_amistad(self, u, v):
        """ Elimina la amistad en ambos sentidos """

        u, v = self._normalizar(u), self._normalizar(v)

        if not self.son_amigos(u, v):
            return False

        del self.adyacencia[u][v]
        del self.adyacencia[v][u]

        return True

    def son_amigos(self, u, v):
        """ Responde si existe la transición δ(u, v) """

        return v in self.adyacencia.get(u, {})

    def amigos(self, u):
        """ Devuelve los amigos de u con su peso, ej. {'luis': 1, 'ana': 3} """

        return dict(self.adyacencia.get(self._normalizar(u), {}))

    def peso(self, u, v):
        """ Devuelve w(u, v): el nivel de cercanía entre dos amigos """

        return self.adyacencia[u][v]