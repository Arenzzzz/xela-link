"""Ventana de login y registro (CustomTkinter).

Responsable: Ángel.

Pantalla dividida en dos:
- Izquierda: panel de marca con una mini red de amistades y una ruta resaltada
  (guiño a Dijkstra / al autómata).
- Derecha: formulario que cambia entre "Iniciar sesión" y "Crear cuenta".

Al entrar se oculta el login y se abre VentanaPrincipal(self, grafo, usuario).
Para cerrar sesión desde la ventana principal: self.master.volver_al_login(self)
"""
import customtkinter as ctk

# ---------------------------------------------------------------- tema
# Paleta oscura con verde quetzal como acento. Cada color es (modo claro, modo oscuro).
COLORES = {
    "fondo": ("#F4F6FB", "#0B1120"),
    "panel": ("#FFFFFF", "#111A2E"),
    "marca": ("#0F2A3D", "#0E2236"),
    "borde": ("#D5DBE7", "#22304A"),
    "texto": ("#0F172A", "#E6EBF5"),
    "texto_suave": ("#5B6478", "#8C98B3"),
    "acento": ("#0E9F6E", "#10B981"),
    "acento_hover": ("#0B7F58", "#0E9F6E"),
    "error": ("#DC2626", "#F87171"),
    "exito": ("#0E9F6E", "#34D399"),
    "campo": ("#F8FAFD", "#0D1526"),
}

FUENTE = "Segoe UI"  # en Linux/Mac Tk usa una equivalente si no existe

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


def fuente(tamano, peso="normal"):
    return ctk.CTkFont(family=FUENTE, size=tamano, weight=peso)


# ---------------------------------------------------------------- panel de marca
class PanelMarca(ctk.CTkFrame):
    """Panel izquierdo: logo, eslogan y una mini red dibujada en un Canvas."""

    # Nodos de adorno (x, y en proporción 0-1) y aristas; la ruta va resaltada.
    NODOS = {
        "A": (0.18, 0.30), "B": (0.45, 0.18), "C": (0.78, 0.28),
        "D": (0.30, 0.62), "E": (0.62, 0.55), "F": (0.85, 0.78),
        "G": (0.48, 0.86),
    }
    ARISTAS = [("A", "B"), ("B", "C"), ("A", "D"), ("D", "E"), ("B", "E"),
               ("E", "F"), ("C", "F"), ("D", "G"), ("G", "F"), ("E", "C")]
    RUTA = ["A", "D", "E", "F"]

    def __init__(self, master):
        super().__init__(master, fg_color=COLORES["marca"], corner_radius=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.grid(row=0, column=0, sticky="nw", padx=36, pady=(40, 0))

        ctk.CTkLabel(cabecera, text="◆  Xela Link", font=fuente(26, "bold"),
                     text_color="#FFFFFF").pack(anchor="w")
        ctk.CTkLabel(cabecera, text="La cadena de amistades más corta\nentre tú y cualquier persona.",
                     font=fuente(14), text_color="#9FB3C8", justify="left").pack(anchor="w", pady=(10, 0))

        # Canvas de Tk (CustomTkinter no trae uno propio)
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0, bd=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=24, pady=10)
        self.canvas.bind("<Configure>", lambda _e: self._dibujar())

        ctk.CTkLabel(self, text="Lenguajes Formales y Autómatas · URL Quetzaltenango",
                     font=fuente(11), text_color="#6F86A0").grid(row=2, column=0, sticky="sw",
                                                                 padx=36, pady=(0, 24))

    def _dibujar(self):
        c = self.canvas
        c.configure(bg=self._apply_appearance_mode(COLORES["marca"]))
        c.delete("all")
        ancho, alto = c.winfo_width(), c.winfo_height()
        if ancho < 50 or alto < 50:
            return
        pos = {n: (x * ancho, y * alto) for n, (x, y) in self.NODOS.items()}
        en_ruta = {frozenset(par) for par in zip(self.RUTA, self.RUTA[1:])}

        for u, v in self.ARISTAS:
            (x1, y1), (x2, y2) = pos[u], pos[v]
            resaltada = frozenset((u, v)) in en_ruta
            c.create_line(x1, y1, x2, y2,
                          fill="#10B981" if resaltada else "#2B4A63",
                          width=3 if resaltada else 1.5)

        for nodo, (x, y) in pos.items():
            r = 13 if nodo in self.RUTA else 9
            if nodo in (self.RUTA[0], self.RUTA[-1]):  # origen y destino con halo
                c.create_oval(x - r - 7, y - r - 7, x + r + 7, y + r + 7, outline="#10B981", width=1)
            c.create_oval(x - r, y - r, x + r, y + r,
                          fill="#10B981" if nodo in self.RUTA else "#3A5A75", outline="")


