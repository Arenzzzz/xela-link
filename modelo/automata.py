"""AFD ponderado A = (Q, Σ, δ, q0, F, w) construido sobre el grafo.

Responsable: Cristhian.
Q = usuarios ∪ {ERROR}, Σ = usuarios, δ(u, v) = v si son amigos, si no ERROR.
"""

ERROR = "q_err"

class Automata:
    def __init__(self, grafo, q0, destino):
        self.grafo = grafo
        self.q0 = q0
        self.F = {destino}

    def delta(self, estado, simbolo):
        if estado == ERROR:
            return ERROR, None
        if self.grafo.son_amigos(estado, simbolo):
            peso = self.grafo.peso(estado, simbolo)
            return simbolo, peso

        return ERROR, None

    def validar(self, cadena):
        """cadena: lista de usuarios sin incluir q0, ej. ["luis", "maria", "carlos"].
        Devuelve:
        {
            "aceptada": True/False,
            "recorrido": ["arenz", "luis", "maria", "carlos"],
            "peso": 4,                 # None si se rechaza
            "falla": None,             # o texto: "arenz y maria no son amigos"
        }
        """
        estado_actual = self.q0
        recorrido = [estado_actual]
        peso_total = 0
        for simbolo in cadena:
            estado_siguiente, peso = self.delta(estado_actual, simbolo)

            if estado_siguiente == ERROR:
                return {
                    "aceptada": False,
                    "recorrido": recorrido,
                    "peso": None,
                    "falla": f"{estado_actual} y {simbolo} no son amigos"
                }
            peso_total += peso
            estado_actual = estado_siguiente
            recorrido.append(estado_actual)

        if estado_actual in self.F:
            return {
                "aceptada": True,
                "recorrido": recorrido,
                "peso": peso_total,
                "falla": None
            }
        else:
            return {
                "aceptada": False,
                "recorrido": recorrido,
                "peso": None,
                "falla": f"La ruta termina en {estado_actual}, que no es el destino esperado."
            }