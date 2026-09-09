
'''from modelos.paquete import Paquete
from algoritmos.fuerza_bruta import resolver_fuerza_bruta
from algoritmos.voraz import resolver_voraz
from algoritmos.backtracking import resolver_backtracking
from algoritmos.programacion_dinamica import resolver_programacion_dinamica


def test():
    datos_prueba = [
        Paquete("PKG-1", peso=10, valor=60),
        Paquete("PKG-2", peso=20, valor=100),
        Paquete("PKG-3", peso=30, valor=120),
        Paquete("PKG-4", peso=15, valor=75),
        Paquete("PKG-5", peso=5, valor=30)
    ]
    capacidad = 50.0

    print("================ TEST COMPLETO DE ALGORITMOS ================")

    # primero probamos fuerza bruta
    res_fb = resolver_fuerza_bruta(datos_prueba, capacidad)
    print(f"\n[1. Fuerza Bruta]           | Ganancia: ${res_fb[2]} | Peso: {res_fb[1]} kg | Tiempo: {res_fb[3]:.4f} ms")

    # luego probamos el metodo voraz
    res_v = resolver_voraz(datos_prueba, capacidad)
    print(f"[2. Voraz (Greedy)]         | Ganancia: ${res_v[2]} | Peso: {res_v[1]} kg | Tiempo: {res_v[3]:.4f} ms")

    # despues probamos backtracking
    res_bt = resolver_backtracking(datos_prueba, capacidad)
    print(f"[3. Backtracking]           | Ganancia: ${res_bt[2]} | Peso: {res_bt[1]} kg | Tiempo: {res_bt[3]:.4f} ms")

    # por ultimo probamos programacion dinamica
    res_dp = resolver_programacion_dinamica(datos_prueba, capacidad)
    print(f"[4. Programación Dinámica]  | Ganancia: ${res_dp[2]} | Peso: {res_dp[1]} kg | Tiempo: {res_dp[3]:.4f} ms")
    print("=============================================================")'''


from vistas.interfaz import VentanaOptimizador

# esta es la puerta de entrada del programa
def main():
    # crea la ventana y la deja lista para que el usuario la use
    app = VentanaOptimizador()
    app.mainloop()


if __name__ == "__main__":
    main()