# ---------------------------------------------------------------- piezas del formulario
class Campo(ctk.CTkFrame):
    """Etiqueta + entrada. Si es contraseña, agrega botón para mostrarla."""

    def __init__(self, master, etiqueta, placeholder="", clave=False):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text=etiqueta, font=fuente(12, "bold"),
                     text_color=COLORES["texto_suave"]).pack(anchor="w", pady=(0, 4))

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x")
        self.entrada = ctk.CTkEntry(fila, placeholder_text=placeholder, height=42,
                                    font=fuente(14), corner_radius=10, border_width=1,
                                    fg_color=COLORES["campo"], border_color=COLORES["borde"],
                                    text_color=COLORES["texto"], show="•" if clave else "")
        self.entrada.pack(side="left", fill="x", expand=True)

        self._clave = clave
        if clave:
            self.boton_ojo = ctk.CTkButton(fila, text="Ver", width=52, height=42, corner_radius=10,
                                           font=fuente(12), fg_color=COLORES["campo"],
                                           hover_color=COLORES["borde"], border_width=1,
                                           border_color=COLORES["borde"],
                                           text_color=COLORES["texto_suave"],
                                           command=self._alternar)
            self.boton_ojo.pack(side="left", padx=(6, 0))

    def _alternar(self):
        oculta = self.entrada.cget("show") == "•"
        self.entrada.configure(show="" if oculta else "•")
        self.boton_ojo.configure(text="Ocultar" if oculta else "Ver")

    def valor(self):
        return self.entrada.get()

    def limpiar(self):
        self.entrada.delete(0, "end")

    def poner(self, texto):
        self.limpiar()
        self.entrada.insert(0, texto)

    def marcar_error(self, hay_error):
        self.entrada.configure(border_color=COLORES["error"] if hay_error else COLORES["borde"])


def boton_principal(master, texto, comando):
    return ctk.CTkButton(master, text=texto, command=comando, height=44, corner_radius=10,
                         font=fuente(14, "bold"), fg_color=COLORES["acento"],
                         hover_color=COLORES["acento_hover"], text_color="#FFFFFF")


def enlace(master, pregunta, texto, comando):
    fila = ctk.CTkFrame(master, fg_color="transparent")
    ctk.CTkLabel(fila, text=pregunta, font=fuente(12),
                 text_color=COLORES["texto_suave"]).pack(side="left")
    ctk.CTkButton(fila, text=texto, command=comando, width=10, height=24,
                  fg_color="transparent", hover_color=COLORES["panel"], font=fuente(12, "bold"),
                  text_color=COLORES["acento"]).pack(side="left", padx=(4, 0))
    return fila


