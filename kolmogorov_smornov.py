import numpy as np
import pandas as pd
from scipy import stats
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PruebaKS:
    def __init__(self, datos, num_intervalos=10, alpha=0.05):
        self.datos = np.array(datos)
        self.num_intervalos = num_intervalos
        self.alpha = alpha
        self.n = len(datos)
        
        # Tabla de valores críticos para Kolmogorov-Smirnov
        self.tabla_ks = {
            0.10: 1.22,
            0.05: 1.36,
            0.025: 1.48,
            0.01: 1.63,
            0.005: 1.73,
            0.001: 1.95
        }
    
    def calcular_frecuencias_acumuladas(self):
        """Calcular frecuencias acumuladas observadas y teóricas"""
        datos_ordenados = np.sort(self.datos)

        min_val = np.min(self.datos)
        max_val = np.max(self.datos)
        
        # Crear límites con pequeño epsilon para mantener exclusión del límite superior
        limites = np.linspace(min_val, max_val + 1e-10, self.num_intervalos + 1)

        # Calcular frecuencias observadas en los intervalos [a, b)
        freq_obs, _ = np.histogram(self.datos, bins=limites)

        # Frecuencia acumulada observada (proporción)
        freq_acum_obs = np.cumsum(freq_obs) / self.n

        # Evaluar la acumulada teórica en los límites superiores de cada intervalo
        limites_superiores = limites[1:]  # Los bordes derechos
        freq_acum_teorica = (limites_superiores - min_val) / (max_val - min_val)

        return limites, freq_obs, freq_acum_obs, freq_acum_teorica, limites_superiores

    
    def calcular_estadistico_ks(self):
        """Calcular estadístico de Kolmogorov-Smirnov"""
        limites, freq_obs, freq_acum_obs, freq_acum_teorica, puntos_medios = self.calcular_frecuencias_acumuladas()
        
        # Calcular diferencias absolutas
        diferencias = np.abs(freq_acum_obs - freq_acum_teorica)
        
        # El estadístico KS es la máxima diferencia
        d_max = np.max(diferencias)
        
        return d_max, limites, freq_obs, freq_acum_obs, freq_acum_teorica, puntos_medios, diferencias
    
    def obtener_valor_critico(self):
        """Obtener valor crítico para la prueba KS"""
        # Valor crítico aproximado: K_alpha / sqrt(n)
        if self.alpha in self.tabla_ks:
            k_alpha = self.tabla_ks[self.alpha]
        else:
            # Interpolación o aproximación
            if self.alpha <= 0.001:
                k_alpha = 1.95
            elif self.alpha <= 0.005:
                k_alpha = 1.73
            elif self.alpha <= 0.01:
                k_alpha = 1.63
            elif self.alpha <= 0.025:
                k_alpha = 1.48
            elif self.alpha <= 0.05:
                k_alpha = 1.36
            else:
                k_alpha = 1.22
        
        return k_alpha / np.sqrt(self.n)
    
    def ejecutar(self):
        """Ejecutar la prueba de Kolmogorov-Smirnov"""
        try:
            d_max, limites, freq_obs, freq_acum_obs, freq_acum_teorica, puntos_medios, diferencias = self.calcular_estadistico_ks()
            valor_critico = self.obtener_valor_critico()
            
            # También usar scipy para comparar
            datos_normalizados = (self.datos - np.min(self.datos)) / (np.max(self.datos) - np.min(self.datos))
            ks_stat_scipy, p_valor_scipy = stats.kstest(datos_normalizados, 'uniform')
            
            # Decisión de la prueba
            rechaza_h0 = d_max > valor_critico
            
            resultado = {
                'estadistico': d_max,
                'valor_critico': valor_critico,
                'p_valor': p_valor_scipy,
                'rechaza_h0': rechaza_h0,
                'limites': limites,
                'frecuencias_observadas': freq_obs,
                'frecuencias_acumuladas_obs': freq_acum_obs,
                'frecuencias_acumuladas_teorica': freq_acum_teorica,
                'puntos_medios': puntos_medios,
                'diferencias': diferencias,
                'tipo_prueba': 'Kolmogorov-Smirnov',
                'alpha': self.alpha,
                'n': self.n
            }
            
            return resultado
            
        except Exception as e:
            raise Exception(f"Error en prueba Kolmogorov-Smirnov: {str(e)}")
    
    def mostrar_tabla_detallada(self, parent=None):
        """Mostrar tabla detallada de la prueba KS"""
        ventana = tk.Toplevel(parent) if parent else tk.Tk()
        ventana.title("Tabla Detallada - Kolmogorov-Smirnov")
        ventana.geometry("900x700")
        
        # Ejecutar la prueba para obtener datos
        resultado = self.ejecutar()
        
        # Frame principal
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        titulo = ttk.Label(main_frame, text="Prueba Kolmogorov-Smirnov - Tabla Detallada", 
                          font=("Arial", 14, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Crear tabla
        columns = ('Intervalo', 'Límite Inf', 'Límite Sup', 'Punto Medio', 'Fi', 'Fi Acum Obs', 'Fi Acum Teór', '|Diferencia|')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=12)
        
        # Definir encabezados y anchos
        anchos = [80, 100, 100, 100, 60, 100, 100, 100]
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=anchos[i], anchor='center')
        
        # Llenar datos
        limites = resultado['limites']
        freq_obs = resultado['frecuencias_observadas']
        freq_acum_obs = resultado['frecuencias_acumuladas_obs']
        freq_acum_teorica = resultado['frecuencias_acumuladas_teorica']
        puntos_medios = resultado['puntos_medios']
        diferencias = resultado['diferencias']
        
        for i in range(len(freq_obs)):
            tree.insert('', 'end', values=(
                f"Int {i+1}",
                f"{limites[i]:.4f}",
                f"{limites[i+1]:.4f}",
                f"{puntos_medios[i]:.4f}",
                f"{freq_obs[i]}",
                f"{freq_acum_obs[i]:.4f}",
                f"{freq_acum_teorica[i]:.4f}",
                f"{diferencias[i]:.4f}"
            ))
        
        # Destacar la máxima diferencia
        max_diff_idx = np.argmax(diferencias)
        tree.set(tree.get_children()[max_diff_idx], columns[-1], f"{diferencias[max_diff_idx]:.4f} ←MAX")
        
        tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        
        # Resultados
        frame_resultados = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        frame_resultados.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(frame_resultados, text=f"D máximo: {resultado['estadistico']:.6f}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(frame_resultados, text=f"Valor crítico: {resultado['valor_critico']:.6f}").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(frame_resultados, text=f"P-valor: {resultado['p_valor']:.6f}").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(frame_resultados, text=f"Nivel de significancia: {self.alpha}").grid(row=3, column=0, sticky=tk.W)
        
        # Decisión
        decision_text = "Se RECHAZA H0" if resultado['rechaza_h0'] else "NO se rechaza H0"
        color = "red" if resultado['rechaza_h0'] else "green"
        decision_label = ttk.Label(frame_resultados, text=f"Decisión: {decision_text}", 
                                  foreground=color, font=("Arial", 10, "bold"))
        decision_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        # Gráfico
        self.crear_grafico_ks(main_frame, resultado)
        
        # Configurar weights
        ventana.columnconfigure(0, weight=1)
        ventana.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        return ventana
    
    def crear_grafico_ks(self, parent, resultado):
        """Crear gráfico de funciones de distribución acumulada"""
        # Frame para el gráfico
        frame_grafico = ttk.LabelFrame(parent, text="Función de Distribución Acumulada", padding="5")
        frame_grafico.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Crear figura con subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Gráfico 1: Funciones de distribución acumulada
        puntos_medios = resultado['puntos_medios']
        freq_acum_obs = resultado['frecuencias_acumuladas_obs']
        freq_acum_teorica = resultado['frecuencias_acumuladas_teorica']
        
        ax1.plot(puntos_medios, freq_acum_obs, 'o-', label='Observada', color='blue', linewidth=2)
        ax1.plot(puntos_medios, freq_acum_teorica, 's-', label='Teórica (Uniforme)', color='red', linewidth=2)
        
        # Líneas verticales para mostrar diferencias
        for i, (x, y_obs, y_teo) in enumerate(zip(puntos_medios, freq_acum_obs, freq_acum_teorica)):
            ax1.plot([x, x], [y_obs, y_teo], 'k--', alpha=0.5, linewidth=1)
        
        ax1.set_xlabel('Valor')
        ax1.set_ylabel('Probabilidad Acumulada')
        ax1.set_title('Funciones de Distribución Acumulada')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)
        
        # Gráfico 2: Diferencias absolutas
        diferencias = resultado['diferencias']
        bars = ax2.bar(range(len(diferencias)), diferencias, alpha=0.7, color='orange')
        
        # Destacar la máxima diferencia
        max_idx = np.argmax(diferencias)
        bars[max_idx].set_color('red')
        bars[max_idx].set_alpha(1.0)
        
        # Línea del valor crítico
        ax2.axhline(y=resultado['valor_critico'], color='red', linestyle='--', 
                   label=f'Valor crítico = {resultado["valor_critico"]:.4f}')
        
        ax2.set_xlabel('Intervalo')
        ax2.set_ylabel('|Diferencia|')
        ax2.set_title('Diferencias Absolutas')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(range(len(diferencias)))
        ax2.set_xticklabels([f'Int{i+1}' for i in range(len(diferencias))])
        
        # Agregar texto con el valor máximo
        ax2.text(max_idx, diferencias[max_idx] + 0.01, 
                f'MAX\n{diferencias[max_idx]:.4f}', 
                ha='center', va='bottom', fontweight='bold', color='red')
        
        plt.tight_layout()
        
        # Integrar en tkinter
        canvas = FigureCanvasTkAgg(fig, frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def main():
    """Función para probar el módulo independientemente"""
    # Generar datos de prueba
    np.random.seed(42)
    datos_test = np.random.uniform(0, 1, 100)
    
    # Crear y ejecutar prueba
    prueba = PruebaKS(datos_test, num_intervalos=10, alpha=0.05)
    resultado = prueba.ejecutar()
    
    print("Prueba Kolmogorov-Smirnov")
    print("=" * 30)
    print(f"Estadístico D: {resultado['estadistico']:.6f}")
    print(f"Valor crítico: {resultado['valor_critico']:.6f}")
    print(f"P-valor: {resultado['p_valor']:.6f}")
    print(f"¿Rechaza H0?: {resultado['rechaza_h0']}")
    
    # Mostrar tabla detallada
    ventana = prueba.mostrar_tabla_detallada()
    ventana.mainloop()

if __name__ == "__main__":
    main()