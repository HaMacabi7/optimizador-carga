import time
from decimal import Decimal
from typing import List, Tuple
from modelos.paquete import Paquete


def _cantidad_decimales(valor: float) -> int:
    # Calcula cuántos decimales necesitamos conservar, por ejemplo 1.50 -> 2.
    decimal = Decimal(str(valor)).normalize()
    return max(0, -decimal.as_tuple().exponent)


def resolver_programacion_dinamica(paquetes: List[Paquete], capacidad_maxima: float) -> Tuple[List[Paquete], float, float, float]:
    """
    Resuelve el problema de la mochila 0/1 construyendo una tabla de subproblemas.
    Complejidad Temporal: O(n * W)
    Complejidad Espacial: O(n * W)
    """
    inicio = time.perf_counter()
    n = len(paquetes)
    # La tabla trabaja con números enteros. Escalamos los pesos para no perder
    # los decimales: 1.5 kg pasa a ser 15 si la precisión usada es de 1 decimal.
    precision = max(
        [_cantidad_decimales(capacidad_maxima)]
        + [_cantidad_decimales(p.peso) for p in paquetes]
    )
    escala = 10 ** precision
    capacidad = int(Decimal(str(capacidad_maxima)) * escala)

    # Cada fila representa los paquetes revisados y cada columna una capacidad.
    # En cada casilla guardamos la mayor ganancia posible hasta ese punto.
    dp = [[0.0 for _ in range(capacidad + 1)] for _ in range(n + 1)]

    # Para cada paquete elegimos entre usarlo o dejar la mejor opción anterior.
    for i in range(1, n + 1):
        p = paquetes[i - 1]
        peso_int = int(Decimal(str(p.peso)) * escala)
        for w in range(1, capacidad + 1):
            if peso_int <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - peso_int] + p.valor)
            else:
                dp[i][w] = dp[i - 1][w]

    # Retrocedemos por la tabla para descubrir qué paquetes formaron la solución.
    seleccionados = []
    w = capacidad
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            p = paquetes[i - 1]
            seleccionados.append(p)
            w -= int(Decimal(str(p.peso)) * escala)

    peso_total = sum(p.peso for p in seleccionados)
    mejor_valor = dp[n][capacidad]
    duracion_ms = (time.perf_counter() - inicio) * 1000

    return seleccionados, peso_total, mejor_valor, duracion_ms