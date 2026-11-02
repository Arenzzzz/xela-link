"""Dibujo del grafo con NetworkX + Matplotlib dentro de un frame de CustomTkinter.

Responsable: Pedro.
"""
import math
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ── Paleta adaptada a CustomTkinter ──────────────────────────────────────────
_BG          = "#1e1e2e"
_NODE_DEF    = "#7c83fd"
_NODE_RUTA   = "#f38ba8"
_EDGE_DEF    = "#45475a"
_EDGE_RUTA   = "#f38ba8"
_LABEL_COLOR = "#cdd6f4"
_LABEL_BG    = "#181825"
_WEIGHT_DEF  = "#a6adc8"
_WEIGHT_RUTA = "#f38ba8"
_WEIGHT_BG   = "#11111b"

# ── Constantes visuales ───────────────────────────────────────────────────────
_NODE_SIZE      = 600      # points²  para nodos normales
_NODE_SIZE_RUTA = 750      # points²  para nodos de la ruta
_FIG_W, _FIG_H  = 7.8, 6.6   # pulgadas
_DPI            = 100


# ── Cálculo de layout ordenado con separación física ─────────────────────────

def _obtener_posiciones_ordenadas(G):
    """Calcula posiciones para los nodos donde:
    1. Se maximiza el espacio entre nodos para evitar amontonamiento.
    2. Se aplica una relajación que empuja a los nodos lejos del trayecto
       de las aristas, logrando que la gran mayoría de aristas sean rectas
       y que ninguna pase por encima ni por debajo de ningún nodo.
    """
    n = len(G)
    if n == 0:
        return {}

    # Layout inicial amplio: k alto para forzar repulsión entre nodos
    k_inicial = max(0.85, 3.0 / math.sqrt(n))
    pos_base = nx.spring_layout(G, seed=42, k=k_inicial, iterations=300, scale=2.5)

    coords = {nodo: [float(p[0]), float(p[1])] for nodo, p in pos_base.items()}
    nodos = list(G.nodes())
    aristas = list(G.edges())

    # Distancias de seguridad en unidades del layout
    d_seguridad_arista = 0.35  # margen para que las aristas no toquen los nodos
    d_min_nodos        = 0.45  # margen entre centros de dos nodos vecinos

    # Relajación física en 60 pasos
    for paso in range(60):
        factor_fuerza = 0.5 * (1.0 - (paso / 75.0))

        # A) Repulsión entre nodos para evitar que se peguen
        for i in range(len(nodos)):
            u = nodos[i]
            pu = coords[u]
            for j in range(i + 1, len(nodos)):
                v = nodos[j]
                pv = coords[v]
                dx = pv[0] - pu[0]
                dy = pv[1] - pu[1]
                dist = math.hypot(dx, dy)
                if dist < d_min_nodos:
                    if dist < 1e-6:
                        dx, dy, dist = 0.01, 0.0, 0.01
                    solapamiento = d_min_nodos - dist
                    empuje = factor_fuerza * solapamiento * 0.5
                    ux = (dx / dist) * empuje
                    uy = (dy / dist) * empuje
                    pu[0] -= ux
                    pu[1] -= uy
                    pv[0] += ux
                    pv[1] += uy

        # B) Repulsión nodo-arista: empujar nodos perpendiculares a las aristas
        for u, v in aristas:
            p0 = coords[u]
            p1 = coords[v]
            dx = p1[0] - p0[0]
            dy = p1[1] - p0[1]
            L2 = dx * dx + dy * dy
            if L2 < 1e-6:
                continue
            L = math.sqrt(L2)

            for w in nodos:
                if w == u or w == v:
                    continue
                pw = coords[w]
                t = ((pw[0] - p0[0]) * dx + (pw[1] - p0[1]) * dy) / L2
                if 0.03 < t < 0.97:
                    proj_x = p0[0] + t * dx
                    proj_y = p0[1] + t * dy
                    dist_x = pw[0] - proj_x
                    dist_y = pw[1] - proj_y
                    dist = math.hypot(dist_x, dist_y)

                    if dist < d_seguridad_arista:
                        solapamiento = d_seguridad_arista - dist
                        empuje = factor_fuerza * solapamiento
                        if dist > 1e-6:
                            norm_x = dist_x / dist
                            norm_y = dist_y / dist
                        else:
                            norm_x = -dy / L
                            norm_y = dx / L

                        pw[0] += norm_x * empuje * 0.7
                        pw[1] += norm_y * empuje * 0.7
                        p0[0] -= norm_x * empuje * 0.15
                        p0[1] -= norm_y * empuje * 0.15
                        p1[0] -= norm_x * empuje * 0.15
                        p1[1] -= norm_y * empuje * 0.15

    return {n: (coords[n][0], coords[n][1]) for n in nodos}


