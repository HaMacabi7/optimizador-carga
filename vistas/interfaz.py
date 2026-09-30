import csv
from math import isfinite
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from modelos.paquete import Paquete
from modelos.vehiculo import Vehiculo
from algoritmos.fuerza_bruta import resolver_fuerza_bruta
from algoritmos.voraz import resolver_voraz
from algoritmos.backtracking import resolver_backtracking
from algoritmos.programacion_dinamica import resolver_programacion_dinamica


class VentanaOptimizador(tk.Tk):
    MAX_PAQUETES_EXHAUSTIVOS = 20
    ALGORITMOS_EXHAUSTIVOS = {"Fuerza Bruta", "Backtracking"}

    # esta clase arma la ventana y conecta los botones con los algoritmos
    def __init__(self):
        super().__init__()
        self.title("OptiCarga - Sistema de Optimización Logística")
        self.geometry("1300x780")
        self.minsize(1000, 650)

        self.paquetes = []
        self.vehiculos = []
        self._crear_interfaz()

    def _crear_interfaz(self):
        # aqui armamos la parte de arriba con los controles principales
        panel_top = ttk.LabelFrame(self, text=" Configuración de Carga y Capacidad ", padding=10)
        panel_top.pack(fill="x", padx=15, pady=8)

        ttk.Button(panel_top, text="Cargar CSV", command=self._cargar_csv).pack(side="left", padx=3)
        ttk.Button(panel_top, text="Agregar paquete", command=self._mostrar_dialogo_paquete).pack(side="left", padx=3)
        ttk.Button(panel_top, text="Editar paquete", command=self._editar_paquete).pack(side="left", padx=3)
        ttk.Button(panel_top, text="Quitar paquete", command=self._quitar_paquete).pack(side="left", padx=3)

        ttk.Label(panel_top, text="Algoritmo:").pack(side="left", padx=(15, 5))
        self.combo_algoritmo = ttk.Combobox(
            panel_top,
            values=["Fuerza Bruta", "Voraz (Greedy)", "Backtracking", "Programación Dinámica", "Comparar Todos"],
            state="readonly",
            width=20
        )
        self.combo_algoritmo.current(4)  # dejamos comparar todos como opcion inicial
        self.combo_algoritmo.pack(side="left", padx=5)

        ttk.Button(panel_top, text="Ejecutar Optimización", command=self._ejecutar).pack(side="left", padx=10)

        self.frame_estado = ttk.LabelFrame(self, text=" Estado de carga del vehículo ", padding=(10, 5))
        self.frame_estado.pack(fill="x", padx=15, pady=(0, 5))
        self.indicador_estado = tk.Canvas(self.frame_estado, width=20, height=20, highlightthickness=0)
        self.indicador_estado.pack(side="left", padx=(2, 7))
        self.indicador_estado_id = self.indicador_estado.create_oval(3, 3, 17, 17, fill="#d64a4a", outline="")
        self.etiqueta_estado = ttk.Label(self.frame_estado, text="Seleccione un vehículo")
        self.etiqueta_estado.pack(side="left", padx=(0, 18))
        self.etiqueta_carga = ttk.Label(self.frame_estado, text="")
        self.etiqueta_carga.pack(side="left")

        # aqui dividimos la ventana entre los paquetes y los resultados
        panel_central = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        panel_central.pack(fill="both", expand=True, padx=15, pady=5)

        # esta tabla muestra los paquetes que se cargaron
        frame_tabla = ttk.LabelFrame(panel_central, text=" Manifiesto de Paquetes ", padding=5)
        panel_central.add(frame_tabla, weight=1)

        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=("id", "peso", "valor", "ratio", "vehiculo"),
            show="headings",
            height=18,
            selectmode="browse"
        )
        self.tabla.heading("id", text="ID")
        self.tabla.heading("peso", text="Peso (kg)")
        self.tabla.heading("valor", text="Valor ($)")
        self.tabla.heading("ratio", text="Ratio ($/kg)")
        self.tabla.heading("vehiculo", text="Vehículo asignado")
        self.tabla.column("id", width=80, anchor="center")
        self.tabla.column("peso", width=80, anchor="e")
        self.tabla.column("valor", width=80, anchor="e")
        self.tabla.column("ratio", width=80, anchor="e")
        self.tabla.column("vehiculo", width=120, anchor="center")
        self.tabla.bind("<<TreeviewSelect>>", lambda _evento: self._actualizar_estado_seleccionado())

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll_y.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        # Este lado mantiene la flota visible junto a los resultados y las métricas.
        frame_derecho = ttk.Frame(panel_central)
        panel_central.add(frame_derecho, weight=2)

        frame_lista_vehiculos = ttk.LabelFrame(frame_derecho, text=" Vehículos registrados ", padding=5)
        frame_lista_vehiculos.pack(fill="x", padx=5, pady=(0, 5))
        self.tabla_vehiculos = ttk.Treeview(
            frame_lista_vehiculos,
            columns=("nombre", "capacidad", "carga", "disponible", "ocupacion", "estado"),
            show="headings",
            height=5,
            selectmode="browse"
        )
        encabezados = {
            "nombre": ("Vehículo", 130),
            "capacidad": ("Capacidad", 82),
            "carga": ("Carga actual", 88),
            "disponible": ("Disponible", 82),
            "ocupacion": ("Ocupación", 78),
            "estado": ("Estado", 130),
        }
        for columna, (texto, ancho) in encabezados.items():
            self.tabla_vehiculos.heading(columna, text=texto)
            self.tabla_vehiculos.column(columna, width=ancho, anchor="center")
        self.tabla_vehiculos.tag_configure("baja", background="#f8d7da", foreground="#842029")
        self.tabla_vehiculos.tag_configure("cerca", background="#fff3cd", foreground="#664d03")
        self.tabla_vehiculos.tag_configure("completa", background="#d1e7dd", foreground="#0f5132")
        self.tabla_vehiculos.bind("<<TreeviewSelect>>", lambda _evento: self._actualizar_estado_seleccionado())
        self.tabla_vehiculos.pack(side="left", fill="x", expand=True)
        barra_vehiculos = ttk.Scrollbar(
            frame_lista_vehiculos, orient="vertical", command=self.tabla_vehiculos.yview
        )
        self.tabla_vehiculos.configure(yscrollcommand=barra_vehiculos.set)
        barra_vehiculos.pack(side="left", fill="y")

        acciones_vehiculos = ttk.Frame(frame_lista_vehiculos)
        acciones_vehiculos.pack(side="left", fill="y", padx=(6, 0))
        ttk.Button(acciones_vehiculos, text="Agregar vehículo", command=self._agregar_vehiculo).pack(fill="x", pady=2)
        ttk.Button(acciones_vehiculos, text="Editar vehículo", command=self._editar_vehiculo).pack(fill="x", pady=2)
        ttk.Button(acciones_vehiculos, text="Eliminar vehículo", command=self._eliminar_vehiculo).pack(fill="x", pady=2)
        ttk.Separator(acciones_vehiculos, orient="horizontal").pack(fill="x", pady=4)
        ttk.Button(acciones_vehiculos, text="Asignar paquete", command=self._asignar_paquete).pack(fill="x", pady=2)
        ttk.Button(acciones_vehiculos, text="Retirar paquete", command=self._retirar_paquete).pack(fill="x", pady=2)

        self.txt_resultados = tk.Text(frame_derecho, height=6, wrap="word", font=("Consolas", 9))
        self.txt_resultados.pack(fill="x", padx=5, pady=(0, 5))

        self.frame_grafica = ttk.LabelFrame(frame_derecho, text=" Métricas de Rendimiento ", padding=5)
        self.frame_grafica.pack(fill="both", expand=True, padx=5)

    def _vehiculo_seleccionado(self):
        seleccion = self.tabla_vehiculos.selection()
        if not seleccion:
            return None
        return next((vehiculo for vehiculo in self.vehiculos if str(id(vehiculo)) == seleccion[0]), None)

    def _paquete_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            return None
        return next((paquete for paquete in self.paquetes if str(id(paquete)) == seleccion[0]), None)

    def _agregar_vehiculo(self, nombre=None, capacidad=None):
        if nombre is None:
            self._mostrar_dialogo_vehiculo()
            return
        vehiculo = Vehiculo(nombre, capacidad)
        self.vehiculos.append(vehiculo)
        self._actualizar_tabla_vehiculos(vehiculo)

    def _mostrar_dialogo_vehiculo(self, vehiculo=None):
        dialogo = tk.Toplevel(self)
        dialogo.title("Editar vehículo" if vehiculo else "Agregar vehículo")
        dialogo.transient(self)
        dialogo.resizable(False, False)
        dialogo.grab_set()
        campos = (("Nombre", "nombre"), ("Capacidad (kg)", "capacidad"))
        entradas = {}
        valores = {
            "nombre": vehiculo.nombre if vehiculo else f"Vehículo {len(self.vehiculos) + 1}",
            "capacidad": f"{vehiculo.capacidad:g}" if vehiculo else "500",
        }
        for fila, (etiqueta, clave) in enumerate(campos):
            ttk.Label(dialogo, text=etiqueta).grid(row=fila, column=0, padx=12, pady=6, sticky="w")
            entrada = ttk.Entry(dialogo, width=24)
            entrada.insert(0, valores[clave])
            entrada.grid(row=fila, column=1, padx=12, pady=6)
            entradas[clave] = entrada

        def guardar():
            nombre = entradas["nombre"].get().strip()
            try:
                capacidad = float(entradas["capacidad"].get())
                if not nombre or capacidad <= 0:
                    raise ValueError("Ingrese un nombre y una capacidad mayor que cero.")
                if any(
                    otro is not vehiculo and otro.nombre.casefold() == nombre.casefold()
                    for otro in self.vehiculos
                ):
                    raise ValueError("Ya existe un vehículo con ese nombre.")
                if vehiculo:
                    vehiculo.actualizar(nombre, capacidad)
                else:
                    self.vehiculos.append(Vehiculo(nombre, capacidad))
            except ValueError as error:
                messagebox.showerror("Datos inválidos", str(error), parent=dialogo)
                return
            dialogo.destroy()
            self._actualizar_tabla_vehiculos(vehiculo or self.vehiculos[-1])
            self._actualizar_tabla_paquetes()

        botones = ttk.Frame(dialogo)
        botones.grid(row=len(campos), column=0, columnspan=2, pady=(8, 12))
        ttk.Button(botones, text="Cancelar", command=dialogo.destroy).pack(side="left", padx=5)
        ttk.Button(botones, text="Guardar", command=guardar).pack(side="left", padx=5)
        entradas["nombre"].focus_set()

    def _editar_vehiculo(self):
        vehiculo = self._vehiculo_seleccionado()
        if vehiculo is None:
            messagebox.showinfo("Vehículos", "Seleccione un vehículo para editarlo.")
            return
        self._mostrar_dialogo_vehiculo(vehiculo)

    def _eliminar_vehiculo(self):
        vehiculo = self._vehiculo_seleccionado()
        if vehiculo is None:
            messagebox.showinfo("Vehículos", "Seleccione un vehículo para eliminarlo.")
            return
        if len(self.vehiculos) == 1:
            messagebox.showwarning("Vehículos", "Debe conservar al menos un vehículo registrado.")
            return
        if vehiculo.paquetes and not messagebox.askyesno(
            "Eliminar vehículo",
            f"{vehiculo.nombre} tiene {len(vehiculo.paquetes)} paquete(s). "
            "Se liberarán para que puedan asignarse a otro vehículo. ¿Continuar?"
        ):
            return
        self.vehiculos.remove(vehiculo)
        self._actualizar_tabla_vehiculos()
        self._actualizar_tabla_paquetes()

    def _actualizar_tabla_vehiculos(self, seleccionado=None):
        for fila in self.tabla_vehiculos.get_children():
            self.tabla_vehiculos.delete(fila)
        for vehiculo in self.vehiculos:
            etiqueta = "completa" if vehiculo.estado == "Capacidad alcanzada" else (
                "cerca" if vehiculo.estado == "Cerca del límite" else "baja"
            )
            self.tabla_vehiculos.insert(
                "", "end", iid=str(id(vehiculo)),
                values=(
                    vehiculo.nombre,
                    f"{vehiculo.capacidad:.2f} kg",
                    f"{vehiculo.peso_actual:.2f} kg",
                    f"{vehiculo.disponible:.2f} kg",
                    f"{vehiculo.ocupacion:.1f}%",
                    vehiculo.estado,
                ),
                tags=(etiqueta,)
            )
        if seleccionado in self.vehiculos:
            self.tabla_vehiculos.selection_set(str(id(seleccionado)))
            self.tabla_vehiculos.focus(str(id(seleccionado)))
        elif self.vehiculos:
            primer_id = str(id(self.vehiculos[0]))
            self.tabla_vehiculos.selection_set(primer_id)
        self._actualizar_estado_seleccionado()

    def _actualizar_estado_seleccionado(self):
        vehiculo = self._vehiculo_seleccionado()
        if vehiculo is None:
            self.etiqueta_estado.configure(text="Seleccione un vehículo")
            self.etiqueta_carga.configure(text="")
            color = "#d64a4a"
        else:
            self.etiqueta_estado.configure(text=f"{vehiculo.nombre}: {vehiculo.estado}")
            self.etiqueta_carga.configure(
                text=(
                    f"Carga: {vehiculo.peso_actual:.2f} kg     "
                    f"Disponible: {vehiculo.disponible:.2f} kg     "
                    f"Ocupación: {vehiculo.ocupacion:.1f}%"
                )
            )
            color = "#2e9d59" if vehiculo.estado == "Capacidad alcanzada" else (
                "#e0aa17" if vehiculo.estado == "Cerca del límite" else "#d64a4a"
            )
        self.indicador_estado.itemconfigure(self.indicador_estado_id, fill=color)

    def _actualizar_tabla_paquetes(self, seleccionado=None):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for paquete in self.paquetes:
            asignado = next(
                (vehiculo.nombre for vehiculo in self.vehiculos if paquete in vehiculo.paquetes),
                "Disponible"
            )
            self.tabla.insert(
                "", "end", iid=str(id(paquete)),
                values=(paquete.id_paquete, f"{paquete.peso:.2f}", f"{paquete.valor:.2f}",
                        f"{paquete.ratio:.2f}", asignado)
            )
        if seleccionado in self.paquetes:
            self.tabla.selection_set(str(id(seleccionado)))

    def _mostrar_dialogo_paquete(self, paquete_original=None):
        dialogo = tk.Toplevel(self)
        dialogo.title("Editar paquete" if paquete_original else "Agregar paquete")
        dialogo.transient(self)
        dialogo.resizable(False, False)
        dialogo.grab_set()

        paquete_agregado = False
        valores_iniciales = {
            "id": paquete_original.id_paquete if paquete_original else "",
            "peso": f"{paquete_original.peso:g}" if paquete_original else "",
            "valor": f"{paquete_original.valor:g}" if paquete_original else "",
        }
        campos = (("ID", "id"), ("Peso (kg)", "peso"), ("Valor ($)", "valor"))
        entradas = {}
        for fila, (etiqueta, clave) in enumerate(campos):
            ttk.Label(dialogo, text=etiqueta).grid(row=fila, column=0, padx=12, pady=6, sticky="w")
            entrada = ttk.Entry(dialogo, width=24)
            entrada.insert(0, valores_iniciales[clave])
            entrada.grid(row=fila, column=1, padx=12, pady=6)
            entradas[clave] = entrada

        def guardar_paquete():
            nonlocal paquete_agregado
            id_paquete = entradas["id"].get().strip()
            try:
                peso = float(entradas["peso"].get())
                valor = float(entradas["valor"].get())
                if not id_paquete or not isfinite(peso) or peso <= 0 or not isfinite(valor) or valor < 0:
                    raise ValueError("Ingrese un ID, un peso mayor que cero y un valor igual o mayor que cero.")
            except ValueError as error:
                messagebox.showerror(
                    "Datos inválidos",
                    str(error) or "El peso y el valor deben ser números válidos.",
                    parent=dialogo
                )
                return

            if any(
                existente is not paquete_original
                and existente.id_paquete.casefold() == id_paquete.casefold()
                for existente in self.paquetes
            ):
                messagebox.showerror("ID duplicado", "Ya existe un paquete con ese ID.", parent=dialogo)
                return

            paquete_nuevo = Paquete(id_paquete, peso, valor)
            if paquete_original:
                vehiculo_asignado = next(
                    (vehiculo for vehiculo in self.vehiculos if paquete_original in vehiculo.paquetes), None
                )
                if vehiculo_asignado and (
                    vehiculo_asignado.peso_actual - paquete_original.peso + paquete_nuevo.peso
                    > vehiculo_asignado.capacidad + 1e-9
                ):
                    messagebox.showerror(
                        "Capacidad excedida",
                        f"El cambio dejaría a {vehiculo_asignado.nombre} por encima de su capacidad.",
                        parent=dialogo
                    )
                    return
                posicion = self.paquetes.index(paquete_original)
                self.paquetes[posicion] = paquete_nuevo
                if vehiculo_asignado:
                    indice = vehiculo_asignado.paquetes.index(paquete_original)
                    vehiculo_asignado.paquetes[indice] = paquete_nuevo
            else:
                self.paquetes.append(paquete_nuevo)
            paquete_agregado = True
            dialogo.destroy()
            self._actualizar_tabla_paquetes(paquete_nuevo)
            self._actualizar_tabla_vehiculos(self._vehiculo_seleccionado())

        botones = ttk.Frame(dialogo)
        botones.grid(row=len(campos), column=0, columnspan=2, pady=(8, 12))
        ttk.Button(botones, text="Cancelar", command=dialogo.destroy).pack(side="left", padx=5)
        ttk.Button(
            botones,
            text="Guardar cambios" if paquete_original else "Agregar",
            command=guardar_paquete
        ).pack(side="left", padx=5)
        entradas["id"].focus_set()
        self.wait_window(dialogo)
        return paquete_agregado

    def _editar_paquete(self):
        paquete = self._paquete_seleccionado()
        if paquete is None:
            messagebox.showinfo("Paquetes", "Seleccione un paquete para editarlo.")
            return
        self._mostrar_dialogo_paquete(paquete)

    def _quitar_paquete(self):
        paquete = self._paquete_seleccionado()
        if paquete is None:
            messagebox.showinfo("Paquetes", "Seleccione un paquete para quitarlo.")
            return
        if not messagebox.askyesno("Quitar paquete", f"¿Desea eliminar el paquete {paquete.id_paquete}?"):
            return
        for vehiculo in self.vehiculos:
            vehiculo.quitar_paquete(paquete.id_paquete)
        self.paquetes.remove(paquete)
        self._actualizar_tabla_paquetes()
        self._actualizar_tabla_vehiculos(self._vehiculo_seleccionado())

    def _asignar_paquete(self):
        paquete = self._paquete_seleccionado()
        vehiculo = self._vehiculo_seleccionado()
        if paquete is None or vehiculo is None:
            messagebox.showinfo("Asignación", "Seleccione un paquete y un vehículo.")
            return
        if any(paquete in otro.paquetes for otro in self.vehiculos):
            messagebox.showwarning("Asignación", "Retire el paquete de su vehículo actual antes de reasignarlo.")
            return
        try:
            vehiculo.agregar_paquete(paquete)
        except ValueError as error:
            messagebox.showwarning("Capacidad excedida", str(error))
            return
        self._actualizar_tabla_paquetes(paquete)
        self._actualizar_tabla_vehiculos(vehiculo)

    def _retirar_paquete(self):
        paquete = self._paquete_seleccionado()
        if paquete is None:
            messagebox.showinfo("Asignación", "Seleccione el paquete que desea retirar.")
            return
        vehiculo = next((item for item in self.vehiculos if paquete in item.paquetes), None)
        if vehiculo is None:
            messagebox.showinfo("Asignación", "El paquete seleccionado no está asignado a un vehículo.")
            return
        vehiculo.quitar_paquete(paquete.id_paquete)
        self._actualizar_tabla_paquetes(paquete)
        self._actualizar_tabla_vehiculos(vehiculo)

    def _cargar_csv(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos CSV", "*.csv")])
        if not ruta:
            return

        try:
            with open(ruta, mode="r", encoding="utf-8") as archivo:
                reader = csv.DictReader(archivo)
                paquetes_nuevos = []
                ids = set()
                for fila in reader:
                    paquete = Paquete(fila["id"], float(fila["peso"]), float(fila["valor"]))
                    if not paquete.id_paquete.strip() or paquete.peso <= 0 or paquete.valor < 0:
                        raise ValueError("Cada paquete debe tener ID, peso positivo y valor no negativo.")
                    if paquete.id_paquete.casefold() in ids:
                        raise ValueError(f"El archivo contiene un ID duplicado: {paquete.id_paquete}.")
                    ids.add(paquete.id_paquete.casefold())
                    paquetes_nuevos.append(paquete)
        except Exception as error:
            messagebox.showerror("Error de lectura", f"No se pudo leer el archivo CSV:\n{error}")
            return

        if any(vehiculo.paquetes for vehiculo in self.vehiculos):
            reemplazar = messagebox.askyesno(
                "Reemplazar manifiesto",
                "Cargar otro CSV quitará las asignaciones actuales de los vehículos. ¿Desea continuar?"
            )
            if not reemplazar:
                return
        for vehiculo in self.vehiculos:
            vehiculo.paquetes.clear()
        self.paquetes = paquetes_nuevos
        self._actualizar_tabla_paquetes()
        self._actualizar_tabla_vehiculos(self._vehiculo_seleccionado())
        messagebox.showinfo("Éxito", f"Se cargaron {len(self.paquetes)} paquetes correctamente.")

    def _ejecutar(self):
        if not self.paquetes:
            messagebox.showwarning("Aviso", "Primero cargue un CSV o agregue paquetes.")
            return
        if not self.vehiculos:
            messagebox.showwarning("Aviso", "Agregue al menos un vehículo.")
            return

        seleccion = self.combo_algoritmo.get()
        algoritmos = {
            "Fuerza Bruta": resolver_fuerza_bruta,
            "Voraz (Greedy)": resolver_voraz,
            "Backtracking": resolver_backtracking,
            "Programación Dinámica": resolver_programacion_dinamica,
        }
        if seleccion not in algoritmos and seleccion != "Comparar Todos":
            messagebox.showwarning("Aviso", "Seleccione un algoritmo para ejecutar.")
            return

        paquetes_asignados = [paquete for vehiculo in self.vehiculos for paquete in vehiculo.paquetes]
        reoptimizar = bool(paquetes_asignados) and messagebox.askyesno(
            "Reoptimizar flota",
            "Ya hay paquetes asignados. ¿Desea liberar todas las cargas para recalcular la distribución?\n\n"
            "Si responde No, la optimización conservará las cargas actuales y usará solo paquetes disponibles."
        )
        paquetes_disponibles = list(self.paquetes) if reoptimizar else [
            paquete for paquete in self.paquetes
            if not any(paquete in vehiculo.paquetes for vehiculo in self.vehiculos)
        ]
        if not paquetes_disponibles:
            messagebox.showinfo("Optimización", "Todos los paquetes ya están asignados a la flota.")
            return

        nombres_seleccionados = list(algoritmos) if seleccion == "Comparar Todos" else [seleccion]
        if len(paquetes_disponibles) > self.MAX_PAQUETES_EXHAUSTIVOS and any(
            nombre in self.ALGORITMOS_EXHAUSTIVOS for nombre in nombres_seleccionados
        ):
            combinaciones = 2 ** len(paquetes_disponibles)
            messagebox.showwarning(
                "Límite de búsqueda exhaustiva",
                f"Con {len(paquetes_disponibles)} paquetes, la optimización evaluaría aproximadamente "
                f"{combinaciones:,} combinaciones posibles.\n\n"
                "Fuerza Bruta y Backtracking tienen complejidad exponencial (2^n), por lo que se limita "
                f"la entrada a {self.MAX_PAQUETES_EXHAUSTIVOS} paquetes para mantener la aplicación estable.\n\n"
                "Seleccione Voraz o Programación Dinámica para trabajar con conjuntos más grandes."
            )
            return

        if reoptimizar:
            for vehiculo in self.vehiculos:
                vehiculo.paquetes.clear()

        capacidades = [vehiculo.capacidad if reoptimizar else vehiculo.disponible for vehiculo in self.vehiculos]
        self.txt_resultados.delete("1.0", tk.END)
        resultados = []
        nombres_grafica = []
        tiempos_grafica = []

        for nombre in nombres_seleccionados:
            resolver = algoritmos[nombre]
            paquetes_restantes = list(paquetes_disponibles)
            distribucion = []
            tiempo_total = 0.0

            for vehiculo, capacidad_libre in zip(self.vehiculos, capacidades):
                items, peso, valor, tiempo = resolver(paquetes_restantes, capacidad_libre)
                ids_seleccionados = {paquete.id_paquete.casefold() for paquete in items}
                paquetes_restantes = [
                    paquete for paquete in paquetes_restantes
                    if paquete.id_paquete.casefold() not in ids_seleccionados
                ]
                espacio_libre = max(0.0, capacidad_libre - peso)
                distribucion.append((vehiculo, items, peso, valor, tiempo, espacio_libre))
                tiempo_total += tiempo
                self._mostrar_resumen(
                    f"{nombre} | {vehiculo.nombre}", items, peso, valor, tiempo, espacio_libre
                )

            valor_total = sum(resultado[3] for resultado in distribucion)
            resultados.append((nombre, valor_total, distribucion))
            nombres_grafica.append(nombre)
            tiempos_grafica.append(tiempo_total)

        self._dibujar_grafica(nombres_grafica, tiempos_grafica)
        mejor_nombre, _, mejor_asignacion = max(resultados, key=lambda resultado: resultado[1])
        sobrecargados = [
            vehiculo.nombre
            for vehiculo, items, _, _, _, _ in mejor_asignacion
            if vehiculo.peso_actual + sum(paquete.peso for paquete in items) > vehiculo.capacidad + 1e-9
        ]
        if sobrecargados:
            messagebox.showerror(
                "Capacidad excedida",
                "No se aplicó la optimización porque excedería la capacidad de: " + ", ".join(sobrecargados)
            )
            return
        for vehiculo, items, _, _, _, _ in mejor_asignacion:
            for paquete in items:
                vehiculo.agregar_paquete(paquete)
        self.txt_resultados.insert(
            tk.END,
            f"Mejor distribución aplicada: {mejor_nombre}. Puede agregar, retirar o editar paquetes y vehículos.\n"
        )
        self._actualizar_tabla_paquetes()
        self._actualizar_tabla_vehiculos(self._vehiculo_seleccionado())

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