import numpy as np
import pandas as pd
from scipy import stats
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PruebaChi:
    def __init__(self, datos, num_intervalos=10, alpha=0.05):
        self.datos = np.array(datos)
        self.num_intervalos = num_intervalos
        self.alpha = alpha
        self.n = len(datos)
        
        # Tabla Chi-cuadrado (valores críticos)
        self.tabla_chi = {
            1: {0.005: 7.88, 0.01: 6.63, 0.025: 5.02, 0.05: 3.84, 0.10: 2.71, 0.20: 1.64, 0.90: 0.02, 0.95: 0.00, 0.975: 0.00, 0.99: 0.00, 0.995: 0.00},
            2: {0.005: 10.60, 0.01: 9.21, 0.025: 7.38, 0.05: 5.99, 0.10: 4.61, 0.20: 3.22, 0.90: 0.21, 0.95: 0.10, 0.975: 0.05, 0.99: 0.02, 0.995: 0.01},
            3: {0.005: 12.84, 0.01: 11.34, 0.025: 9.35, 0.05: 7.81, 0.10: 6.25, 0.20: 4.64, 0.90: 0.58, 0.95: 0.35, 0.975: 0.22, 0.99: 0.11, 0.995: 0.07},
            4: {0.005: 14.86, 0.01: 13.28, 0.025: 11.14, 0.05: 9.49, 0.10: 7.78, 0.20: 5.99, 0.90: 1.06, 0.95: 0.71, 0.975: 0.48, 0.99: 0.30, 0.995: 0.21},
            5: {0.005: 16.75, 0.01: 15.09, 0.025: 12.83, 0.05: 11.07, 0.10: 9.24, 0.20: 7.29, 0.90: 1.61, 0.95: 1.15, 0.975: 0.83, 0.99: 0.55, 0.995: 0.41},
            6: {0.005: 18.55, 0.01: 16.81, 0.025: 14.45, 0.05: 12.59, 0.10: 10.64, 0.20: 8.56, 0.90: 2.20, 0.95: 1.64, 0.975: 1.24, 0.99: 0.87, 0.995: 0.68},
            7: {0.005: 20.28, 0.01: 18.48, 0.025: 16.01, 0.05: 14.07, 0.10: 12.02, 0.20: 9.80, 0.90: 2.83, 0.95: 2.17, 0.975: 1.69, 0.99: 1.24, 0.995: 0.99},
            8: {0.005: 21.95, 0.01: 20.09, 0.025: 17.53, 0.05: 15.51, 0.10: 13.36, 0.20: 11.03, 0.90: 3.49, 0.95: 2.73, 0.975: 2.18, 0.99: 1.65, 0.995: 1.34},
            9: {0.005: 23.59, 0.01: 21.67, 0.025: 19.02, 0.05: 16.92, 0.10: 14.68, 0.20: 12.24, 0.90: 4.17, 0.95: 3.33, 0.975: 2.70, 0.99: 2.09, 0.995: 1.73},
            10: {0.005: 25.19, 0.01: 23.21, 0.025: 20.48, 0.05: 18.31, 0.10: 15.99, 0.20: 13.44, 0.90: 4.87, 0.95: 3.94, 0.975: 3.25, 0.99: 2.56, 0.995: 2.16}
        }
        
    def calcular_intervalos(self):
        """Dividir el intervalo [0, 1) en num_intervalos iguales sin incluir el extremo derecho"""

        # Dividir [0, 1) en num_intervalos con np.linspace excluyendo el 1.0
        step = 1 / self.num_intervalos
        limites = np.arange(0, 1 + 1e-10, step)  # Agrega un epsilon para asegurar inclusión final en np.histogram

        # Frecuencias observadas (solo cuenta valores >= lim_inf y < lim_sup)
        datos_filtrados = self.datos[self.datos < 1.0]  # Evitar que 1.0 entre al último intervalo
        freq_observadas, _ = np.histogram(datos_filtrados, bins=limites)

        # Frecuencia esperada uniforme
        freq_esperada = self.n / self.num_intervalos

        return limites, freq_observadas, freq_esperada
    
    def calcular_estadistico(self):
        """Calcular estadístico Chi-cuadrado"""
        limites, freq_obs, freq_esp = self.calcular_intervalos()
        
        # Calcular Chi-cuadrado
        chi_cuadrado = np.sum((freq_obs - freq_esp) ** 2 / freq_esp)
        
        # Grados de libertad
        grados_libertad = self.num_intervalos - 1
        
        return chi_cuadrado, grados_libertad, limites, freq_obs, freq_esp
    
    def obtener_valor_critico(self, grados_libertad):
        """Obtener valor crítico de la tabla Chi-cuadrado"""
        if grados_libertad in self.tabla_chi:
            if self.alpha in self.tabla_chi[grados_libertad]:
                return self.tabla_chi[grados_libertad][self.alpha]
        
        # Si no está en la tabla, usar scipy
        return stats.chi2.ppf(1 - self.alpha, grados_libertad)
    
    def ejecutar(self):
        """Ejecutar la prueba Chi-cuadrado"""
        try:
            chi_stat, gl, limites, freq_obs, freq_esp = self.calcular_estadistico()
            valor_critico = self.obtener_valor_critico(gl)
            
            # Calcular p-valor
            p_valor = 1 - stats.chi2.cdf(chi_stat, gl)
            
            # Decisión de la prueba
            rechaza_h0 = chi_stat > valor_critico
            
            resultado = {
                'estadistico': chi_stat,
                'grados_libertad': gl,
                'valor_critico': valor_critico,
                'p_valor': p_valor,
                'rechaza_h0': rechaza_h0,
                'limites': limites,
                'frecuencias_observadas': freq_obs,
                'frecuencia_esperada': freq_esp,
                'tipo_prueba': 'Chi-cuadrado',
                'alpha': self.alpha,
                'n': self.n
            }
            
            return resultado
            
        except Exception as e:
            raise Exception(f"Error en prueba Chi-cuadrado: {str(e)}")
    
    def mostrar_tabla_detallada(self, parent=None):
        """Mostrar tabla detallada de la prueba Chi-cuadrado"""
        ventana = tk.Toplevel(parent) if parent else tk.Tk()
        ventana.title("Tabla Detallada - Chi Cuadrado")
        ventana.geometry("800x600")
        
        # Ejecutar la prueba para obtener datos
        resultado = self.ejecutar()
        limites = resultado['limites']
        freq_obs = resultado['frecuencias_observadas']
        freq_esp = resultado['frecuencia_esperada']
        
        # Frame principal
        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        titulo = ttk.Label(main_frame, text="Prueba Chi-Cuadrado - Tabla Detallada", 
                          font=("Arial", 14, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Crear tabla
        columns = ('Intervalo', 'Límite Inf', 'Límite Sup', 'Oi', 'Ei', '(Oi-Ei)²/Ei')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Definir encabezados
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')
        
        # Llenar datos
        chi_total = 0
        for i in range(len(freq_obs)):
            limite_inf = limites[i]
            limite_sup = limites[i+1]
            oi = freq_obs[i]
            ei = freq_esp
            chi_contrib = (oi - ei) ** 2 / ei
            chi_total += chi_contrib
            
            tree.insert('', 'end', values=(
                f"Intervalo {i+1}",
                f"{limite_inf:.4f}",
                f"{limite_sup:.4f}",
                f"{oi}",
                f"{ei:.2f}",
                f"{chi_contrib:.4f}"
            ))
        
        # Agregar fila de totales
        tree.insert('', 'end', values=(
            "TOTAL",
            "-",
            "-",
            f"{sum(freq_obs)}",
            f"{freq_esp * len(freq_obs):.2f}",
            f"{chi_total:.4f}"
        ), tags=('total',))
        
        # Estilo para la fila total
        tree.tag_configure('total', background='lightblue')
        
        tree.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        
        # Resultados
        frame_resultados = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        frame_resultados.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(frame_resultados, text=f"Chi-cuadrado calculado: {resultado['estadistico']:.6f}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(frame_resultados, text=f"Grados de libertad: {resultado['grados_libertad']}").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(frame_resultados, text=f"Valor crítico: {resultado['valor_critico']:.6f}").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(frame_resultados, text=f"P-valor: {resultado['p_valor']:.6f}").grid(row=3, column=0, sticky=tk.W)
        ttk.Label(frame_resultados, text=f"Nivel de significancia: {self.alpha}").grid(row=4, column=0, sticky=tk.W)
        
        # Decisión
        decision_text = "Se RECHAZA H0" if resultado['rechaza_h0'] else "NO se rechaza H0"
        color = "red" if resultado['rechaza_h0'] else "green"
        decision_label = ttk.Label(frame_resultados, text=f"Decisión: {decision_text}", 
                                  foreground=color, font=("Arial", 10, "bold"))
        decision_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        
        # Gráfico
        self.crear_grafico_chi(main_frame, resultado)
        
        # Configurar weights
        ventana.columnconfigure(0, weight=1)
        ventana.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        return ventana
    
    def crear_grafico_chi(self, parent, resultado):
        """Crear gráfico de barras comparando frecuencias"""
        # Frame para el gráfico
        frame_grafico = ttk.LabelFrame(parent, text="Gráfico Comparativo", padding="5")
        frame_grafico.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Datos para el gráfico
        intervalos = [f"Int {i+1}" for i in range(len(resultado['frecuencias_observadas']))]
        freq_obs = resultado['frecuencias_observadas']
        freq_esp = [resultado['frecuencia_esperada']] * len(freq_obs)
        
        x = np.arange(len(intervalos))
        width = 0.35
        
        # Crear barras
        bars1 = ax.bar(x - width/2, freq_obs, width, label='Observada', alpha=0.8, color='skyblue')
        bars2 = ax.bar(x + width/2, freq_esp, width, label='Esperada', alpha=0.8, color='orange')
        
        # Configurar gráfico
        ax.set_xlabel('Intervalos')
        ax.set_ylabel('Frecuencia')
        ax.set_title('Comparación Frecuencias Observadas vs Esperadas')
        ax.set_xticks(x)
        ax.set_xticklabels(intervalos)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Agregar valores en las barras
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom', fontsize=8)
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=8)
        
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
    prueba = PruebaChi(datos_test, num_intervalos=10, alpha=0.05)
    resultado = prueba.ejecutar()
    
    print("Prueba Chi-cuadrado")
    print("=" * 30)
    print(f"Estadístico: {resultado['estadistico']:.6f}")
    print(f"Grados de libertad: {resultado['grados_libertad']}")
    print(f"Valor crítico: {resultado['valor_critico']:.6f}")
    print(f"P-valor: {resultado['p_valor']:.6f}")
    print(f"¿Rechaza H0?: {resultado['rechaza_h0']}")
    
    # Mostrar tabla detallada
    ventana = prueba.mostrar_tabla_detallada()
    ventana.mainloop()

if __name__ == "__main__":
    main()