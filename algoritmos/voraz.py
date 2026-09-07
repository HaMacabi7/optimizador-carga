import time
from typing import List, Tuple
from modelos.paquete import Paquete

def resolver_voraz(paquetes: List[Paquete], capacidad_maxima: float) -> Tuple[List[Paquete], float, float, float]:
    """
    Selección voraz basada en el ratio valor/peso.
    Complejidad Temporal: O(n log n) por el ordenamiento inicial.
    """
    inicio = time.perf_counter()

    # Primero pone arriba los paquetes que dan más valor por cada kilo.
    # Esta estrategia es rápida, aunque no siempre encuentra la mejor combinación.
    paquetes_ordenados = sorted(paquetes, key=lambda p: p.ratio, reverse=True)

    seleccionados = []
    peso_acumulado = 0.0
    valor_acumulado = 0.0

    for p in paquetes_ordenados:
        # Se agrega el paquete solo si todavía cabe en el vehículo.
        if peso_acumulado + p.peso <= capacidad_maxima:
            seleccionados.append(p)
            peso_acumulado += p.peso
            valor_acumulado += p.valor

    duracion_ms = (time.perf_counter() - inicio) * 1000
    return seleccionados, peso_acumulado, valor_acumulado, duracion_ms