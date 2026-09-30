from math import isfinite


class Paquete:
    # clase guarda datos basicos de cada paquete
    def __init__(self, id_paquete: str, peso: float, valor: float):
        self.id_paquete = id_paquete
        self.peso = float(peso)
        self.valor = float(valor)
        if not self.id_paquete.strip() or not isfinite(self.peso) or self.peso <= 0:
            raise ValueError("El paquete requiere un ID y un peso finito mayor que cero.")
        if not isfinite(self.valor) or self.valor < 0:
            raise ValueError("El valor debe ser finito e igual o mayor que cero.")
        # aqui vemos cuanto valor deja el paquete por cada kilo
        self.ratio = self.valor / self.peso if self.peso > 0 else 0

    def __repr__(self):
        #para mostrar paquete que sea facil de leer
        return f"Paquete(id='{self.id_paquete}', peso={self.peso}kg, valor=${self.valor})"