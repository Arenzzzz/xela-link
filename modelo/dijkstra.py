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

def dijkstra(grafo, origen, destino):
    """ Calcula la ruta (cadena) de menor peso entre origen y destino """
    """ Devuelve un dict """

    origen, destino = origen.strip().lower(), destino.strip().lower()

    # Al inicio todos están a distanci infinita, excepto el origen (0)
    distancias = {usuario: INFINITO for usuario in grafo.usuarios}
    distancias[origen] = 0
    previos = {}            # previos[v] = desde qué usuario llegamos a v
    visitados = set()       # usuarios cuya distancia ya es definitiva
    pasos = []              # tabla paso a paso para el informe y la interfaz

    # Cola de prioridad (heap): siempre saca al usuariocon menor distancia acumulada
    cola = [(0, origen)]

    while cola:
        distancia_actual, actual = heapq.heappop(cola)

        # Si ya se visitó, esta entrada de la cola es vieja y se ignora
        if actual in visitados:
            continue

        visitados.add(actual)

        # Relajación: se intenta mejorar la distancia de cada amnigo de 'actual'
        for amigo, peso in grafo.adyacencia[actual].items():
            nueva = distancia_actual + peso

            if nueva < distancias[amigo]:
                distancias[amigo] = nueva
                previos[amigo] = actual
                heapq.heappush(cola, (nueva, amigo))

        # Se guarda una "foto" del estado después de visitar a 'actual'
        pasos.append({
            "visitado": actual,
            "distancias": dict(distancias),
            "previos": dict(previos)
        })

        if actual == destino:
            break

    ruta = reconstruir_ruta(previos, origen, destino)

    return {
        "ruta": ruta,
        "peso": distancias[destino] if ruta else None,
        "intermediarios": ruta[1:-1],   # todos menos el origen y el destino
        "pasos": pasos
    }