"""Menú principal: Mis amigos, Buscar usuario, Validar cadena, Cerrar sesión.

Responsable: Ángel.

Barra lateral con el usuario (q0) y la navegación; a la derecha, la página activa:
- Mis amigos:     agregar (cercanía 1-3), eliminar y sugerencias (amigos de amigos).
- Buscar:         dijkstra(grafo, usuario, buscado) -> ruta, peso, intermediarios,
                  tabla de pasos y dibujo del grafo con la ruta resaltada.
                  Sin ruta -> sugerencias.
- Validar cadena: Automata(grafo, usuario, destino).validar(cadena).
- Cerrar sesión:  regresa al login (VentanaLogin.volver_al_login).
"""
import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from modelo.dijkstra import dijkstra
from modelo.automata import Automata, ERROR
from modelo.grafo import CERCANIA
from interfaz.vista_grafo import dibujar_grafo
from interfaz.login import COLORES, fuente

# Fondo que usa vista_grafo.py (Pedro); la tarjeta del grafo lo comparte para que no se note el borde.
FONDO_GRAFO = "#1e1e2e"

# Color de cada nivel de cercanía (peso de la arista)
COLOR_CERCANIA = {1: "#10B981", 2: "#3B82F6", 3: "#8C98B3"}

# Colores para avatares (se elige uno según el nombre de usuario)
COLORES_AVATAR = ["#10B981", "#3B82F6", "#F59E0B", "#EC4899", "#8B5CF6", "#06B6D4", "#EF4444"]


# ---------------------------------------------------------------- utilidades (sin interfaz)
def iniciales(nombre):
    partes = nombre.split()
    return ((partes[0][0] + (partes[1][0] if len(partes) > 1 else "")) if partes else "?").upper()


def color_avatar(usuario):
    return COLORES_AVATAR[sum(map(ord, usuario)) % len(COLORES_AVATAR)]


def leer_cadena(texto):
    """'luis, maria  carlos' -> ['luis', 'maria', 'carlos'] (acepta comas, espacios o flechas)."""
    for separador in (",", "→", "->", ";"):
        texto = texto.replace(separador, " ")
    return [simbolo.strip().lower() for simbolo in texto.split() if simbolo.strip()]


def formato_distancia(valor):
    return "∞" if valor == float("inf") else str(valor)


def limpiar_mensaje(texto):
    """grafo.agregar_amistad devuelve mensajes como '>> Ya son amigos.'"""
    return texto.removeprefix(">>").strip()


# ---------------------------------------------------------------- piezas reutilizables
def tarjeta(master, **kwargs):
    opciones = dict(fg_color=COLORES["panel"], corner_radius=14, border_width=1,
                    border_color=COLORES["borde"])
    opciones.update(kwargs)
    return ctk.CTkFrame(master, **opciones)


def titulo_tarjeta(master, texto, subtitulo=None):
    caja = ctk.CTkFrame(master, fg_color="transparent")
    ctk.CTkLabel(caja, text=texto, font=fuente(15, "bold"),
                 text_color=COLORES["texto"]).pack(anchor="w")
    if subtitulo:
        ctk.CTkLabel(caja, text=subtitulo, font=fuente(12),
                     text_color=COLORES["texto_suave"]).pack(anchor="w")
    return caja


