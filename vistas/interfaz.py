import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from modelos.paquete import Paquete
from algoritmos.fuerza_bruta import resolver_fuerza_bruta
from algoritmos.voraz import resolver_voraz
from algoritmos.backtracking import resolver_backtracking
from algoritmos.programacion_dinamica import resolver_programacion_dinamica


class VentanaOptimizador(tk.Tk):
    # esta clase arma la ventana y conecta los botones con los algoritmos
    def __init__(self):
        super().__init__()
        self.title("OptiCarga - Sistema de Optimización Logística")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.paquetes = []
        self._crear_interfaz()

    def _crear_interfaz(self):
        # aqui armamos la parte de arriba con los controles principales
        panel_top = ttk.LabelFrame(self, text=" Configuración de Carga y Capacidad ", padding=10)
        panel_top.pack(fill="x", padx=15, pady=8)

        ttk.Button(panel_top, text="Cargar Archivo CSV", command=self._cargar_csv).pack(side="left", padx=5)

        ttk.Label(panel_top, text="Capacidad Vehicular (kg):").pack(side="left", padx=(20, 5))
        self.entry_capacidad = ttk.Entry(panel_top, width=10)
        self.entry_capacidad.insert(0, "50")
        self.entry_capacidad.pack(side="left", padx=5)

        ttk.Label(panel_top, text="Algoritmo:").pack(side="left", padx=(20, 5))
        self.combo_algoritmo = ttk.Combobox(
            panel_top,
            values=["Fuerza Bruta", "Voraz (Greedy)", "Backtracking", "Programación Dinámica", "Comparar Todos"],
            state="readonly",
            width=22
        )
        self.combo_algoritmo.current(4)  # dejamos comparar todos como opcion inicial
        self.combo_algoritmo.pack(side="left", padx=5)

        ttk.Button(panel_top, text="▶ Ejecutar Optimización", command=self._ejecutar).pack(side="left", padx=15)

        # aqui dividimos la ventana entre los paquetes y los resultados
        panel_central = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        panel_central.pack(fill="both", expand=True, padx=15, pady=5)

        # esta tabla muestra los paquetes que se cargaron
        frame_tabla = ttk.LabelFrame(panel_central, text=" Manifiesto de Paquetes Disponibles ", padding=5)
        panel_central.add(frame_tabla, weight=1)

        self.tabla = ttk.Treeview(frame_tabla, columns=("id", "peso", "valor", "ratio"), show="headings", height=15)
        self.tabla.heading("id", text="ID")
        self.tabla.heading("peso", text="Peso (kg)")
        self.tabla.heading("valor", text="Valor ($)")
        self.tabla.heading("ratio", text="Ratio ($/kg)")
        self.tabla.column("id", width=80, anchor="center")
        self.tabla.column("peso", width=80, anchor="e")
        self.tabla.column("valor", width=80, anchor="e")
        self.tabla.column("ratio", width=80, anchor="e")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # este lado muestra los resultados y la grafica
        frame_derecho = ttk.Frame(panel_central)
        panel_central.add(frame_derecho, weight=2)

        self.txt_resultados = tk.Text(frame_derecho, height=8, wrap="word", font=("Consolas", 10))
        self.txt_resultados.pack(fill="x", padx=5, pady=(0, 5))

        self.frame_grafica = ttk.LabelFrame(frame_derecho, text=" Métricas de Rendimiento ", padding=5)
        self.frame_grafica.pack(fill="both", expand=True, padx=5)

    def _cargar_csv(self):
        # lee el archivo y convierte cada fila en un objeto paquete
        ruta = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
        if not ruta:
            return

        self.paquetes.clear()
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            with open(ruta, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pkg = Paquete(row["id"], float(row["peso"]), float(row["valor"]))
                    self.paquetes.append(pkg)
                    self.tabla.insert("", "end", values=(pkg.id_paquete, f"{pkg.peso:.2f}", f"{pkg.valor:.2f}",
                                                         f"{pkg.ratio:.2f}"))
            messagebox.showinfo("Éxito", f"Se cargaron {len(self.paquetes)} paquetes correctamente.")
        except Exception as e:
            messagebox.showerror("Error de lectura", f"No se pudo leer el archivo CSV:\n{e}")

    def _ejecutar(self):
        # toma la capacidad y ejecuta el algoritmo que eligio el usuario
        if not self.paquetes:
            messagebox.showwarning("Aviso", "Primero debe cargar un archivo CSV con paquetes.")
            return

        try:
            capacidad = float(self.entry_capacidad.get())
            if capacidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La capacidad debe ser un número mayor a cero.")
            return

        # la fuerza bruta revisa todas las combinaciones y puede tardar mucho
        # por eso frenamos cargas grandes para que la ventana no se congele
        if len(self.paquetes) > 22 and self.combo_algoritmo.get() in ["Fuerza Bruta", "Comparar Todos"]:
            messagebox.showwarning("Límite de Fuerza Bruta",
                                   f"Fuerza Bruta tiene complejidad O(2^n). Con {len(self.paquetes)} paquetes "
                                   "tomaría demasiado tiempo. Ejecútelo con máximo 20 paquetes.")
            return

        seleccion = self.combo_algoritmo.get()
        self.txt_resultados.delete("1.0", tk.END)

        tiempos = []
        nombres = []

        if seleccion in ["Fuerza Bruta", "Comparar Todos"]:
            # busca la mejor respuesta revisando todas las combinaciones
            items, peso, val, t = resolver_fuerza_bruta(self.paquetes, capacidad)
            self._mostrar_resumen("Fuerza Bruta", items, peso, val, t)
            nombres.append("Fuerza Bruta")
            tiempos.append(t)

        if seleccion in ["Voraz (Greedy)", "Comparar Todos"]:
            # empieza por los paquetes con mejor valor por kilo
            items, peso, val, t = resolver_voraz(self.paquetes, capacidad)
            self._mostrar_resumen("Voraz (Greedy)", items, peso, val, t)
            nombres.append("Voraz")
            tiempos.append(t)

        if seleccion in ["Backtracking", "Comparar Todos"]:
            # prueba caminos y descarta los que ya superan la capacidad
            items, peso, val, t = resolver_backtracking(self.paquetes, capacidad)
            self._mostrar_resumen("Backtracking", items, peso, val, t)
            nombres.append("Backtracking")
            tiempos.append(t)

        if seleccion in ["Programación Dinámica", "Comparar Todos"]:
            # aprovecha resultados anteriores para no repetir tantos calculos
            items, peso, val, t = resolver_programacion_dinamica(self.paquetes, capacidad)
            self._mostrar_resumen("Prog. Dinámica", items, peso, val, t)
            nombres.append("Prog. Dinámica")
            tiempos.append(t)

        if seleccion == "Comparar Todos":
            self._dibujar_grafica(nombres, tiempos)

    def _mostrar_resumen(self, metodo: str, items: list, peso: float, val: float, t: float):
        # prepara el texto que se muestra despues de cada algoritmo
        ids = ", ".join(p.id_paquete for p in items)
        linea = (f"[{metodo}]\n"
                 f" • Paquetes ({len(items)}): {ids}\n"
                 f" • Peso Total: {peso:.2f} kg | Ganancia: ${val:.2f} | Tiempo: {t:.4f} ms\n"
                 f"{'-' * 75}\n")
        self.txt_resultados.insert(tk.END, linea)

    def _dibujar_grafica(self, nombres: list, tiempos: list):
        # crea una grafica sencilla para comparar los tiempos
        for widget in self.frame_grafica.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(5, 3.2), dpi=100)
        colores = ["#e74c3c", "#3498db", "#f39c12", "#2ecc71"]
        barras = ax.bar(nombres, tiempos, color=colores[:len(nombres)])

        ax.set_ylabel("Tiempo (milisegundos)")
        ax.set_title("Comparativa de Tiempo de Ejecución")
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        for bar in barras:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval, f"{yval:.4f}", ha="center", va="bottom", fontsize=8)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)