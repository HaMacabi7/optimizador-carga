import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generar_diagrama_ishikawa_opticarga():
    fig, ax = plt.subplots(figsize=(16.5, 9), dpi=300)
    fig.patch.set_facecolor('#0B132B')
    ax.set_facecolor('#0B132B')
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Paleta de colores
    c_linea_central = '#00B4D8'
    c_espina = '#0077B6'
    c_subespina = '#1D3E6E'
    c_texto_espina = '#FFFFFF'
    c_texto_causa = '#C5D3E8'
    c_caja_categoria = '#10254C'
    c_borde_categoria = '#00B4D8'
    c_rojo_borde = '#E63946'
    c_rojo_titulo = '#FF4D6D'

    # 1. TÍTULO SUPERIOR
    ax.text(0.6, 9.4, "DIAGRAMA DE ISHIKAWA — SISTEMA DE OPTIMIZACIÓN LOGÍSTICA (OPTICARGA)", 
            color='white', fontsize=13.5, fontweight='bold', ha='left', va='center')

    # 2. ESPINA CENTRAL HORIZONTAL
    ax.annotate("", xy=(12.3, 4.8), xytext=(0.6, 4.8),
                arrowprops=dict(arrowstyle="-|>", color=c_linea_central, lw=4.5, mutation_scale=28))

    # 3. CABEZA DEL PEZ (PROBLEMA PRINCIPAL)
    puntos_cabeza = [
        [12.6, 6.5],
        [16.0, 6.5],
        [16.0, 3.1],
        [12.6, 3.1],
        [12.2, 4.8]
    ]
    poligono = patches.Polygon(puntos_cabeza, closed=True, facecolor='#101F3C', 
                               edgecolor=c_rojo_borde, linewidth=2.5, zorder=3)
    ax.add_patch(poligono)

    ax.text(14.3, 5.8, "PROBLEMA PRINCIPAL", color=c_rojo_titulo, 
            fontsize=10.5, fontweight='bold', ha='center', va='center')
    
    texto_problema = (
        "Ineficiencia operativa,\n"
        "subutilización de carga\n"
        "y descontrol en la\n"
        "selección de paquetes de\n"
        "reparto en RutaSegura"
    )
    ax.text(14.3, 4.5, texto_problema, color='#FFFFFF', 
            fontsize=9.0, ha='center', va='center', linespacing=1.25)

    # 4. DIBUJAR ESPINAS 1 Y 2 (MÉTODOS, DATOS, MANO DE OBRA, MEDICIÓN)
    # Formato: (xc, xa, titulo_sup, causas_sup, titulo_inf, causas_inf)
    pares_izq = [
        (2.2, 3.6, "MÉTODOS", [
            "• Selección manual y empírica",
            "• Cálculo a prueba y error",
            "• Sin modelo matemático"
        ], "DATOS / MANIFIESTO", [
            "• Manifiestos no unificados",
            "• Sin cálculo de ratio $/kg",
            "• Disparidad peso vs valor"
        ]),
        (5.5, 6.9, "MANO DE OBRA", [
            "• Criterio subjetivo de carga",
            "• Fatiga mental en turnos punta",
            "• Desconocimiento Mochila 0/1"
        ], "MEDICIÓN Y CONTROL", [
            "• Riesgo de multas por peso",
            "• Descontrol de rentabilidad/viaje",
            "• Sin métricas de ocupación real"
        ])
    ]

    for xc, xa, tit_s, causas_s, tit_i, causas_i in pares_izq:
        # Superior
        ax.plot([xc, xa], [8.05, 4.8], color=c_espina, lw=2.5)
        ax.text(xc, 8.5, tit_s, color=c_texto_espina, fontsize=9.5, fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.5,rounding_size=0.3", facecolor=c_caja_categoria, edgecolor=c_borde_categoria, lw=1.8))
        
        y_sup = [7.3, 6.4, 5.5]
        for idx, y_n in enumerate(y_sup):
            x_d = xc + (y_n - 8.05) * ((xa - xc) / (4.8 - 8.05))
            ax.plot([x_d - 0.5, x_d], [y_n, y_n], color=c_subespina, lw=1.3, linestyle=":")
            ax.text(x_d - 0.6, y_n, causas_s[idx], color=c_texto_causa, fontsize=8.0, ha='right', va='center')

        # Inferior
        ax.plot([xc, xa], [1.55, 4.8], color=c_espina, lw=2.5)
        ax.text(xc, 1.1, tit_i, color=c_texto_espina, fontsize=9.5, fontweight='bold', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.5,rounding_size=0.3", facecolor=c_caja_categoria, edgecolor=c_borde_categoria, lw=1.8))
        
        y_inf = [4.1, 3.2, 2.3]
        for idx, y_n in enumerate(y_inf):
            x_d = xc + (y_n - 1.55) * ((xa - xc) / (4.8 - 1.55))
            ax.plot([x_d - 0.5, x_d], [y_n, y_n], color=c_subespina, lw=1.3, linestyle=":")
            ax.text(x_d - 0.6, y_n, causas_i[idx], color=c_texto_causa, fontsize=8.0, ha='right', va='center')

    # 5. ESPINA 3: TECNOLOGÍA Y LOGÍSTICA (TEXTOS A LA DERECHA, EN EL HUECO ROJO)
    xc3, xa3 = 8.8, 10.2

    # --- Superior: TECNOLOGÍA ---
    ax.plot([xc3, xa3], [8.05, 4.8], color=c_espina, lw=2.5)
    ax.text(xc3, 8.5, "TECNOLOGÍA", color=c_texto_espina, fontsize=9.5, fontweight='bold', ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.5,rounding_size=0.3", facecolor=c_caja_categoria, edgecolor=c_borde_categoria, lw=1.8))

    causas_tec = [
        "• Carencia de software automatizado",
        "• Planillas aisladas sin validación",
        "• Sin motor decisional integrado"
    ]
    y_sup_tec = [7.3, 6.4, 5.5]
    for idx, y_n in enumerate(y_sup_tec):
        x_d = xc3 + (y_n - 8.05) * ((xa3 - xc3) / (4.8 - 8.05))
        # Ramita punteada hacia la derecha
        ax.plot([x_d, x_d + 0.5], [y_n, y_n], color=c_subespina, lw=1.3, linestyle=":")
        # Texto colocado a la derecha exactamente en la zona indicada
        ax.text(x_d + 0.6, y_n, causas_tec[idx], color=c_texto_causa, fontsize=8.0, ha='left', va='center')

    # --- Inferior: LOGÍSTICA Y TIEMPOS ---
    ax.plot([xc3, xa3], [1.55, 4.8], color=c_espina, lw=2.5)
    ax.text(xc3, 1.1, "LOGÍSTICA Y TIEMPOS", color=c_texto_espina, fontsize=9.5, fontweight='bold', ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.5,rounding_size=0.3", facecolor=c_caja_categoria, edgecolor=c_borde_categoria, lw=1.8))

    causas_log = [
        "• Sobrecostos por viajes extras",
        "• Retrasos en ventanas de entrega",
        "• Demoras de 40 a 60 min en patio"
    ]
    y_inf_log = [4.1, 3.2, 2.3]
    for idx, y_n in enumerate(y_inf_log):
        x_d = xc3 + (y_n - 1.55) * ((xa3 - xc3) / (4.8 - 1.55))
        # Ramita punteada hacia la derecha
        ax.plot([x_d, x_d + 0.5], [y_n, y_n], color=c_subespina, lw=1.3, linestyle=":")
        # Texto colocado a la derecha en la zona indicada
        ax.text(x_d + 0.6, y_n, causas_log[idx], color=c_texto_causa, fontsize=8.0, ha='left', va='center')

    plt.tight_layout()
    plt.savefig("ishikawa_opticarga_dark.png", dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.show()
    print("✓ Diagrama generado con éxito. Los textos de Tecnología y Logística se ubicaron en la zona derecha.")

if __name__ == "__main__":
    generar_diagrama_ishikawa_opticarga()