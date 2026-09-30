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
        self.furgonetas = []
        self._crear_interfaz()

    def _crear_interfaz(self):
        # aqui armamos la parte de arriba con los controles principales
        panel_top = ttk.LabelFrame(self, text=" Configuración de Carga y Capacidad ", padding=10)
        panel_top.pack(fill="x", padx=15, pady=8)

        ttk.Button(panel_top, text="Cargar Archivo CSV", command=self._cargar_csv).pack(side="left", padx=5)
        ttk.Button(panel_top, text="Agregar paquetes", command=self._mostrar_dialogo_paquete).pack(side="left", padx=5)

        ttk.Label(panel_top, text="Algoritmo:").pack(side="left", padx=(15, 5))
        self.combo_algoritmo = ttk.Combobox(
            panel_top,
            values=["Fuerza Bruta", "Voraz (Greedy)", "Backtracking", "Programación Dinámica", "Comparar Todos"],
            state="readonly",
            width=22
        )
        self.combo_algoritmo.current(4)  # dejamos comparar todos como opcion inicial
        self.combo_algoritmo.pack(side="left", padx=5)

        ttk.Button(panel_top, text="Ejecutar Optimización", command=self._ejecutar).pack(side="left", padx=10)

        self.frame_furgonetas = ttk.LabelFrame(self, text=" Furgonetas y capacidad ", padding=8)
        self.frame_furgonetas.pack(fill="x", padx=15, pady=(0, 5))
        ttk.Button(self.frame_furgonetas, text="+ Agregar furgoneta", command=self._agregar_furgoneta).pack(
            side="right", padx=5
        )
        self._agregar_furgoneta("2000")

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

    def _agregar_furgoneta(self, capacidad: str = "500"):
        fila = ttk.Frame(self.frame_furgonetas)
        fila.pack(side="left", padx=(0, 12), pady=2)
        etiqueta = ttk.Label(fila)
        etiqueta.pack(side="left", padx=(0, 5))
        entrada = ttk.Entry(fila, width=9)
        entrada.insert(0, capacidad)
        entrada.pack(side="left")
        boton_quitar = ttk.Button(fila, text="Quitar", command=lambda: self._quitar_furgoneta(fila))
        boton_quitar.pack(side="left", padx=(4, 0))
        self.furgonetas.append((fila, etiqueta, entrada))
        self._actualizar_etiquetas_furgonetas()

    def _quitar_furgoneta(self, fila):
        if len(self.furgonetas) == 1:
            messagebox.showwarning("Furgonetas", "Debe conservar al menos una furgoneta.")
            return

        self.furgonetas = [item for item in self.furgonetas if item[0] is not fila]
        fila.destroy()
        self._actualizar_etiquetas_furgonetas()

    def _actualizar_etiquetas_furgonetas(self):
        for indice, (_, etiqueta, _) in enumerate(self.furgonetas, start=1):
            etiqueta.configure(text=f"Furgoneta {indice} (kg):")

    def _mostrar_dialogo_paquete(self):
        dialogo = tk.Toplevel(self)
        dialogo.title("Agregar paquete")
        dialogo.transient(self)
        dialogo.resizable(False, False)
        dialogo.grab_set()

        paquete_agregado = False
        campos = (("ID", "id"), ("Peso (kg)", "peso"), ("Valor ($)", "valor"))
        entradas = {}
        for fila, (etiqueta, clave) in enumerate(campos):
            ttk.Label(dialogo, text=etiqueta).grid(row=fila, column=0, padx=12, pady=6, sticky="w")
            entrada = ttk.Entry(dialogo, width=24)
            entrada.grid(row=fila, column=1, padx=12, pady=6)
            entradas[clave] = entrada

        def guardar_paquete():
            nonlocal paquete_agregado
            id_paquete = entradas["id"].get().strip()
            try:
                peso = float(entradas["peso"].get())
                valor = float(entradas["valor"].get())
                if not id_paquete or peso <= 0 or valor < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Datos inválidos",
                    "Ingrese un ID, un peso mayor que cero y un valor igual o mayor que cero.",
                    parent=dialogo
                )
                return

            if any(paquete.id_paquete.casefold() == id_paquete.casefold() for paquete in self.paquetes):
                messagebox.showerror("ID duplicado", "Ya existe un paquete con ese ID.", parent=dialogo)
                return

            paquete = Paquete(id_paquete, peso, valor)
            self.paquetes.append(paquete)
            self._insertar_paquete_en_tabla(paquete)
            paquete_agregado = True
            dialogo.destroy()

        botones = ttk.Frame(dialogo)
        botones.grid(row=len(campos), column=0, columnspan=2, pady=(8, 12))
        ttk.Button(botones, text="Cancelar", command=dialogo.destroy).pack(side="left", padx=5)
        ttk.Button(botones, text="Agregar", command=guardar_paquete).pack(side="left", padx=5)
        entradas["id"].focus_set()
        self.wait_window(dialogo)
        return paquete_agregado

    def _insertar_paquete_en_tabla(self, paquete: Paquete):
        self.tabla.insert(
            "", "end",
            values=(paquete.id_paquete, f"{paquete.peso:.2f}", f"{paquete.valor:.2f}", f"{paquete.ratio:.2f}")
        )

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
                    self._insertar_paquete_en_tabla(pkg)
            messagebox.showinfo("Éxito", f"Se cargaron {len(self.paquetes)} paquetes correctamente.")
        except Exception as e:
            messagebox.showerror("Error de lectura", f"No se pudo leer el archivo CSV:\n{e}")

    def _ejecutar(self):
        if not self.paquetes:
            messagebox.showwarning("Aviso", "Primero cargue un CSV o agregue paquetes.")
            return

        capacidades = []
        try:
            for indice, (_, _, entrada) in enumerate(self.furgonetas, start=1):
                capacidad = float(entrada.get())
                if capacidad <= 0:
                    raise ValueError(f"La capacidad de la furgoneta {indice} debe ser mayor que cero.")
                capacidades.append(capacidad)
        except ValueError as error:
            mensaje = str(error) or "Todas las capacidades deben ser números mayores que cero."
            messagebox.showerror("Capacidad inválida", mensaje)
            return

        if not capacidades:
            messagebox.showwarning("Aviso", "Agregue al menos una furgoneta.")
            return

        seleccion = self.combo_algoritmo.get()
        if len(self.paquetes) > 22 and seleccion in ["Fuerza Bruta", "Comparar Todos"]:
            messagebox.showwarning(
                "Límite de Fuerza Bruta",
                f"Fuerza Bruta tiene complejidad O(2^n). Con {len(self.paquetes)} paquetes "
                "tomaría demasiado tiempo. Ejecútelo con máximo 20 paquetes."
            )
            return

        algoritmos = {
            "Fuerza Bruta": resolver_fuerza_bruta,
            "Voraz (Greedy)": resolver_voraz,
            "Backtracking": resolver_backtracking,
            "Programación Dinámica": resolver_programacion_dinamica,
        }
        nombres_seleccionados = list(algoritmos) if seleccion == "Comparar Todos" else [seleccion]
        self.txt_resultados.delete("1.0", tk.END)
        resultados = []
        nombres_grafica = []
        tiempos_grafica = []

        for nombre in nombres_seleccionados:
            resolver = algoritmos[nombre]
            paquetes_disponibles = list(self.paquetes)
            resultados_furgonetas = []
            tiempo_total = 0.0

            for indice, capacidad in enumerate(capacidades, start=1):
                items, peso, valor, tiempo = resolver(paquetes_disponibles, capacidad)
                seleccionados = {id(paquete) for paquete in items}
                paquetes_disponibles = [
                    paquete for paquete in paquetes_disponibles if id(paquete) not in seleccionados
                ]
                espacio_libre = max(0.0, capacidad - peso)
                resultados_furgonetas.append((indice, capacidad, items, peso, valor, tiempo, espacio_libre))
                tiempo_total += tiempo
                self._mostrar_resumen(f"{nombre} | Furgoneta {indice}", items, peso, valor, tiempo, espacio_libre)

            valor_total = sum(resultado[4] for resultado in resultados_furgonetas)
            resultados.append((nombre, valor_total, resultados_furgonetas))
            nombres_grafica.append(nombre)
            tiempos_grafica.append(tiempo_total)

        self._dibujar_grafica(nombres_grafica, tiempos_grafica)
        mejor_nombre, _, mejor_asignacion = max(resultados, key=lambda resultado: resultado[1])
        espacios_libres = [resultado for resultado in mejor_asignacion if resultado[6] > 0.000001]
        if espacios_libres:
            detalle = "\n".join(
                f"Furgoneta {indice}: {espacio_libre:.2f} kg"
                for indice, _, _, _, _, _, espacio_libre in espacios_libres
            )
            agregar = messagebox.askyesno(
                "Espacio disponible",
                f"Con {mejor_nombre}, aún queda espacio por aprovechar:\n{detalle}\n\n"
                "¿Deseas agregar otro paquete?"
            )
            if agregar and self._mostrar_dialogo_paquete():
                self.txt_resultados.insert(
                    tk.END,
                    "Paquete agregado al manifiesto. Ejecute nuevamente la optimización para actualizar la flota.\n"
                )

    def _mostrar_resumen(self, metodo: str, items: list, peso: float, val: float, t: float, espacio_libre: float):
        # prepara el texto que se muestra despues de cada algoritmo
        ids = ", ".join(p.id_paquete for p in items)
        linea = (f"[{metodo}]\n"
                 f" • Paquetes ({len(items)}): {ids}\n"
                 f" • Peso Total: {peso:.2f} kg | Espacio libre: {espacio_libre:.2f} kg\n"
                 f" • Ganancia: ${val:.2f} | Tiempo: {t:.4f} ms\n"
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