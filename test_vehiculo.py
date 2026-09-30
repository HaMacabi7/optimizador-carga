import unittest

from modelos.paquete import Paquete
from modelos.vehiculo import Vehiculo


class VehiculoTests(unittest.TestCase):
    def test_calcula_estado_disponible_y_ocupacion(self):
        vehiculo = Vehiculo("Furgoneta", 100)
        vehiculo.agregar_paquete(Paquete("PKG-001", 95, 120))

        self.assertEqual(vehiculo.peso_actual, 95)
        self.assertEqual(vehiculo.disponible, 5)
        self.assertEqual(vehiculo.estado, "Cerca del límite")

    def test_rechaza_paquete_que_supera_la_capacidad(self):
        vehiculo = Vehiculo("Furgoneta", 100)
        vehiculo.agregar_paquete(Paquete("PKG-001", 95, 120))

        with self.assertRaises(ValueError):
            vehiculo.agregar_paquete(Paquete("PKG-002", 6, 50))

    def test_no_reduce_capacidad_por_debajo_de_la_carga(self):
        vehiculo = Vehiculo("Furgoneta", 100)
        vehiculo.agregar_paquete(Paquete("PKG-001", 95, 120))

        with self.assertRaises(ValueError):
            vehiculo.actualizar("Furgoneta", 90)

    def test_carga_completa_activa_estado_alcanzado(self):
        vehiculo = Vehiculo("Furgoneta", 100)
        vehiculo.agregar_paquete(Paquete("PKG-001", 95, 120))
        vehiculo.actualizar("Furgoneta XL", 95)

        self.assertEqual(vehiculo.disponible, 0)
        self.assertEqual(vehiculo.estado, "Capacidad alcanzada")

    def test_rechaza_pesos_y_capacidades_no_finitos(self):
        with self.assertRaises(ValueError):
            Paquete("PKG-001", float("nan"), 10)
        with self.assertRaises(ValueError):
            Vehiculo("Furgoneta", float("inf"))


if __name__ == "__main__":
    unittest.main()