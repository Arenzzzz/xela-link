"""Dibujo del grafo con NetworkX + Matplotlib dentro de un frame de CustomTkinter.

Responsable: Pedro.
"""
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Paleta adaptada a CustomTkinter 
_BG          = "#1e1e2e"   
_NODE_DEF    = "#7c83fd"   
_NODE_RUTA   = "#f38ba8"   
_EDGE_DEF    = "#45475a"   
_EDGE_RUTA   = "#f38ba8"   
_LABEL_COLOR = "#cdd6f4"   
_WEIGHT_DEF  = "#a6adc8"   
_WEIGHT_RUTA = "#f38ba8"   


def dibujar_grafo(frame, grafo, ruta=None):
    """Dibuja todos los usuarios y amistades con su peso.
    Si se pasa `ruta` (lista de usuarios), sus nodos y aristas van en rojo y el resto en gris.
    Limpia el frame antes de redibujar para poder llamarse varias veces.
    """
    # --- Limpiar widgets anteriores del frame ---
    for widget in frame.winfo_children():
        widget.destroy()

    # --- Construir nx.Graph desde grafo.adyacencia ---
    G = nx.Graph()
    G.add_nodes_from(grafo.usuarios.keys())
    for u, vecinos in grafo.adyacencia.items():
        for v, peso in vecinos.items():
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=peso)

    # --- Layout fijo (seed) para que la posición no cambie entre llamadas ---
    pos = nx.spring_layout(G, seed=42, k=2.5)

    # --- Determinar aristas y nodos pertenecientes a la ruta ---
    ruta_aristas = set()
    ruta_nodos   = set()
    if ruta and len(ruta) >= 2:
        ruta_nodos = set(ruta)
        for i in range(len(ruta) - 1):
            # guardar como tupla ordenada para comparación independiente de dirección
            ruta_aristas.add(frozenset([ruta[i], ruta[i + 1]]))

    # Separar aristas normales vs. ruta
    aristas_def  = [(u, v) for u, v in G.edges()
                    if frozenset([u, v]) not in ruta_aristas]
    aristas_ruta = [(u, v) for u, v in G.edges()
                    if frozenset([u, v]) in ruta_aristas]

    # Separar nodos normales vs. ruta
    nodos_def  = [n for n in G.nodes() if n not in ruta_nodos]
    nodos_ruta = [n for n in G.nodes() if n in ruta_nodos]

    # --- Figura Matplotlib ---
    fig = Figure(figsize=(6, 5), dpi=100, facecolor=_BG)
    ax  = fig.add_subplot(111, facecolor=_BG)
    ax.set_axis_off()
    fig.tight_layout(pad=0.5)

    # Dibujar aristas normales
    nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aristas_def,
                           edge_color=_EDGE_DEF, width=1.5, alpha=0.7)

    # Dibujar aristas de ruta
    if aristas_ruta:
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=aristas_ruta,
                               edge_color=_EDGE_RUTA, width=3.0)

    # Dibujar nodos normales
    nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=nodos_def,
                           node_color=_NODE_DEF, node_size=600, alpha=0.9)

    # Dibujar nodos de ruta
    if nodos_ruta:
        nx.draw_networkx_nodes(G, pos, ax=ax, nodelist=nodos_ruta,
                               node_color=_NODE_RUTA, node_size=750)

    # Etiquetas de nodos
    nx.draw_networkx_labels(G, pos, ax=ax,
                            font_color=_LABEL_COLOR, font_size=8,
                            font_family="sans-serif")

    # Etiquetas de peso en las aristas
    pesos_def  = {(u, v): G[u][v]["weight"] for u, v in aristas_def}
    pesos_ruta = {(u, v): G[u][v]["weight"] for u, v in aristas_ruta}

    nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=pesos_def,
                                 font_color=_WEIGHT_DEF, font_size=7,
                                 bbox={"alpha": 0})
    if pesos_ruta:
        nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels=pesos_ruta,
                                     font_color=_WEIGHT_RUTA, font_size=7,
                                     bbox={"alpha": 0})

    # --- Incrustar en el frame de CustomTkinter ---
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
