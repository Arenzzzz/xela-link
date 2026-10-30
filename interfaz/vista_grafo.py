"""Dibujo del grafo con NetworkX + Matplotlib dentro de un frame de CustomTkinter.

Responsable: Pedro.
"""
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def dibujar_grafo(frame, grafo, ruta=None):
    """Dibuja todos los usuarios y amistades con su peso.
    Si se pasa `ruta` (lista de usuarios), sus nodos y aristas van en rojo y el resto en gris.
    """
    # TODO Pedro: construir nx.Graph desde grafo.adyacencia, layout fijo (seed),
    # etiquetas de peso en las aristas, FigureCanvasTkAgg(fig, master=frame).
    raise NotImplementedError