# ---------------------------------------------------------------- formularios
class FormularioLogin(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="Bienvenido de vuelta", font=fuente(24, "bold"),
                     text_color=COLORES["texto"]).pack(anchor="w")
        ctk.CTkLabel(self, text="Inicia sesión para ver tu red.", font=fuente(13),
                     text_color=COLORES["texto_suave"]).pack(anchor="w", pady=(4, 26))

        self.usuario = Campo(self, "Usuario", "ej. arenz")
        self.usuario.pack(fill="x", pady=(0, 14))
        self.clave = Campo(self, "Contraseña", "••••", clave=True)
        self.clave.pack(fill="x")

        self.mensaje = ctk.CTkLabel(self, text="", font=fuente(12), anchor="w",
                                    text_color=COLORES["error"])
        self.mensaje.pack(fill="x", pady=(10, 6))

        boton_principal(self, "Entrar", self.entrar).pack(fill="x")
        enlace(self, "¿No tienes cuenta?", "Regístrate",
               self.app.mostrar_registro).pack(pady=(18, 0))

    def entrar(self):
        usuario, clave = self.usuario.valor().strip(), self.clave.valor()
        self.usuario.marcar_error(not usuario)
        self.clave.marcar_error(not clave)

        if not usuario or not clave:
            return self.avisar("Escribe tu usuario y contraseña.")

        if not self.app.grafo.verificar_login(usuario, clave):
            self.clave.marcar_error(True)
            self.clave.limpiar()
            return self.avisar("Usuario o contraseña incorrectos.")

        self.avisar("")
        self.clave.limpiar()
        self.app.abrir_principal(usuario.lower())

    def avisar(self, texto, exito=False):
        self.mensaje.configure(text=texto,
                               text_color=COLORES["exito"] if exito else COLORES["error"])

    def enfocar(self):
        (self.clave if self.usuario.valor() else self.usuario).entrada.focus_set()


class FormularioRegistro(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="Crea tu cuenta", font=fuente(24, "bold"),
                     text_color=COLORES["texto"]).pack(anchor="w")
        ctk.CTkLabel(self, text="Únete a la red y empieza a conectar.", font=fuente(13),
                     text_color=COLORES["texto_suave"]).pack(anchor="w", pady=(4, 20))

        self.nombre = Campo(self, "Nombre completo", "ej. Ana López")
        self.nombre.pack(fill="x", pady=(0, 12))
        self.usuario = Campo(self, "Usuario", "sin espacios, ej. ana")
        self.usuario.pack(fill="x", pady=(0, 12))

        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x")
        fila.grid_columnconfigure((0, 1), weight=1, uniform="c")
        self.clave = Campo(fila, "Contraseña", "mín. 4 caracteres", clave=True)
        self.clave.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.confirmar = Campo(fila, "Confirmar", "repítela", clave=True)
        self.confirmar.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.mensaje = ctk.CTkLabel(self, text="", font=fuente(12), anchor="w",
                                    text_color=COLORES["error"])
        self.mensaje.pack(fill="x", pady=(10, 6))

        boton_principal(self, "Crear cuenta", self.registrar).pack(fill="x")
        enlace(self, "¿Ya tienes cuenta?", "Inicia sesión",
               self.app.mostrar_login).pack(pady=(16, 0))

    def registrar(self):
        nombre = self.nombre.valor().strip()
        usuario = self.usuario.valor().strip()
        clave, confirmar = self.clave.valor(), self.confirmar.valor()

        for campo in (self.nombre, self.usuario, self.clave, self.confirmar):
            campo.marcar_error(False)

        error, campo_malo = self._validar(nombre, usuario, clave, confirmar)
        if error:
            campo_malo.marcar_error(True)
            return self.avisar(error)

        if not self.app.grafo.agregar_usuario(usuario, nombre, clave):
            self.usuario.marcar_error(True)
            return self.avisar("No se pudo registrar. Revisa los datos.")

        for campo in (self.nombre, self.usuario, self.clave, self.confirmar):
            campo.limpiar()
        self.avisar("")
        self.app.mostrar_login(usuario=usuario.lower(),
                               aviso=f"Cuenta creada. ¡Bienvenido, {nombre.split()[0]}!")

    def _validar(self, nombre, usuario, clave, confirmar):
        if not nombre:
            return "Escribe tu nombre completo.", self.nombre
        if not usuario:
            return "Elige un nombre de usuario.", self.usuario
        if " " in usuario:
            return "El usuario no puede llevar espacios.", self.usuario
        if self.app.grafo.existe(usuario):
            return f"El usuario «{usuario.lower()}» ya está en uso.", self.usuario
        if len(clave) < 4:
            return "La contraseña debe tener al menos 4 caracteres.", self.clave
        if clave != confirmar:
            return "Las contraseñas no coinciden.", self.confirmar
        return None, None

    def avisar(self, texto):
        self.mensaje.configure(text=texto)

    def enfocar(self):
        self.nombre.entrada.focus_set()