def avatar(master, usuario, nombre, tamano=38):
    return ctk.CTkLabel(master, text=iniciales(nombre), width=tamano, height=tamano,
                        corner_radius=tamano // 2, fg_color=color_avatar(usuario),
                        text_color="#FFFFFF", font=fuente(max(11, tamano // 3), "bold"))


def insignia(master, texto, color):
    return ctk.CTkLabel(master, text=f"  {texto}  ", height=22, corner_radius=11,
                        fg_color=color, text_color="#FFFFFF", font=fuente(11, "bold"))


def entrada(master, placeholder, **kwargs):
    return ctk.CTkEntry(master, placeholder_text=placeholder, height=40, corner_radius=10,
                        border_width=1, font=fuente(13), fg_color=COLORES["campo"],
                        border_color=COLORES["borde"], text_color=COLORES["texto"], **kwargs)


def combo(master, valores, **kwargs):
    caja = ctk.CTkComboBox(master, values=valores, height=40, corner_radius=10, border_width=1,
                           font=fuente(13), dropdown_font=fuente(13),
                           fg_color=COLORES["campo"], border_color=COLORES["borde"],
                           button_color=COLORES["borde"], button_hover_color=COLORES["acento"],
                           text_color=COLORES["texto"], **kwargs)
    caja.set("")
    return caja


def boton(master, texto, comando, principal=True, **kwargs):
    if principal:
        estilo = dict(fg_color=COLORES["acento"], hover_color=COLORES["acento_hover"],
                      text_color="#FFFFFF")
    else:
        estilo = dict(fg_color="transparent", hover_color=COLORES["borde"], border_width=1,
                      border_color=COLORES["borde"], text_color=COLORES["texto"])
    estilo.update(kwargs)
    return ctk.CTkButton(master, text=texto, command=comando, height=40, corner_radius=10,
                         font=fuente(13, "bold"), **estilo)


def ruta_en_fichas(master, ruta, grafo, color_ficha=None, ultimo_error=False):
    """Dibuja una ruta como fichas: [arenz] →1→ [luis] →2→ [maria] ..."""
    fila = ctk.CTkFrame(master, fg_color="transparent")
    for i, usuario in enumerate(ruta):
        es_error = ultimo_error and i == len(ruta) - 1
        if i > 0:
            anterior = ruta[i - 1]
            peso = grafo.adyacencia.get(anterior, {}).get(usuario)
            flecha = f" →{peso}→ " if peso is not None else "  ✕  "
            ctk.CTkLabel(fila, text=flecha, font=fuente(12, "bold"),
                         text_color=COLORES["error"] if es_error else COLORES["texto_suave"]
                         ).pack(side="left")
        if es_error:
            color = COLORES["error"]
        elif i in (0, len(ruta) - 1):
            color = color_ficha or COLORES["acento"]
        else:
            color = COLORES["borde"]
        ctk.CTkLabel(fila, text=f"  {usuario}  ", height=28, corner_radius=14, fg_color=color,
                     text_color="#FFFFFF", font=fuente(12, "bold")).pack(side="left")
    return fila


# ---------------------------------------------------------------- página: Mis amigos
class PaginaAmigos(ctk.CTkFrame):
    def __init__(self, master, ventana):
        super().__init__(master, fg_color="transparent")
        self.ventana = ventana
        self.grafo = ventana.grafo
        self.usuario = ventana.usuario
        self._confirmando = None  # usuario cuyo botón "Eliminar" espera confirmación

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # --- Agregar amigo ---
        agregar = tarjeta(self)
        agregar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        titulo_tarjeta(agregar, "Agregar amigo",
                       "Elige qué tan cercanos son: ese será el peso de la amistad."
                       ).pack(anchor="w", padx=18, pady=(16, 10))

        fila = ctk.CTkFrame(agregar, fg_color="transparent")
        fila.pack(fill="x", padx=18)
        self.nuevo = combo(fila, [], width=220)
        self.nuevo.pack(side="left")
        self.cercania = ctk.CTkSegmentedButton(
            fila, values=[f"{p} · {CERCANIA[p]}" for p in CERCANIA], height=40,
            font=fuente(12, "bold"), selected_color=COLORES["acento"],
            selected_hover_color=COLORES["acento_hover"], unselected_color=COLORES["campo"],
            unselected_hover_color=COLORES["borde"], fg_color=COLORES["campo"],
            text_color=COLORES["texto"])
        self.cercania.set(f"2 · {CERCANIA[2]}")
        self.cercania.pack(side="left", padx=10)
        boton(fila, "Agregar", self.agregar, width=110).pack(side="left")

        self.mensaje = ctk.CTkLabel(agregar, text="", font=fuente(12), anchor="w")
        self.mensaje.pack(fill="x", padx=18, pady=(6, 12))

        # --- Lista de amigos ---
        lista = tarjeta(self)
        lista.grid(row=1, column=0, sticky="nsew", padx=(0, 7))
        self.titulo_lista = ctk.CTkLabel(lista, text="", font=fuente(15, "bold"),
                                         text_color=COLORES["texto"])
        self.titulo_lista.pack(anchor="w", padx=18, pady=(16, 6))
        self.lista = ctk.CTkScrollableFrame(lista, fg_color="transparent")
        self.lista.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        # --- Sugerencias ---
        sugerencias = tarjeta(self)
        sugerencias.grid(row=1, column=1, sticky="nsew", padx=(7, 0))
        titulo_tarjeta(sugerencias, "Personas que quizá conozcas",
                       "Amigos de tus amigos").pack(anchor="w", padx=18, pady=(16, 6))
        self.sugerencias = ctk.CTkScrollableFrame(sugerencias, fg_color="transparent")
        self.sugerencias.pack(fill="both", expand=True, padx=8, pady=(0, 10))

    # ---- datos ----
    def peso_elegido(self):
        return int(self.cercania.get().split("·")[0])

    def refrescar(self):
        amigos = self.grafo.amigos(self.usuario)
        otros = sorted(u for u in self.grafo.usuarios
                       if u != self.usuario and u not in amigos)
        self.nuevo.configure(values=otros)

        # Lista de amigos ordenada por cercanía y luego por nombre
        for w in self.lista.winfo_children():
            w.destroy()
        self.titulo_lista.configure(text=f"Mis amigos ({len(amigos)})")
        if not amigos:
            ctk.CTkLabel(self.lista, text="Aún no tienes amigos.\nAgrega a alguien arriba o "
                         "usa las sugerencias.", font=fuente(13), justify="center",
                         text_color=COLORES["texto_suave"]).pack(pady=40)
        for amigo, peso in sorted(amigos.items(), key=lambda par: (par[1], par[0])):
            self._fila_amigo(amigo, peso)

        # Sugerencias
        for w in self.sugerencias.winfo_children():
            w.destroy()
        sugeridos = self.grafo.sugerencias(self.usuario)
        if not sugeridos:
            ctk.CTkLabel(self.sugerencias, text="Sin sugerencias por ahora.", font=fuente(13),
                         text_color=COLORES["texto_suave"]).pack(pady=40)
        for candidato, en_comun in sugeridos:
            self._fila_sugerencia(candidato, en_comun)

    def _fila_amigo(self, amigo, peso):
        fila = ctk.CTkFrame(self.lista, fg_color=COLORES["campo"], corner_radius=10)
        fila.pack(fill="x", pady=4, padx=4)
        avatar(fila, amigo, self.grafo.nombre(amigo)).pack(side="left", padx=10, pady=8)

        textos = ctk.CTkFrame(fila, fg_color="transparent")
        textos.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(textos, text=self.grafo.nombre(amigo), font=fuente(13, "bold"),
                     text_color=COLORES["texto"], anchor="w").pack(anchor="w")
        en_comun = self.grafo.amigos_en_comun(self.usuario, amigo)
        detalle = f"@{amigo}" + (f" · {len(en_comun)} en común" if en_comun else "")
        ctk.CTkLabel(textos, text=detalle, font=fuente(11), text_color=COLORES["texto_suave"],
                     anchor="w").pack(anchor="w")

        confirmando = self._confirmando == amigo
        ctk.CTkButton(fila, text="¿Seguro?" if confirmando else "Eliminar", width=84, height=30,
                      corner_radius=8, font=fuente(12, "bold"),
                      fg_color=COLORES["error"] if confirmando else "transparent",
                      hover_color=COLORES["error"], border_width=1, border_color=COLORES["error"],
                      text_color="#FFFFFF" if confirmando else COLORES["error"],
                      command=lambda a=amigo: self.eliminar(a)).pack(side="right", padx=10)
        insignia(fila, f"{peso} · {CERCANIA[peso]}", COLOR_CERCANIA[peso]).pack(side="right")

    def _fila_sugerencia(self, candidato, en_comun):
        fila = ctk.CTkFrame(self.sugerencias, fg_color=COLORES["campo"], corner_radius=10)
        fila.pack(fill="x", pady=4, padx=4)
        avatar(fila, candidato, self.grafo.nombre(candidato), 34).pack(side="left", padx=10, pady=8)

        textos = ctk.CTkFrame(fila, fg_color="transparent")
        textos.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(textos, text=self.grafo.nombre(candidato), font=fuente(13, "bold"),
                     text_color=COLORES["texto"], anchor="w").pack(anchor="w")
        plural = "amigo" if en_comun == 1 else "amigos"
        ctk.CTkLabel(textos, text=f"{en_comun} {plural} en común", font=fuente(11),
                     text_color=COLORES["texto_suave"], anchor="w").pack(anchor="w")

        ctk.CTkButton(fila, text="+", width=32, height=32, corner_radius=16, font=fuente(16, "bold"),
                      fg_color=COLORES["acento"], hover_color=COLORES["acento_hover"],
                      command=lambda c=candidato: self.agregar(c)).pack(side="right", padx=10)

    # ---- acciones ----
    def agregar(self, usuario=None):
        usuario = (usuario or self.nuevo.get()).strip().lower()
        if not usuario:
            return self.avisar("Escribe o elige un usuario.", False)

        peso = self.peso_elegido()
        exito, texto = self.grafo.agregar_amistad(self.usuario, usuario, peso)
        self.avisar(limpiar_mensaje(texto), exito)
        if exito:
            self.nuevo.set("")
            self._confirmando = None
            self.ventana.datos_cambiaron()

    def eliminar(self, amigo):
        # Primer clic pide confirmación; el segundo elimina
        if self._confirmando != amigo:
            self._confirmando = amigo
            return self.refrescar()

        self._confirmando = None
        if self.grafo.eliminar_amistad(self.usuario, amigo):
            self.avisar(f"Ya no eres amigo de {amigo}.", True)
            self.ventana.datos_cambiaron()

    def avisar(self, texto, exito):
        self.mensaje.configure(text=texto, text_color=COLORES["exito"] if exito else COLORES["error"])


# ---------------------------------------------------------------- página: Buscar
class PaginaBuscar(ctk.CTkFrame):
    def __init__(self, master, ventana):
        super().__init__(master, fg_color="transparent")
        self.ventana = ventana
        self.grafo = ventana.grafo
        self.usuario = ventana.usuario
        self.ruta_actual = None
        self.ultimo_resultado = None

        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_rowconfigure(1, weight=1)

        # --- Barra de búsqueda ---
        barra = tarjeta(self)
        barra.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        fila = ctk.CTkFrame(barra, fg_color="transparent")
        fila.pack(fill="x", padx=18, pady=16)
        ctk.CTkLabel(fila, text=f"Desde  @{self.usuario}  hasta", font=fuente(13, "bold"),
                     text_color=COLORES["texto_suave"]).pack(side="left", padx=(0, 10))
        self.buscado = combo(fila, [], width=240)
        self.buscado.pack(side="left")
        boton(fila, "Buscar ruta", self.buscar, width=130).pack(side="left", padx=10)
        boton(fila, "Ver red completa", self.ver_red, principal=False, width=150).pack(side="left")

        # --- Columna izquierda: resultado + tabla de pasos ---
        izquierda = ctk.CTkFrame(self, fg_color="transparent")
        izquierda.grid(row=1, column=0, sticky="nsew", padx=(0, 7))
        izquierda.grid_rowconfigure(1, weight=1)
        izquierda.grid_columnconfigure(0, weight=1)

        self.resultado = tarjeta(izquierda)
        self.resultado.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        pasos = tarjeta(izquierda)
        pasos.grid(row=1, column=0, sticky="nsew")
        titulo_tarjeta(pasos, "Tabla de pasos de Dijkstra",
                       "distancia acumulada (desde quién se llegó)"
                       ).pack(anchor="w", padx=18, pady=(14, 8))
        contenedor = ctk.CTkFrame(pasos, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.tabla = self._crear_tabla(contenedor)

        # --- Columna derecha: grafo ---
        derecha = tarjeta(self, fg_color=FONDO_GRAFO, border_width=0)
        derecha.grid(row=1, column=1, sticky="nsew", padx=(7, 0))
        self.leyenda = ctk.CTkLabel(derecha, text="", font=fuente(12, "bold"), text_color="#cdd6f4")
        self.leyenda.pack(anchor="w", padx=16, pady=(12, 0))
        self.lienzo = tk.Frame(derecha, bg=FONDO_GRAFO)
        self.lienzo.pack(fill="both", expand=True, padx=8, pady=8)

        self._resultado_inicial()

    def _crear_tabla(self, master):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        fondo = self._apply_appearance_mode(COLORES["campo"])
        texto = self._apply_appearance_mode(COLORES["texto"])
        borde = self._apply_appearance_mode(COLORES["borde"])
        panel = self._apply_appearance_mode(COLORES["panel"])
        estilo.configure("Xela.Treeview", background=fondo, fieldbackground=fondo, foreground=texto,
                         rowheight=28, borderwidth=0, font=("Segoe UI", 10))
        estilo.configure("Xela.Treeview.Heading", background=panel, foreground=texto,
                         relief="flat", font=("Segoe UI", 10, "bold"))
        estilo.map("Xela.Treeview", background=[("selected", borde)])
        estilo.map("Xela.Treeview.Heading", background=[("active", borde)])

        tabla = ttk.Treeview(master, style="Xela.Treeview", show="headings")
        barra_x = ctk.CTkScrollbar(master, orientation="horizontal", command=tabla.xview, height=12)
        barra_y = ctk.CTkScrollbar(master, orientation="vertical", command=tabla.yview, width=12)
        tabla.configure(xscrollcommand=barra_x.set, yscrollcommand=barra_y.set)
        tabla.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        tabla.tag_configure("par", background=fondo)
        tabla.tag_configure("impar", background=panel)
        tabla.tag_configure("destino", background=self._apply_appearance_mode(COLORES["acento"]),
                            foreground="#FFFFFF")
        return tabla

    # ---- datos ----
    def refrescar(self):
        self.buscado.configure(values=sorted(u for u in self.grafo.usuarios if u != self.usuario))
        # Si había una búsqueda, se repite con los datos nuevos; si no, se dibuja la red
        if self.ultimo_resultado and self.buscado.get().strip():
            self.buscar()
        else:
            self.ver_red()

    def ver_red(self):
        self.ruta_actual = None
        self.leyenda.configure(text="Red completa · el número en cada arista es el peso")
        dibujar_grafo(self.lienzo, self.grafo)

    # ---- búsqueda ----
    def buscar(self):
        buscado = self.buscado.get().strip().lower()
        if not buscado:
            return self._resultado_mensaje("Elige a quién buscar", "Escribe o selecciona un usuario.")
        if not self.grafo.existe(buscado):
            return self._resultado_mensaje("Ese usuario no existe", f"No hay nadie registrado como «{buscado}».")
        if buscado == self.usuario:
            return self._resultado_mensaje("Ese eres tú", "Busca a otra persona de la red.")

        resultado = dijkstra(self.grafo, self.usuario, buscado)
        self.ultimo_resultado = resultado
        self._llenar_tabla(resultado["pasos"], buscado)

        if resultado["ruta"]:
            self._mostrar_ruta(buscado, resultado)
            self.ruta_actual = resultado["ruta"]
            self.leyenda.configure(text=f"Ruta más corta: {' → '.join(resultado['ruta'])}  "
                                        f"(peso {resultado['peso']})")
            dibujar_grafo(self.lienzo, self.grafo, resultado["ruta"])
        else:
            self._mostrar_sin_ruta(buscado)
            self.ruta_actual = None
            self.leyenda.configure(text=f"No hay ninguna cadena de amistades hasta {buscado}")
            dibujar_grafo(self.lienzo, self.grafo)

    def _limpiar_resultado(self):
        for w in self.resultado.winfo_children():
            w.destroy()

    def _resultado_inicial(self):
        self._resultado_mensaje("Encuentra a cualquiera",
                                "Elige a una persona y te mostramos la cadena de amistades\n"
                                "más corta para llegar a ella (algoritmo de Dijkstra).",
                                color=COLORES["texto"])

    def _resultado_mensaje(self, titulo, texto, color=None):
        self._limpiar_resultado()
        ctk.CTkLabel(self.resultado, text=titulo, font=fuente(16, "bold"),
                     text_color=color or COLORES["error"]).pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkLabel(self.resultado, text=texto, font=fuente(12), justify="left",
                     text_color=COLORES["texto_suave"]).pack(anchor="w", padx=18, pady=(0, 16))

    def _mostrar_ruta(self, buscado, resultado):
        self._limpiar_resultado()
        ruta, peso, intermediarios = resultado["ruta"], resultado["peso"], resultado["intermediarios"]

        cabecera = ctk.CTkFrame(self.resultado, fg_color="transparent")
        cabecera.pack(fill="x", padx=18, pady=(16, 10))
        ctk.CTkLabel(cabecera, text=f"Ruta hasta {self.grafo.nombre(buscado)}",
                     font=fuente(16, "bold"), text_color=COLORES["texto"]).pack(side="left")
        insignia(cabecera, f"Peso total: {peso}", COLORES["acento"]).pack(side="right")

        ruta_en_fichas(self.resultado, ruta, self.grafo).pack(anchor="w", padx=18)

        saltos = len(ruta) - 1
        if intermediarios:
            nombres = ", ".join(f"{self.grafo.nombre(u)} (@{u})" for u in intermediarios)
            texto = f"Intermediarios: {nombres}"
        else:
            texto = "Ya son amigos directos: no hay intermediarios."
        ctk.CTkLabel(self.resultado, text=f"{saltos} {'salto' if saltos == 1 else 'saltos'} · {texto}",
                     font=fuente(12), text_color=COLORES["texto_suave"], wraplength=420,
                     justify="left").pack(anchor="w", padx=18, pady=(10, 16))

    def _mostrar_sin_ruta(self, buscado):
        self._limpiar_resultado()
        ctk.CTkLabel(self.resultado, text=f"No hay conexión con {self.grafo.nombre(buscado)}",
                     font=fuente(16, "bold"), text_color=COLORES["error"]
                     ).pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkLabel(self.resultado, text="Ninguna cadena de amistades llega hasta esa persona.\n"
                     "Amplía tu red con estas sugerencias:", font=fuente(12), justify="left",
                     text_color=COLORES["texto_suave"]).pack(anchor="w", padx=18, pady=(0, 8))

        sugeridos = self.grafo.sugerencias(self.usuario)[:5]
        if not sugeridos:
            ctk.CTkLabel(self.resultado, text="(Sin sugerencias: agrega amigos en «Mis amigos».)",
                         font=fuente(12), text_color=COLORES["texto_suave"]
                         ).pack(anchor="w", padx=18, pady=(0, 16))
            return
        fila = ctk.CTkFrame(self.resultado, fg_color="transparent")
        fila.pack(anchor="w", padx=18, pady=(0, 16))
        for candidato, en_comun in sugeridos:
            ctk.CTkButton(fila, text=f"@{candidato} · {en_comun}", height=28, width=10,
                          corner_radius=14, font=fuente(12, "bold"), fg_color=COLORES["borde"],
                          hover_color=COLORES["acento"], text_color=COLORES["texto"],
                          command=lambda: self.ventana.mostrar("amigos")).pack(side="left", padx=(0, 6))

    def _llenar_tabla(self, pasos, destino):
        usuarios = sorted(self.grafo.usuarios)
        # El origen primero y el destino segundo para que se lean fácil
        usuarios.sort(key=lambda u: (u != self.usuario, u != destino, u))
        columnas = ["paso", "visitado"] + usuarios

        self.tabla.delete(*self.tabla.get_children())
        self.tabla.configure(columns=columnas)
        self.tabla.heading("paso", text="#")
        self.tabla.column("paso", width=40, minwidth=40, anchor="center", stretch=False)
        self.tabla.heading("visitado", text="Visitado")
        self.tabla.column("visitado", width=90, minwidth=80, anchor="w", stretch=False)
        for u in usuarios:
            self.tabla.heading(u, text=u)
            self.tabla.column(u, width=90, minwidth=70, anchor="center", stretch=True)

        for i, paso in enumerate(pasos, start=1):
            fila = [i, paso["visitado"]]
            for u in usuarios:
                distancia = paso["distancias"].get(u, float("inf"))
                previo = paso["previos"].get(u)
                fila.append(formato_distancia(distancia) + (f" ({previo})" if previo else ""))
            etiqueta = "destino" if paso["visitado"] == destino else ("par" if i % 2 else "impar")
            self.tabla.insert("", "end", values=fila, tags=(etiqueta,))


# ---------------------------------------------------------------- página: Validar cadena
class PaginaValidar(ctk.CTkFrame):
    def __init__(self, master, ventana):
        super().__init__(master, fg_color="transparent")
        self.ventana = ventana
        self.grafo = ventana.grafo
        self.usuario = ventana.usuario

        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_rowconfigure(1, weight=1)

        # --- Entrada ---
        formulario = tarjeta(self)
        formulario.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        titulo_tarjeta(formulario, "Autómata A = (Q, Σ, δ, q₀, F, w)",
                       f"q₀ = {self.usuario}   ·   F = {{destino}}   ·   "
                       "δ(u, v) = v si u y v son amigos; si no, q_err"
                       ).pack(anchor="w", padx=18, pady=(16, 10))

        fila = ctk.CTkFrame(formulario, fg_color="transparent")
        fila.pack(fill="x", padx=18)
        ctk.CTkLabel(fila, text="Destino", font=fuente(12, "bold"),
                     text_color=COLORES["texto_suave"]).pack(side="left", padx=(0, 8))
        self.destino = combo(fila, [], width=170)
        self.destino.pack(side="left")
        ctk.CTkLabel(fila, text="Cadena", font=fuente(12, "bold"),
                     text_color=COLORES["texto_suave"]).pack(side="left", padx=(14, 8))
        self.cadena = entrada(fila, "ej. luis, maria, carlos")
        self.cadena.pack(side="left", fill="x", expand=True)
        self.cadena.bind("<Return>", lambda _e: self.validar())
        boton(fila, "Validar", self.validar, width=100).pack(side="left", padx=(10, 0))

        fila2 = ctk.CTkFrame(formulario, fg_color="transparent")
        fila2.pack(fill="x", padx=18, pady=(8, 14))
        ctk.CTkLabel(fila2, text="Escribe los usuarios por los que pasa la ruta, sin incluirte; "
                     "sepáralos con comas o espacios.", font=fuente(11),
                     text_color=COLORES["texto_suave"]).pack(side="left")
        ctk.CTkButton(fila2, text="Usar la ruta más corta", height=26, width=10, corner_radius=8,
                      font=fuente(12, "bold"), fg_color="transparent", hover_color=COLORES["borde"],
                      text_color=COLORES["acento"], command=self.usar_ruta_corta).pack(side="right")

        # --- Resultado ---
        self.resultado = tarjeta(self)
        self.resultado.grid(row=1, column=0, sticky="nsew", padx=(0, 7))

        derecha = tarjeta(self, fg_color=FONDO_GRAFO, border_width=0)
        derecha.grid(row=1, column=1, sticky="nsew", padx=(7, 0))
        self.leyenda = ctk.CTkLabel(derecha, text="Recorrido del autómata sobre la red",
                                    font=fuente(12, "bold"), text_color="#cdd6f4")
        self.leyenda.pack(anchor="w", padx=16, pady=(12, 0))
        self.lienzo = tk.Frame(derecha, bg=FONDO_GRAFO)
        self.lienzo.pack(fill="both", expand=True, padx=8, pady=8)

        self._resultado_inicial()

    def refrescar(self):
        self.destino.configure(values=sorted(u for u in self.grafo.usuarios if u != self.usuario))
        dibujar_grafo(self.lienzo, self.grafo)

    def usar_ruta_corta(self):
        destino = self.destino.get().strip().lower()
        if not self.grafo.existe(destino) or destino == self.usuario:
            return self._mensaje("Elige un destino primero", "Selecciona a quién quieres llegar.")
        ruta = dijkstra(self.grafo, self.usuario, destino)["ruta"]
        if not ruta:
            return self._mensaje("No hay ruta", f"Ninguna cadena llega hasta {destino}.")
        self.cadena.delete(0, "end")
        self.cadena.insert(0, ", ".join(ruta[1:]))
        self.validar()

    def validar(self):
        destino = self.destino.get().strip().lower()
        cadena = leer_cadena(self.cadena.get())
        if not destino:
            return self._mensaje("Falta el destino", "Elige el estado final (F).")
        if not self.grafo.existe(destino):
            return self._mensaje("Destino inválido", f"«{destino}» no es un estado de Q.")
        if not cadena:
            return self._mensaje("Falta la cadena", "Escribe al menos un símbolo.")

        resultado = Automata(self.grafo, self.usuario, destino).validar(cadena)
        self._mostrar(destino, cadena, resultado)

    # ---- dibujo del resultado ----
    def _limpiar(self):
        for w in self.resultado.winfo_children():
            w.destroy()

    def _resultado_inicial(self):
        self._limpiar()
        ctk.CTkLabel(self.resultado, text="¿La cadena es aceptada?", font=fuente(16, "bold"),
                     text_color=COLORES["texto"]).pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkLabel(self.resultado, text="El autómata lee la cadena símbolo por símbolo.\n"
                     "Se acepta si cada paso es una amistad y termina en el destino.",
                     font=fuente(12), justify="left", text_color=COLORES["texto_suave"]
                     ).pack(anchor="w", padx=18)

    def _mensaje(self, titulo, texto):
        self._limpiar()
        ctk.CTkLabel(self.resultado, text=titulo, font=fuente(16, "bold"),
                     text_color=COLORES["error"]).pack(anchor="w", padx=18, pady=(16, 2))
        ctk.CTkLabel(self.resultado, text=texto, font=fuente(12),
                     text_color=COLORES["texto_suave"]).pack(anchor="w", padx=18)

    def _mostrar(self, destino, cadena, resultado):
        self._limpiar()
        aceptada = resultado["aceptada"]
        recorrido = resultado["recorrido"]

        cabecera = ctk.CTkFrame(self.resultado, fg_color="transparent")
        cabecera.pack(fill="x", padx=18, pady=(16, 4))
        insignia(cabecera, "✓  ACEPTADA" if aceptada else "✕  RECHAZADA",
                 COLORES["exito"] if aceptada else COLORES["error"]).pack(side="left")
        if aceptada:
            insignia(cabecera, f"Peso: {resultado['peso']}", COLORES["borde"]).pack(side="left", padx=8)

        # Si falló por una transición inexistente, el último estado es q_err
        fallo_en_transicion = not aceptada and len(recorrido) <= len(cadena)
        estados = recorrido + ([ERROR] if fallo_en_transicion else [])
        ruta_en_fichas(self.resultado, estados, self.grafo,
                       ultimo_error=fallo_en_transicion).pack(anchor="w", padx=18, pady=(10, 6))

        if not aceptada:
            falla = resultado["falla"]
            if fallo_en_transicion:
                simbolo = cadena[len(recorrido) - 1]
                if not self.grafo.existe(simbolo):
                    falla = f"«{simbolo}» no pertenece a Σ (no existe ese usuario)."
                else:
                    falla = f"δ({recorrido[-1]}, {simbolo}) = q_err: {falla}."
            ctk.CTkLabel(self.resultado, text=falla, font=fuente(12, "bold"), wraplength=420,
                         justify="left", text_color=COLORES["error"]).pack(anchor="w", padx=18)

        # Tabla de transiciones leídas
        ctk.CTkLabel(self.resultado, text="Transiciones", font=fuente(13, "bold"),
                     text_color=COLORES["texto"]).pack(anchor="w", padx=18, pady=(14, 4))
        lista = ctk.CTkScrollableFrame(self.resultado, fg_color="transparent", height=140)
        lista.pack(fill="both", expand=True, padx=10, pady=(0, 12))
        acumulado = 0
        for i, simbolo in enumerate(cadena):
            if i >= len(recorrido):
                break
            origen = recorrido[i]
            if i + 1 < len(recorrido):
                peso = self.grafo.peso(origen, simbolo)
                acumulado += peso
                texto = f"δ({origen}, {simbolo}) = {simbolo}     w = {peso}     acumulado = {acumulado}"
                color = COLORES["texto"]
            else:
                texto = f"δ({origen}, {simbolo}) = {ERROR}"
                color = COLORES["error"]
            ctk.CTkLabel(lista, text=texto, font=ctk.CTkFont(family="Consolas", size=12),
                         text_color=color, anchor="w").pack(anchor="w", padx=8, pady=1)

        final = recorrido[-1]
        en_f = "∈ F" if final == destino else "∉ F"
        if fallo_en_transicion:
            texto_final = f"Estado final: {ERROR} ∉ F"
        else:
            texto_final = f"Estado final: {final} {en_f}"
        ctk.CTkLabel(lista, text=texto_final, font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                     text_color=COLORES["exito"] if aceptada else COLORES["error"],
                     anchor="w").pack(anchor="w", padx=8, pady=(6, 0))

        # Grafo con el recorrido resaltado
        self.leyenda.configure(text=f"Recorrido: {' → '.join(recorrido)}"
                                    + ("" if aceptada else "  (rechazada)"))
        dibujar_grafo(self.lienzo, self.grafo, recorrido if len(recorrido) > 1 else None)


# ---------------------------------------------------------------- ventana
class VentanaPrincipal(ctk.CTkToplevel):
    PAGINAS = [
        ("amigos", "◉   Mis amigos", "Mis amigos", "Agrega, elimina y descubre personas."),
        ("buscar", "⌕   Buscar", "Buscar usuario", "La cadena de amistades más corta (Dijkstra)."),
        ("validar", "✓   Validar cadena", "Validar cadena", "¿Una ruta es aceptada por el autómata?"),
    ]

    def __init__(self, master, grafo, usuario):
        super().__init__(master)
        self.grafo = grafo
        self.usuario = usuario  # q0
        self.title(f"Xela Link — {usuario}")
        self.geometry("1180x720")
        self.minsize(1000, 640)
        self.configure(fg_color=COLORES["fondo"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._barra_lateral()

        # Área de contenido: cabecera + página activa
        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.grid(row=0, column=1, sticky="nsew", padx=24, pady=20)
        contenido.grid_columnconfigure(0, weight=1)
        contenido.grid_rowconfigure(1, weight=1)

        cabecera = ctk.CTkFrame(contenido, fg_color="transparent")
        cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        self.titulo = ctk.CTkLabel(cabecera, text="", font=fuente(24, "bold"),
                                   text_color=COLORES["texto"])
        self.titulo.pack(anchor="w")
        self.subtitulo = ctk.CTkLabel(cabecera, text="", font=fuente(13),
                                      text_color=COLORES["texto_suave"])
        self.subtitulo.pack(anchor="w")

        self.paginas = {
            "amigos": PaginaAmigos(contenido, self),
            "buscar": PaginaBuscar(contenido, self),
            "validar": PaginaValidar(contenido, self),
        }
        self._pendientes = set(self.paginas)  # páginas que deben refrescarse al mostrarse
        self.actual = None
        self.mostrar("amigos")

        # CTkToplevel a veces abre detrás de otras ventanas
        self.after(150, self._traer_al_frente)

    # ---- barra lateral ----
    def _barra_lateral(self):
        barra = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLORES["marca"])
        barra.grid(row=0, column=0, sticky="nsw")
        barra.grid_propagate(False)
        barra.grid_rowconfigure(3, weight=1)
        barra.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(barra, text="◆  Xela Link", font=fuente(20, "bold"),
                     text_color="#FFFFFF").grid(row=0, column=0, sticky="w", padx=22, pady=(26, 22))

        # Tarjeta del usuario
        perfil = ctk.CTkFrame(barra, fg_color="#163650", corner_radius=12)
        perfil.grid(row=1, column=0, sticky="ew", padx=14)
        nombre = self.grafo.nombre(self.usuario)
        avatar(perfil, self.usuario, nombre, 42).pack(side="left", padx=12, pady=12)
        textos = ctk.CTkFrame(perfil, fg_color="transparent")
        textos.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(textos, text=nombre, font=fuente(13, "bold"), text_color="#FFFFFF",
                     anchor="w").pack(anchor="w")
        self.resumen = ctk.CTkLabel(textos, text="", font=fuente(11), text_color="#9FB3C8", anchor="w")
        self.resumen.pack(anchor="w")

        # Navegación
        menu = ctk.CTkFrame(barra, fg_color="transparent")
        menu.grid(row=2, column=0, sticky="ew", padx=12, pady=(22, 0))
        self.botones = {}
        for clave, texto, _t, _s in self.PAGINAS:
            b = ctk.CTkButton(menu, text=texto, anchor="w", height=42, corner_radius=10,
                              font=fuente(14, "bold"), fg_color="transparent",
                              hover_color="#163650", text_color="#9FB3C8",
                              command=lambda c=clave: self.mostrar(c))
            b.pack(fill="x", pady=3)
            self.botones[clave] = b

        ctk.CTkButton(barra, text="⏻   Cerrar sesión", anchor="w", height=42, corner_radius=10,
                      font=fuente(14, "bold"), fg_color="transparent", hover_color="#3A1E28",
                      text_color="#F87171", command=self.cerrar_sesion
                      ).grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 20))

        self._actualizar_resumen()

    def _actualizar_resumen(self):
        total = len(self.grafo.amigos(self.usuario))
        self.resumen.configure(text=f"@{self.usuario} · {total} {'amigo' if total == 1 else 'amigos'}")

    # ---- navegación ----
    def mostrar(self, clave):
        if self.actual:
            self.paginas[self.actual].grid_forget()
        self.actual = clave
        self.paginas[clave].grid(row=1, column=0, sticky="nsew")

        for c, b in self.botones.items():
            activo = c == clave
            b.configure(fg_color=COLORES["acento"] if activo else "transparent",
                        text_color="#FFFFFF" if activo else "#9FB3C8")
        for c, _texto, titulo, subtitulo in self.PAGINAS:
            if c == clave:
                self.titulo.configure(text=titulo)
                self.subtitulo.configure(text=subtitulo)

        if clave in self._pendientes:
            self._pendientes.discard(clave)
            self.paginas[clave].refrescar()

    def datos_cambiaron(self):
        """Se llama al agregar/eliminar amistades: todas las páginas se ponen al día."""
        self._actualizar_resumen()
        self._pendientes = set(self.paginas) - {self.actual}
        self.paginas[self.actual].refrescar()

    def _traer_al_frente(self):
        self.lift()
        self.focus_force()

    # ---- sesión ----
    def cerrar_sesion(self):
        if hasattr(self.master, "volver_al_login"):
            self.master.volver_al_login(self)
        else:
            self.destroy()
