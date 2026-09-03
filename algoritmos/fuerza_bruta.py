import time
from itertools import combinations
from typing import List, Tuple
from modelos.paquete import Paquete


def resolver_fuerza_bruta(paquetes: List[Paquete], capacidad_maxima: float) -> Tuple[
    List[Paquete], float, float, float]:
    """
    Evalúa todas las combinaciones posibles
    Complejidad Temporal: 
    """
    inicio = time.perf_counter()

    mejor_combinacion = []
    mejor_valor = 0.0
    mejor_peso = 0.0
    n = len(paquetes)

    # Genera todas las combinaciones de tamaño 1 hasta n
    for r in range(1, n + 1):
        for combo in combinations(paquetes, r):
            peso_total = sum(p.peso for p in combo)
            if peso_total <= capacidad_maxima:
                valor_total = sum(p.valor for p in combo)
                if valor_total > mejor_valor:
                    mejor_valor = valor_total
                    mejor_peso = peso_total
                    mejor_combinacion = list(combo)

    duracion_ms = (time.perf_counter() - inicio) * 1000
    return mejor_combinacion, mejor_peso, mejor_valor, duracion_ms