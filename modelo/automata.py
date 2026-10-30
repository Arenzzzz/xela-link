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
        """Función de transición."""
        # TODO Cristhian
        raise NotImplementedError

    def validar(self, cadena):
        """cadena: lista de usuarios SIN incluir q0, ej. ["luis", "maria", "carlos"].

        Devuelve:
        {
            "aceptada": True/False,
            "recorrido": ["arenz", "luis", "maria", "carlos"],
            "peso": 4,                 # None si se rechaza
            "falla": None,             # o texto: "arenz y maria no son amigos"
        }
        """
        # TODO Cristhian
        raise NotImplementedError
