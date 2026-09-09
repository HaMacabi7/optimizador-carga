class Paquete:
    # esta clase guarda los datos basicos de cada paquete
    def __init__(self, id_paquete: str, peso: float, valor: float):
        self.id_paquete = id_paquete
        self.peso = float(peso)
        self.valor = float(valor)
        # aqui vemos cuanto valor deja el paquete por cada kilo
        self.ratio = self.valor / self.peso if self.peso > 0 else 0

    def __repr__(self):
        # esto sirve para mostrar el paquete de forma facil de leer
        return f"Paquete(id='{self.id_paquete}', peso={self.peso}kg, valor=${self.valor})"