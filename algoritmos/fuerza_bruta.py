import time
from itertools import combinations
from typing import List, Tuple
from modelos.paquete import Paquete


def resolver_fuerza_bruta(paquetes: List[Paquete], capacidad_maxima: float) -> Tuple[
    List[Paquete], float, float, float]:
    "esta funcion revisa todas las formas posibles de cargar los paquetes"
    inicio = time.perf_counter()

    mejor_combinacion = []
    mejor_valor = 0.0
    mejor_peso = 0.0
    n = len(paquetes)

    "prueba grupos de uno dos tres paquetes y asi hasta revisar todas las opciones"
    "es facil de entender pero se vuelve lenta con muchos paquetes"
    for r in range(1, n + 1):
        for combo in combinations(paquetes, r):
            peso_total = sum(p.peso for p in combo)
            if peso_total <= capacidad_maxima:
                valor_total = sum(p.valor for p in combo)
                "guardamos la combinacion valida que deja mas ganancia"
                if valor_total > mejor_valor:
                    mejor_valor = valor_total
                    mejor_peso = peso_total
                    mejor_combinacion = list(combo)

    duracion_ms = (time.perf_counter() - inicio) * 1000
    return mejor_combinacion, mejor_peso, mejor_valor, duracion_ms