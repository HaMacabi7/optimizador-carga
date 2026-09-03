class Paquete:
    def __init__(self, id_paquete: str, peso: float, valor: float):
        self.id_paquete = id_paquete
        self.peso = float(peso)
        self.valor = float(valor)
        # Ratio de rentabilidad por kilo
        self.ratio = self.valor / self.peso if self.peso > 0 else 0

    def __repr__(self):
        return f"Paquete(id='{self.id_paquete}', peso={self.peso}kg, valor=${self.valor})"