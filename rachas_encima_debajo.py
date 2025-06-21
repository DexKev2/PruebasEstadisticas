
import numpy as np
import pandas as pd
from scipy import stats
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class RachasEncimaDebajo:
    """
    Realiza la prueba de rachas por encima y por debajo de un umbral (0.5).
    Esta prueba utiliza un estadístico Z para determinar si el número de rachas
    observado es significativamente diferente del esperado bajo la hipótesis de independencia.
    """
    def __init__(self, datos, alpha):
        """
        Inicializa la prueba.
        :param datos: Una lista o array de números.
        :param alpha: Nivel de significancia para la prueba.
        """
        self.datos = np.array(datos)
        self.alpha = alpha
        self.n_total = len(self.datos)
        
        if self.n_total == 0:
            raise ValueError("El conjunto de datos no puede estar vacío.")

        # Usar 0.5 como umbral
        self.umbral = 0.5
        
        # Generar secuencia de '+' y '-' basada en el umbral
        self.secuencia = ['+' if dato > self.umbral else '-' for dato in self.datos]
        
        # Contar n1 (encima del umbral) y n2 (debajo del umbral)
        self.n1 = self.secuencia.count('+')
        self.n2 = self.secuencia.count('-')
        self.N = self.n1 + self.n2  # Total de elementos considerados

    def _contar_rachas(self):
        """
        Cuenta el número total de rachas en la secuencia.
        Una racha es una secuencia consecutiva del mismo símbolo.
        """
        if not self.secuencia:
            return 0
        
        num_rachas = 1
        for i in range(1, len(self.secuencia)):
            if self.secuencia[i] != self.secuencia[i-1]:
                num_rachas += 1
        
        return num_rachas

    def ejecutar(self):
        """
        Ejecuta la prueba completa y devuelve los resultados.
        """
        # Contar rachas observadas
        R = self._contar_rachas()
        
        if self.N == 0 or self.n1 == 0 or self.n2 == 0:
            return {
                'error': 'No se pueden calcular las rachas. Verifique que haya datos tanto por encima como por debajo del umbral.'
            }

        # Calcular valores esperados según las fórmulas
        # μR = (2*n1*n2)/(n1+n2) + 1
        mu_R = (2 * self.n1 * self.n2) / (self.n1 + self.n2) + 1
        
        # σR² = [2*n1*n2*(2*n1*n2 - n1 - n2)] / [(n1+n2)²*(n1+n2-1)]
        numerador = 2 * self.n1 * self.n2 * (2 * self.n1 * self.n2 - self.n1 - self.n2)
        denominador = (self.n1 + self.n2)**2 * (self.n1 + self.n2 - 1)
        
        if denominador == 0:
            return {
                'error': 'Error en el cálculo de la varianza. Denominador igual a cero.'
            }
        
        sigma_R_squared = numerador / denominador
        sigma_R = np.sqrt(sigma_R_squared)
        
        # Calcular estadístico Z
        # Z = abs(R - μR) / σR
        if sigma_R == 0:
            return {
                'error': 'Error en el cálculo del estadístico Z. Desviación estándar igual a cero.'
            }
        
        Z = abs(R - mu_R) / sigma_R
        
        # Valor crítico para prueba bilateral
        valor_critico = stats.norm.ppf(1 - self.alpha/2)
        
        # P-valor para prueba bilateral
        p_valor = 2 * (1 - stats.norm.cdf(abs(Z)))
        
        # Decisión
        rechaza_h0 = Z > valor_critico

        resultado = {
            'estadistico': Z,
            'valor_critico': valor_critico,
            'p_valor': p_valor,
            'rechaza_h0': rechaza_h0,
            'tipo_prueba': 'Rachas Encima/Debajo (Umbral 0.5)',
            'alpha': self.alpha,
            'n_total': self.n_total,
            'umbral': self.umbral,
            'n1': self.n1,
            'n2': self.n2,
            'rachas_observadas': R,
            'rachas_esperadas': mu_R,
            'desviacion_estandar': sigma_R,
            'secuencia': ''.join(self.secuencia[:50]) + ('...' if len(self.secuencia) > 50 else '')  # Primeros 50 para mostrar
        }
        
        return resultado

    def mostrar_tabla_detallada(self, parent=None):
        """Muestra una ventana con la tabla detallada de la prueba."""
        resultado = self.ejecutar()

        if 'error' in resultado:
            tk.messagebox.showerror("Error", resultado['error'])
            return

        ventana = tk.Toplevel(parent) if parent else tk.Tk()
        ventana.title("Tabla Detallada - Rachas Encima/Debajo (Umbral 0.5)")
        ventana.geometry("700x600")

        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        titulo = ttk.Label(main_frame, text="Prueba de Rachas Encima/Debajo (Umbral 0.5)", font=("Arial", 14, "bold"))
        titulo.pack(pady=10)

        # --- Información básica ---
        frame_info = ttk.LabelFrame(main_frame, text="Información Básica", padding="10")
        frame_info.pack(fill=tk.X, expand=True, pady=5)
        
        info_text = f"""
Umbral utilizado: {resultado['umbral']:.1f}
Total de datos: {resultado['n_total']}
Datos por encima del umbral (n₁): {resultado['n1']}
Datos por debajo del umbral (n₂): {resultado['n2']}
Secuencia (primeros 50): {resultado['secuencia']}
        """
        
        ttk.Label(frame_info, text=info_text.strip(), font=("Courier", 9)).pack(anchor=tk.W)

        # --- Cálculos ---
        frame_calculos = ttk.LabelFrame(main_frame, text="Cálculos", padding="10")
        frame_calculos.pack(fill=tk.X, expand=True, pady=5)
        
        cols_calc = ('Parámetro', 'Fórmula', 'Valor')
        tree_calc = ttk.Treeview(frame_calculos, columns=cols_calc, show='headings', height=6)
        for col in cols_calc:
            tree_calc.heading(col, text=col)
            tree_calc.column(col, width=200, anchor='center')
        
        # Agregar cálculos paso a paso
        tree_calc.insert('', 'end', values=('Rachas Observadas (R)', 'Conteo directo', f"{resultado['rachas_observadas']}"))
        tree_calc.insert('', 'end', values=('Media Esperada (μR)', '(2×n₁×n₂)/(n₁+n₂) + 1', f"{resultado['rachas_esperadas']:.4f}"))
        tree_calc.insert('', 'end', values=('Desviación Estándar (σR)', '√[2×n₁×n₂×(2×n₁×n₂-n₁-n₂)/((n₁+n₂)²×(n₁+n₂-1))]', f"{resultado['desviacion_estandar']:.4f}"))
        tree_calc.insert('', 'end', values=('Estadístico Z', '|R - μR| / σR', f"{resultado['estadistico']:.6f}"))
        tree_calc.insert('', 'end', values=('Valor Crítico', f'Z₁₋α/₂ (α={self.alpha})', f"{resultado['valor_critico']:.6f}"))
        tree_calc.insert('', 'end', values=('P-valor', '2×(1-Φ(|Z|))', f"{resultado['p_valor']:.6f}"))
        
        tree_calc.pack(fill=tk.X, expand=True)

        # --- Resultados ---
        frame_resultados = ttk.LabelFrame(main_frame, text="Resultados Finales", padding="10")
        frame_resultados.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Label(frame_resultados, text=f"Estadístico Z: {resultado['estadistico']:.6f}").pack(anchor=tk.W)
        ttk.Label(frame_resultados, text=f"Valor crítico (α={self.alpha}): {resultado['valor_critico']:.6f}").pack(anchor=tk.W)
        ttk.Label(frame_resultados, text=f"P-valor: {resultado['p_valor']:.6f}").pack(anchor=tk.W)
        
        decision_text = "Se RECHAZA H₀ (Los datos no son independientes)" if resultado['rechaza_h0'] else "NO se rechaza H₀ (Los datos son independientes)"
        color = "red" if resultado['rechaza_h0'] else "green"
        ttk.Label(frame_resultados, text=f"Decisión: {decision_text}", foreground=color, font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        
        return ventana

def main():
    """Función para probar el módulo independientemente."""
    # Generar datos de prueba (por ejemplo, números entre 0 y 1)
    np.random.seed(42)
    datos_test = np.random.rand(100)  # Datos aleatorios entre 0 y 1

    alpha = 0.05
    
    # Crear y ejecutar prueba
    try:
        prueba = RachasEncimaDebajo(datos_test, alpha=alpha)
        
        # Mostrar tabla detallada
        ventana = prueba.mostrar_tabla_detallada()
        ventana.mainloop()

    except Exception as e:
        print(f"Error al ejecutar la prueba: {e}")

if __name__ == "__main__":
    main()