""" 
Dijkstra para la ruta (cadena) de menor peso entre dos usuarios.

Responsable: Arenz. Implementado a mano con heapq (no usa nx.shortest_path).
La ruta que devuelve es la cadena de menor peso aceptada por el autómata.
"""
import heapq

# Distancia inicial de todos los usuarios que aún no se han alcanzado
INFINITO = float("inf")


def reconstruir_ruta(previos, origen, destino):
    """Arma la ruta yendo hacia atrás desde el destino hasta el origen
    usando la tabla de predecesores, y luego la invierte.
    Ej.: previos = {"luis": "arenz", "maria": "luis", "carlos": "maria"}
         -> ["arenz", "luis", "maria", "carlos"]
    Si el destino nunca se alcanzó, devuelve una lista vacía."""
    if destino != origen and destino not in previos:
        return []

    ruta = [destino]
    while ruta[-1] != origen:
        ruta.append(previos[ruta[-1]])   # paso hacia atrás: ¿de quién vine?
    ruta.reverse()                        # se invierte para que empiece en el origen
    return ruta