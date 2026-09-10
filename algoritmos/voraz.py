import time
from typing import List, Tuple
from modelos.paquete import Paquete

def resolver_voraz(paquetes: List[Paquete], capacidad_maxima: float) -> Tuple[List[Paquete], float, float, float]:
    "esta funcion empieza por los paquetes que parecen mas rentables"
    inicio = time.perf_counter()

    "pone arriba los paquetes que dan mas valor por cada kilo"
    "es rapido aunque no siempre encuentra la mejor combinacion"
    paquetes_ordenados = sorted(paquetes, key=lambda p: p.ratio, reverse=True)

    seleccionados = []
    peso_acumulado = 0.0
    valor_acumulado = 0.0

    for p in paquetes_ordenados:
        "agrega el paquete solo si todavia cabe en el vehiculo"
        if peso_acumulado + p.peso <= capacidad_maxima:
            seleccionados.append(p)
            peso_acumulado += p.peso
            valor_acumulado += p.valor

    duracion_ms = (time.perf_counter() - inicio) * 1000
    return seleccionados, peso_acumulado, valor_acumulado, duracion_ms