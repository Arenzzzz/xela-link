"""Dijkstra para la ruta (cadena) de menor peso entre dos usuarios.

Responsable: Arenz. Implementar a mano con heapq (no usar nx.shortest_path).
"""
import heapq


def dijkstra(grafo, origen, destino):
    """Devuelve un dict:
    {
        "ruta": ["arenz", "luis", "maria", "carlos"],  # [] si no hay conexión
        "peso": 4,                                      # None si no hay conexión
        "intermediarios": ["luis", "maria"],            # personas en común
        "pasos": [                                      # tabla paso a paso
            {"visitado": "arenz", "distancias": {...}, "previos": {...}},
            ...
        ],
    }
    """
    # TODO Arenz
    raise NotImplementedError