# ---------------------------------------------------------------- ventana
class VentanaLogin(ctk.CTk):
    def __init__(self, grafo):
        super().__init__()
        self.grafo = grafo
        self.title("Xela Link — Iniciar sesión")
        self.geometry("900x560")
        self.minsize(780, 520)
        self.configure(fg_color=COLORES["fondo"])
        self.principal = None

        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=6)
        self.grid_rowconfigure(0, weight=1)

        PanelMarca(self).grid(row=0, column=0, sticky="nsew")

        # Lado derecho: tarjeta centrada que contiene el formulario activo
        lado = ctk.CTkFrame(self, fg_color=COLORES["fondo"], corner_radius=0)
        lado.grid(row=0, column=1, sticky="nsew")
        tarjeta = ctk.CTkFrame(lado, fg_color="transparent")
        tarjeta.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.78)

        self.form_login = FormularioLogin(tarjeta, self)
        self.form_registro = FormularioRegistro(tarjeta, self)
        self.bind("<Return>", self._enter)

        self.mostrar_login()
        self._centrar()

    # ---- navegación entre formularios ----
    def mostrar_login(self, usuario=None, aviso=None):
        self.form_registro.pack_forget()
        self.form_login.pack(fill="x")
        self.title("Xela Link — Iniciar sesión")
        if usuario:
            self.form_login.usuario.poner(usuario)
        self.form_login.avisar(aviso or "", exito=bool(aviso))
        self.after(50, self.form_login.enfocar)

    def mostrar_registro(self):
        self.form_login.pack_forget()
        self.form_registro.pack(fill="x")
        self.title("Xela Link — Crear cuenta")
        self.after(50, self.form_registro.enfocar)

    def _enter(self, _evento):
        if self.form_login.winfo_ismapped():
            self.form_login.entrar()
        elif self.form_registro.winfo_ismapped():
            self.form_registro.registrar()

    # ---- sesión ----
    def abrir_principal(self, usuario):
        # Import aquí para que el login funcione aunque la principal aún esté en construcción
        from interfaz.ventana_principal import VentanaPrincipal

        self.withdraw()
        self.principal = VentanaPrincipal(self, self.grafo, usuario)
        # Cerrar la ventana principal con la X cierra toda la app (main.py guarda al salir)
        self.principal.protocol("WM_DELETE_WINDOW", self.destroy)

    def volver_al_login(self, ventana=None):
        """Llamar desde el botón 'Cerrar sesión' de la ventana principal."""
        (ventana or self.principal).destroy()
        self.principal = None
        self.deiconify()
        self.mostrar_login(aviso="Sesión cerrada.")

    def _centrar(self):
        self.update_idletasks()
        ancho, alto = 900, 560
        x = (self.winfo_screenwidth() - ancho) // 2
        y = (self.winfo_screenheight() - alto) // 3
        self.geometry(f"{ancho}x{alto}+{x}+{y}")


# ---------------------------------------------------------------- prueba rápida
if __name__ == "__main__":
    # Probar solo el login sin depender de gestor_json:  python -m interfaz.login
    from modelo.grafo import Grafo

    g = Grafo()
    g.agregar_usuario("arenz", "Arenz Peláez", "1234")
    g.agregar_usuario("ana", "Ana López", "1234")
    VentanaLogin(g).mainloop()
