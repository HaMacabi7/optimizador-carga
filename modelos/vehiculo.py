from math import isfinite

from modelos.paquete import Paquete


class Vehiculo:
    def __init__(self, nombre: str, capacidad: float):
        nombre = nombre.strip()
        capacidad = float(capacidad)
        if not nombre:
            raise ValueError("El nombre del vehículo no puede estar vacío.")
        if not isfinite(capacidad) or capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor que cero.")

        self.nombre = nombre
        self.capacidad = capacidad
        self.paquetes: list[Paquete] = []

    @property
    def peso_actual(self) -> float:
        return sum(paquete.peso for paquete in self.paquetes)

    @property
    def valor_carga(self) -> float:
        return sum(paquete.valor for paquete in self.paquetes)

    @property
    def disponible(self) -> float:
        return max(0.0, self.capacidad - self.peso_actual)

    @property
    def ocupacion(self) -> float:
        return self.peso_actual / self.capacidad * 100

    @property
    def estado(self) -> str:
        if self.ocupacion >= 99.999999:
            return "Capacidad alcanzada"
        if self.ocupacion >= 95:
            return "Cerca del límite"
        return "Carga baja"

    def agregar_paquete(self, paquete: Paquete) -> None:
        if self.peso_actual + paquete.peso > self.capacidad + 1e-9:
            raise ValueError(
                f"El paquete supera la capacidad disponible de {self.disponible:.2f} kg."
            )
        if any(actual.id_paquete.casefold() == paquete.id_paquete.casefold() for actual in self.paquetes):
            raise ValueError("Este paquete ya está asignado al vehículo.")
        self.paquetes.append(paquete)

    def quitar_paquete(self, id_paquete: str) -> Paquete | None:
        for indice, paquete in enumerate(self.paquetes):
            if paquete.id_paquete.casefold() == id_paquete.casefold():
                return self.paquetes.pop(indice)
        return None

    def actualizar(self, nombre: str, capacidad: float) -> None:
        nombre = nombre.strip()
        capacidad = float(capacidad)
        if not nombre:
            raise ValueError("El nombre del vehículo no puede estar vacío.")
        if not isfinite(capacidad):
            raise ValueError("La capacidad debe ser un número finito.")
        if capacidad < self.peso_actual - 1e-9:
            raise ValueError("La capacidad no puede ser menor que la carga actual.")
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor que cero.")
        self.nombre = nombre
        self.capacidad = capacidad