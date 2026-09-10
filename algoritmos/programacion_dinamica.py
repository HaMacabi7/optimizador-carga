import time
from decimal import Decimal
from typing import List, Tuple
from modelos.paquete import Paquete


def _cantidad_decimales(valor: float) -> int:
    "revisa cuantos decimales tenemos que conservar"
    decimal = Decimal(str(valor)).normalize()
    return max(0, -decimal.as_tuple().exponent)


def resolver_programacion_dinamica(paquetes: List[Paquete], capacidad_maxima: float) -> Tuple[List[Paquete], float, float, float]:
    "esta funcion va guardando resultados anteriores para no repetir tanto trabajo"
    inicio = time.perf_counter()
    n = len(paquetes)
    "la tabla usa numeros enteros para no perder los decimales"
    "por ejemplo uno punto cinco kilos pasa a ser quince"
    precision = max(
        [_cantidad_decimales(capacidad_maxima)]
        + [_cantidad_decimales(p.peso) for p in paquetes]
    )
    escala = 10 ** precision
    capacidad = int(Decimal(str(capacidad_maxima)) * escala)

    "cada fila representa paquetes revisados y cada columna una capacidad"
    "en cada espacio guardamos la mayor ganancia encontrada"
    dp = [[0.0 for _ in range(capacidad + 1)] for _ in range(n + 1)]

    "para cada paquete elegimos si usarlo o dejar la mejor opcion anterior"
    for i in range(1, n + 1):
        p = paquetes[i - 1]
        peso_int = int(Decimal(str(p.peso)) * escala)
        for w in range(1, capacidad + 1):
            if peso_int <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - peso_int] + p.valor)
            else:
                dp[i][w] = dp[i - 1][w]

    "recorremos la tabla hacia atras para saber que paquetes formaron la respuesta"
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