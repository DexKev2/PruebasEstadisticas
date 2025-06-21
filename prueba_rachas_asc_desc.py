import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import norm


class RachasAscendentesDescendentes:
    def __init__(self, datos, alpha=0.05):
        self.datos = datos
        self.alpha = alpha
        self.N = len(datos)
        self.resultados = {}

    def ejecutar(self):
        # Paso 1: Identificar cambios de dirección
        direcciones = []
        for i in range(1, self.N):
            if self.datos[i] > self.datos[i-1]:
                direcciones.append(1)  # Ascendente
            elif self.datos[i] < self.datos[i-1]:
                direcciones.append(-1)  # Descendente
            else:
                # En caso de empate, mantener la dirección anterior
                if direcciones:
                    direcciones.append(direcciones[-1])
                else:
                    direcciones.append(1)  # Por defecto ascendente

        # Paso 2: Contar rachas (cambios de dirección)
        if not direcciones:
            # Si solo hay un dato
            rachas = []
            A = 0
            longitudes = []
        else:
            rachas = []
            racha_actual = [direcciones[0]]

            for i in range(1, len(direcciones)):
                if direcciones[i] == direcciones[i-1]:
                    racha_actual.append(direcciones[i])
                else:
                    rachas.append(racha_actual)
                    racha_actual = [direcciones[i]]

            rachas.append(racha_actual)

            # Número de rachas (A) es la cantidad de grupos
            A = len(rachas)
            longitudes = [len(r) for r in rachas]

        # Contar frecuencias de longitudes
        frecuencias = {}
        for lon in longitudes:
            frecuencias[lon] = frecuencias.get(lon, 0) + 1

        # Paso 3: Cálculos estadísticos
        mu_A = (2 * self.N - 1) / 3
        sigma2_A = (16 * self.N - 29) / 90
        sigma_A = np.sqrt(sigma2_A)
        Z_prueba = abs((A - mu_A) / sigma_A)
        Z_teorico = norm.ppf(1 - self.alpha / 2)

        # Paso 4: Resultado de la prueba
        rechaza_H0 = Z_prueba > Z_teorico

        # Almacenar resultados
        self.resultados = {
            'numero_rachas': A,  # ESTE ES EL ESTADÍSTICO A IMPORTANTE
            'suma_longitudes': sum(longitudes) if longitudes else 0,
            'longitud_maxima': max(longitudes) if longitudes else 0,
            'frecuencias_longitudes': frecuencias,
            'rachas': rachas,
            'mu_A': mu_A,
            'sigma2_A': sigma2_A,
            'sigma_A': sigma_A,
            'Z_prueba': Z_prueba,
            'Z_teorico': Z_teorico,
            'rechaza_H0': rechaza_H0,
            'tipo_prueba': 'Rachas Ascendentes/Descendentes',
            'alpha': self.alpha
        }

        return self.resultados

    def mostrar_tabla_detallada(self, parent=None):
        if not self.resultados:
            self.ejecutar()

        ventana = tk.Toplevel(parent)
        ventana.title("Detalle de Rachas Ascendentes/Descendentes")
        ventana.geometry("900x700")

        # Frame principal
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Resumen estadístico
        resumen = ttk.LabelFrame(
            main_frame, text="Resumen Estadístico", padding="10")
        resumen.pack(fill=tk.X, padx=5, pady=5)

        datos_resumen = [
            ("Número total de datos", self.N),
            ("Número de rachas (A)", self.resultados['numero_rachas']),
            ("Suma de longitudes", f"{self.resultados['suma_longitudes']}"),
            ("μ_A", f"{self.resultados['mu_A']:.4f}"),
            ("σ²_A", f"{self.resultados['sigma2_A']:.4f}"),
            ("σ_A", f"{self.resultados['sigma_A']:.4f}"),
            ("Z prueba", f"{self.resultados['Z_prueba']:.4f}"),
            ("Z teórico", f"{self.resultados['Z_teorico']:.4f}"),
            ("Nivel de significancia", f"{self.alpha}"),
            ("Resultado", "Rechaza H0 (No aleatorio)" if self.resultados['rechaza_H0']
                          else "Acepta H0 (Aleatorio)")
        ]

        for i, (label, valor) in enumerate(datos_resumen):
            ttk.Label(resumen, text=label, font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(resumen, text=valor).grid(
                row=i, column=1, sticky=tk.W, padx=5, pady=2)

        # Tabla de frecuencias de longitudes
        frame_frecuencias = ttk.LabelFrame(
            main_frame, text="Distribución de Longitudes de Rachas", padding="10")
        frame_frecuencias.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Crear tabla
        tree = ttk.Treeview(frame_frecuencias, columns=(
            'Longitud', 'Frecuencia'), show='headings')
        vsb = ttk.Scrollbar(frame_frecuencias,
                            orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        tree.heading('Longitud', text='Longitud')
        tree.heading('Frecuencia', text='Frecuencia')
        tree.column('Longitud', width=75, anchor=tk.CENTER)
        tree.column('Frecuencia', width=50, anchor=tk.CENTER)

        # Insertar datos
        for longitud, freq in self.resultados['frecuencias_longitudes'].items():
            tree.insert('', tk.END, values=(longitud, freq))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Gráfico de distribución de longitudes
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            longitudes = list(self.resultados['frecuencias_longitudes'].keys())
            frecuencias = list(
                self.resultados['frecuencias_longitudes'].values())

            # Ordenar por longitud para mejor visualización
            longitudes.sort()
            frecuencias = [self.resultados['frecuencias_longitudes'][lon]
                           for lon in longitudes]

            sns.barplot(x=longitudes, y=frecuencias, ax=ax,
                        palette="viridis", hue=longitudes, legend=False)
            ax.set_title('Distribución de Longitudes de Rachas')
            ax.set_xlabel('Longitud de Racha')
            ax.set_ylabel('Frecuencia')
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            # Añadir valores encima de las barras
            for i, v in enumerate(frecuencias):
                ax.text(i, v + 0.2, str(v), ha='center')

            plt.tight_layout()

            # Integrar gráfico en la interfaz
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            canvas = FigureCanvasTkAgg(fig, master=main_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            canvas.draw()
        except Exception as e:
            print(f"Error al crear gráfico: {e}")

        ventana.transient(parent)
        ventana.grab_set()
        parent.wait_window(ventana)


# Ejemplo de uso independiente (para pruebas)
if __name__ == "__main__":
    # Datos de ejemplo basados en tu archivo
    datos_ejemplo = np.array([
        0.811, 0.781, 0.046, 0.376, 0.502, 0.313, 0.318, 0.226,
        0.468, 0.319, 0.939, 0.547, 0.011, 0.981, 0.684, 0.839,
        0.047, 0.107, 0.609, 0.131, 0.461, 0.145, 0.208, 0.491,
        0.321, 0.775, 0.608, 0.342, 0.576, 0.598, 0.493, 0.156,
        0.344, 0.214, 0.195, 0.883, 0.18, 0.348, 0.285, 0.494
    ])

    prueba = RachasAscendentesDescendentes(datos_ejemplo, alpha=0.10)
    resultados = prueba.ejecutar()

    print("Resultados de la prueba de rachas ascendentes/descendentes:")
    print(f"Número de rachas (A): {resultados['numero_rachas']}")
    print(f"Suma de longitudes: {resultados['suma_longitudes']}")
    print(f"Frecuencias: {resultados['frecuencias_longitudes']}")
    print(f"μ_A: {resultados['mu_A']:.4f}")
    print(f"σ²_A: {resultados['sigma2_A']:.4f}")
    print(f"σ_A: {resultados['sigma_A']:.4f}")
    print(f"Z prueba: {resultados['Z_prueba']:.4f}")
    print(f"Z teórico: {resultados['Z_teorico']:.4f}")
    print(f"Rechaza H0: {'Sí' if resultados['rechaza_H0'] else 'No'}")

    # Mostrar tabla detallada
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    prueba.mostrar_tabla_detallada(parent=root)
    root.mainloop()
