"""Pruebas del modelo con el ejemplo del informe.

Responsable: Keila. Ejecutar: python -m unittest discover pruebas
"""
import unittest

from datos.gestor_json import cargar
from modelo.dijkstra import dijkstra
from modelo.automata import Automata


class TestXelaLink(unittest.TestCase):
    def setUp(self):
        self.g = cargar("datos/usuarios.json")

    def test_ruta_mas_corta(self):
        r = dijkstra(self.g, "arenz", "carlos")
        self.assertEqual(r["ruta"], ["arenz", "luis", "maria", "carlos"])
        self.assertEqual(r["peso"], 4)
        self.assertEqual(r["intermediarios"], ["luis", "maria"])

    def test_cadena_aceptada(self):
        a = Automata(self.g, "arenz", "carlos")
        self.assertTrue(a.validar(["luis", "maria", "carlos"])["aceptada"])

    def test_cadena_rechazada_sin_amistad(self):
        a = Automata(self.g, "arenz", "carlos")
        self.assertFalse(a.validar(["maria", "carlos"])["aceptada"])

    def test_cadena_rechazada_no_termina_en_F(self):
        a = Automata(self.g, "arenz", "carlos")
        self.assertFalse(a.validar(["luis", "maria"])["aceptada"])

    # TODO Keila: caso "sin conexión" (agregar un usuario aislado) y amigos directos.


if __name__ == "__main__":
    unittest.main()
