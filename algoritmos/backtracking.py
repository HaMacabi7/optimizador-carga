import time
from typing import List, Tuple
from modelos.paquete import Paquete


def resolver_backtracking(paquetes: List[Paquete], capacidad_maxima: float) -> Tuple[
    List[Paquete], float, float, float]:
    """
    Exploración recursiva del árbol de decisiones con poda de ramas inválidas.
    Complejidad Temporal: O(2^n) en el peor caso, pero poda ramas que exceden la capacidad.
    """
    inicio = time.perf_counter()
    n = len(paquetes)

    mejor_valor = 0.0
    mejor_peso = 0.0
    mejor_seleccion = []

    def backtrack(indice: int, peso_actual: float, valor_actual: float, seleccion_actual: List[Paquete]):
        nonlocal mejor_valor, mejor_peso, mejor_seleccion

        # Si esta combinación ya se pasó de peso, no tiene sentido seguirla.
        # Así evitamos revisar varias opciones que ya sabemos que no sirven.
        if peso_actual > capacidad_maxima:
            return

        # Si encontramos una combinación con mejor valor que la actual
        if valor_actual > mejor_valor:
            mejor_valor = valor_actual
            mejor_peso = peso_actual
            mejor_seleccion = list(seleccion_actual)

        # Cuando ya no quedan paquetes, termina este camino de búsqueda.
        if indice == n:
            return

        # Probamos primero incluir el paquete actual.
        p = paquetes[indice]
        seleccion_actual.append(p)
        backtrack(indice + 1, peso_actual + p.peso, valor_actual + p.valor, seleccion_actual)
        seleccion_actual.pop()  # Quitarlo permite probar la otra opción.

        # Después probamos el mismo camino sin incluirlo.
        backtrack(indice + 1, peso_actual, valor_actual, seleccion_actual)

    backtrack(0, 0.0, 0.0, [])
    duracion_ms = (time.perf_counter() - inicio) * 1000
    return mejor_seleccion, mejor_peso, mejor_valor, duracion_ms