# ── Detección de colisiones y cálculo de curvatura ───────────────────────────

def _dist_punto_a_segmento(p0, p1, q):
    """Distancia mínima euclídea del punto q al segmento p0→p1."""
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    L2 = dx * dx + dy * dy
    if L2 < 1e-9:
        return math.hypot(q[0] - p0[0], q[1] - p0[1])
    t = max(0.0, min(1.0, ((q[0] - p0[0]) * dx + (q[1] - p0[1]) * dy) / L2))
    return math.hypot(q[0] - (p0[0] + t * dx), q[1] - (p0[1] + t * dy))


def _dist_punto_a_curva(p0, p1, rad, q, n_muestras=24):
    """Distancia mínima del punto q al arco arc3 de matplotlib."""
    x12 = (p0[0] + p1[0]) / 2.0
    y12 = (p0[1] + p1[1]) / 2.0
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    ctrl_x = x12 + rad * dy
    ctrl_y = y12 - rad * dx

    d_min = float("inf")
    for i in range(1, n_muestras):
        t = i / float(n_muestras)
        mt = 1.0 - t
        bx = mt * mt * p0[0] + 2.0 * mt * t * ctrl_x + t * t * p1[0]
        by = mt * mt * p0[1] + 2.0 * mt * t * ctrl_y + t * t * p1[1]
        dist = math.hypot(bx - q[0], by - q[1])
        if dist < d_min:
            d_min = dist
    return d_min


def _evaluar_arista(u, v, pos, nodos, radio_seguridad):
    """Determina si la arista puede ser recta (rad=0.0) o si requiere curvatura
    para evitar pasar por encima de algún nodo intermedio.
    """
    p0 = pos[u]
    p1 = pos[v]
    intermedios = [pos[n] for n in nodos if n != u and n != v]
    if not intermedios:
        return 0.0

    # 1. Verificar si la línea recta es segura
    recta_segura = True
    for q in intermedios:
        d_p0 = math.hypot(q[0] - p0[0], q[1] - p0[1])
        d_p1 = math.hypot(q[0] - p1[0], q[1] - p1[1])
        # Solo comprobar nodos que no sean los propios extremos
        if d_p0 > radio_seguridad * 0.9 and d_p1 > radio_seguridad * 0.9:
            if _dist_punto_a_segmento(p0, p1, q) < radio_seguridad:
                recta_segura = False
                break

    if recta_segura:
        return 0.0

    # 2. Si hay colisión con recta, probar curvaturas graduales
    candidatos = [0.25, -0.25, 0.40, -0.40, 0.60, -0.60, 0.80, -0.80]
    mejor_rad = 0.35
    max_margen = -1.0

    for rad in candidatos:
        margen = min(_dist_punto_a_curva(p0, p1, rad, q) for q in intermedios)
        if margen >= radio_seguridad:
            return rad
        if margen > max_margen:
            max_margen = margen
            mejor_rad = rad

    return mejor_rad


def _clasificar_aristas(G, pos, edgelist, radio_seguridad):
    """Separa las aristas en rectas (rad=0) y curvas {(u,v): rad}."""
    todos = list(G.nodes())
    rectas = []
    curvas = {}
    for u, v in edgelist:
        rad = _evaluar_arista(u, v, pos, todos, radio_seguridad)
        if rad == 0.0:
            rectas.append((u, v))
        else:
            curvas[(u, v)] = rad
    return rectas, curvas


# ── Dibujo principal ──────────────────────────────────────────────────────────

