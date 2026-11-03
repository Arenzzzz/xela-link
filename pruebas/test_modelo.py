"""Pruebas del modelo con el ejemplo del informe.

Responsable: Keila. Ejecutar: python -m unittest discover pruebas
"""
import unittest

import os
import tempfile

from datos.gestor_json import cargar, guardar
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

    def test_cadena_aceptada_detalle(self):
        r = Automata(self.g, "arenz", "carlos").validar(["luis", "maria", "carlos"])
        self.assertEqual(r["recorrido"], ["arenz", "luis", "maria", "carlos"])
        self.assertEqual(r["peso"], 4)
        self.assertIsNone(r["falla"])

    def test_cadena_rechazada_detalle_sin_amistad(self):
        r = Automata(self.g, "arenz", "carlos").validar(["maria", "carlos"])
        self.assertIsNone(r["peso"])
        self.assertEqual(r["falla"], "arenz y maria no son amigos")

    def test_cadena_rechazada_detalle_no_termina_en_F(self):
        r = Automata(self.g, "arenz", "carlos").validar(["luis", "maria"])
        self.assertIsNone(r["peso"])
        self.assertIn("maria", r["falla"])

    def test_sin_conexion(self):
        # Usuario aislado: existe pero no tiene ninguna amistad
        self.g.agregar_usuario("aislado", "Usuario Aislado", "1234")
        r = dijkstra(self.g, "arenz", "aislado")
        self.assertEqual(r["ruta"], [])
        self.assertIsNone(r["peso"])
        self.assertEqual(r["intermediarios"], [])
        self.assertEqual(self.g.sugerencias("aislado"), [])

    def test_amigos_directos(self):
        r = dijkstra(self.g, "arenz", "luis")
        self.assertEqual(r["ruta"], ["arenz", "luis"])
        self.assertEqual(r["peso"], self.g.peso("arenz", "luis"))
        self.assertEqual(r["intermediarios"], [])

    def test_cadena_directa_aceptada(self):
        r = Automata(self.g, "arenz", "luis").validar(["luis"])
        self.assertTrue(r["aceptada"])
        self.assertEqual(r["peso"], 1)

    def test_cadena_vacia_rechazada(self):
        r = Automata(self.g, "arenz", "carlos").validar([])
        self.assertFalse(r["aceptada"])

    def test_amistad_usuario_inexistente(self):
        ok, mensaje = self.g.agregar_amistad("arenz", "fantasma", 2)
        self.assertFalse(ok)
        self.assertIn("no existe", mensaje)

    def test_amistad_repetida(self):
        ok, mensaje = self.g.agregar_amistad("arenz", "luis", 2)
        self.assertFalse(ok)
        self.assertIn("Ya son amigos", mensaje)

    def test_amistad_con_nivel_invalido(self):
        self.g.agregar_usuario("nuevo", "Nuevo", "1234")
        ok, mensaje = self.g.agregar_amistad("arenz", "nuevo", 5)
        self.assertFalse(ok)
        self.assertIn("1, 2 o 3", mensaje)

    def test_eliminar_amistad(self):
        self.assertTrue(self.g.eliminar_amistad("arenz", "luis"))
        self.assertFalse(self.g.son_amigos("arenz", "luis"))
        self.assertFalse(self.g.son_amigos("luis", "arenz"))

    def test_login(self):
        self.assertTrue(self.g.verificar_login("arenz", "1234"))
        self.assertFalse(self.g.verificar_login("arenz", "incorrecta"))

    def test_sugerencias_son_amigos_de_amigos(self):
        sugeridos = [u for u, _ in self.g.sugerencias("arenz")]
        self.assertTrue(sugeridos)
        for u in sugeridos:
            self.assertFalse(self.g.son_amigos("arenz", u))
            self.assertNotEqual(u, "arenz")

    def test_guardar_y_cargar(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "copia.json")
            guardar(self.g, ruta)
            copia = cargar(ruta)
        self.assertEqual(copia.usuarios, self.g.usuarios)
        self.assertEqual(copia.adyacencia, self.g.adyacencia)


if __name__ == "__main__":
    unittest.main()