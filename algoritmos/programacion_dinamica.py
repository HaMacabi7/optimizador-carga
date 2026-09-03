import time
from typing import List, Tuple
from modelos.paquete import Paquete

def resolver_programacion_dinamica(paquetes: List[Paquete], capacidad_maxima: float) -> Tuple[List[Paquete], float, float, float]:
    """
    Resuelve el problema de la mochila 0/1 construyendo una tabla de subproblemas.
    Complejidad Temporal: O(n * W)
    Complejidad Espacial: O(n * W)
    """
    inicio = time.perf_counter()
    n = len(paquetes)
    capacidad = int(capacidad_maxima)

    # Matriz DP de dimensiones (n + 1) x (capacidad + 1)
    dp = [[0.0 for _ in range(capacidad + 1)] for _ in range(n + 1)]

    # Construcción de la tabla
    for i in range(1, n + 1):
        p = paquetes[i - 1]
        peso_int = int(p.peso)
        for w in range(1, capacidad + 1):
            if peso_int <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - peso_int] + p.valor)
            else:
                dp[i][w] = dp[i - 1][w]

    # Reconstrucción de la solución óptima
    seleccionados = []
    w = capacidad
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            p = paquetes[i - 1]
            seleccionados.append(p)
            w -= int(p.peso)

    peso_total = sum(p.peso for p in seleccionados)
    mejor_valor = dp[n][capacidad]
    duracion_ms = (time.perf_counter() - inicio) * 1000

    return seleccionados, peso_total, mejor_valor, duracion_ms