def dibujar_grafo(frame, grafo, ruta=None):
    """Dibuja todos los usuarios y amistades con su peso de forma ordenada.

    Garantías:
    • Los nodos se distribuyen ampliamente sin encimarse.
    • Las aristas se mantienen rectas siempre que sea posible.
    • Si una arista fuese a cruzar sobre un nodo, se curva automáticamente
      para rodearlo sin tocarlo ni pasar por encima ni por debajo.
    • Las aristas curvas usan arrows=True y arrowstyle='-' para eliminar
      las advertencias de Matplotlib/NetworkX sin dibujar flechas.
    """
    for widget in frame.winfo_children():
        widget.destroy()

    # Construir grafo
    G = nx.Graph()
    G.add_nodes_from(grafo.usuarios.keys())
    for u, vecinos in grafo.adyacencia.items():
        for v, peso in vecinos.items():
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=peso)

    # Posiciones con relajación anti-colisión
    pos = _obtener_posiciones_ordenadas(G)

    # Radio de seguridad geométrico para colisiones
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    rango = max((max(xs) - min(xs)), (max(ys) - min(ys))) or 1.0
    radio_seguridad = rango * 0.045  # margen proporcional a la escala

    # Identificar ruta
    ruta_aristas = set()
    ruta_nodos   = set()
    if ruta and len(ruta) >= 2:
        ruta_nodos = set(ruta)
        for i in range(len(ruta) - 1):
            ruta_aristas.add(frozenset([ruta[i], ruta[i + 1]]))

    aristas_def  = [(u, v) for u, v in G.edges() if frozenset([u, v]) not in ruta_aristas]
    aristas_ruta = [(u, v) for u, v in G.edges() if frozenset([u, v]) in ruta_aristas]
    nodos_def    = [n for n in G.nodes() if n not in ruta_nodos]
    nodos_ruta   = [n for n in G.nodes() if n in ruta_nodos]

    # Clasificar rectas vs curvas
    rectas_def, curvas_def   = _clasificar_aristas(G, pos, aristas_def, radio_seguridad)
    rectas_ruta, curvas_ruta = _clasificar_aristas(G, pos, aristas_ruta, radio_seguridad)

    # Crear figura
    fig = Figure(figsize=(_FIG_W, _FIG_H), dpi=_DPI, facecolor=_BG)
    ax  = fig.add_subplot(111, facecolor=_BG)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.03, right=0.97, top=0.97, bottom=0.03)

    # Márgenes amplios en los ejes para que ningún nodo se corte
    pad_x = (max(xs) - min(xs)) * 0.08 + 0.2
    pad_y = (max(ys) - min(ys)) * 0.08 + 0.2
    ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
    ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)

    # 1. Dibujar aristas rectas normales (LineCollection limpia sin advertencias)
    if rectas_def:
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=rectas_def,
            edge_color=_EDGE_DEF,
            width=1.4,
            alpha=0.75,
        )

    # 2. Dibujar aristas curvas normales (con arrows=True y arrowstyle='-' sin flechas ni advertencias)
    for (u, v), rad in curvas_def.items():
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=[(u, v)],
            edge_color=_EDGE_DEF,
            width=1.4,
            alpha=0.75,
            arrows=True,
            arrowstyle="-",
            connectionstyle=f"arc3,rad={rad}",
            min_source_margin=16,
            min_target_margin=16,
        )

    # 3. Dibujar aristas de la ruta
    if rectas_ruta:
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=rectas_ruta,
            edge_color=_EDGE_RUTA,
            width=2.8,
            alpha=1.0,
        )

    for (u, v), rad in curvas_ruta.items():
        nx.draw_networkx_edges(
            G, pos, ax=ax,
            edgelist=[(u, v)],
            edge_color=_EDGE_RUTA,
            width=2.8,
            alpha=1.0,
            arrows=True,
            arrowstyle="-",
            connectionstyle=f"arc3,rad={rad}",
            min_source_margin=18,
            min_target_margin=18,
        )

    # 4. Dibujar nodos (encima de las aristas con zorder alto)
    if nodos_def:
        nx.draw_networkx_nodes(
            G, pos, ax=ax,
            nodelist=nodos_def,
            node_color=_NODE_DEF,
            node_size=_NODE_SIZE,
            alpha=0.95,
        )
    if nodos_ruta:
        nx.draw_networkx_nodes(
            G, pos, ax=ax,
            nodelist=nodos_ruta,
            node_color=_NODE_RUTA,
            node_size=_NODE_SIZE_RUTA,
            alpha=1.0,
        )

    # 5. Etiquetas de nodos limpias
    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_color=_LABEL_COLOR,
        font_size=7.5,
        font_weight="bold",
        font_family="sans-serif",
    )

    # 6. Etiquetas de peso
    bbox_def  = dict(boxstyle="round,pad=0.12", facecolor=_WEIGHT_BG, edgecolor="none", alpha=0.8)
    bbox_ruta = dict(boxstyle="round,pad=0.12", facecolor=_WEIGHT_BG, edgecolor=_EDGE_RUTA, linewidth=0.8, alpha=0.9)

    pesos_def  = {(u, v): G[u][v]["weight"] for u, v in aristas_def}
    pesos_ruta = {(u, v): G[u][v]["weight"] for u, v in aristas_ruta}

    if pesos_def:
        nx.draw_networkx_edge_labels(
            G, pos, ax=ax,
            edge_labels=pesos_def,
            font_color=_WEIGHT_DEF,
            font_size=6.5,
            bbox=bbox_def,
        )
    if pesos_ruta:
        nx.draw_networkx_edge_labels(
            G, pos, ax=ax,
            edge_labels=pesos_ruta,
            font_color=_WEIGHT_RUTA,
            font_size=6.5,
            bbox=bbox_ruta,
        )

    # Restaurar límites del canvas
    ax.set_xlim(min(xs) - pad_x, max(xs) + pad_x)
    ax.set_ylim(min(ys) - pad_y, max(ys) + pad_y)

    # Incrustar en CustomTkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
