import time
from typing import List, Tuple
from modelos.paquete import Paquete


def resolver_backtracking(paquetes: List[Paquete], capacidad_maxima: float) -> Tuple[
    List[Paquete], float, float, float]:
    # esta funcion va probando caminos y regresa cuando uno ya no sirve
    inicio = time.perf_counter()
    n = len(paquetes)

    mejor_valor = 0.0
    mejor_peso = 0.0
    mejor_seleccion = []

    def backtrack(indice: int, peso_actual: float, valor_actual: float, seleccion_actual: List[Paquete]):
        nonlocal mejor_valor, mejor_peso, mejor_seleccion

        # si esta combinacion se pasa de peso ya no seguimos por ese camino
        # asi evitamos revisar opciones que sabemos que no sirven
        if peso_actual > capacidad_maxima:
            return

        # si encontramos una combinacion con mas valor la guardamos
        if valor_actual > mejor_valor:
            mejor_valor = valor_actual
            mejor_peso = peso_actual
            mejor_seleccion = list(seleccion_actual)

        # cuando ya no quedan paquetes termina este camino
        if indice == n:
            return

        # primero probamos metiendo el paquete actual
        p = paquetes[indice]
        seleccion_actual.append(p)
        backtrack(indice + 1, peso_actual + p.peso, valor_actual + p.valor, seleccion_actual)
        seleccion_actual.pop()  # lo quitamos para probar la otra opcion

        # despues probamos el mismo camino sin meterlo
        backtrack(indice + 1, peso_actual, valor_actual, seleccion_actual)

    backtrack(0, 0.0, 0.0, [])
    duracion_ms = (time.perf_counter() - inicio) * 1000
    return mejor_seleccion, mejor_peso, mejor_valor, duracion_ms