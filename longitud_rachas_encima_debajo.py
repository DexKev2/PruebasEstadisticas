import numpy as np
import pandas as pd
from scipy import stats
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

class LongitudRachasEncimaDebajo:
    """
    Realiza la prueba de longitud de rachas por encima y por debajo de la media.
    Esta prueba utiliza un estadístico Chi-cuadrado para comparar las frecuencias
    observadas (Oi) de rachas de diferentes longitudes con las frecuencias
    esperadas (Ei).
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

        # --- MODIFICACIÓN CLAVE AQUÍ: Usar 0.5 como umbral en lugar de la media ---
        self.umbral = 0.5 # Definimos el umbral como 0.5
        
        # Generar secuencia de '+' y '-' basada en el umbral
        self.secuencia = ['+' if dato > self.umbral else '-' for dato in self.datos]
        
        # Contar n1 (encima del umbral) y n2 (debajo del umbral)
        self.n1 = self.secuencia.count('+')
        self.n2 = self.secuencia.count('-')
        self.N = self.n1 + self.n2  # Total de elementos considerados

    def _calcular_frecuencias(self):
        """
        Calcula las frecuencias observadas y esperadas de las longitudes de racha.
        """
        # --- Frecuencias Observadas (Oi) ---
        if not self.secuencia:
            return {}, {}

        observed_counts = defaultdict(int)
        current_run_length = 0
        current_run_char = self.secuencia[0]

        for char in self.secuencia:
            if char == current_run_char:
                current_run_length += 1
            else:
                if current_run_length > 0:
                    observed_counts[current_run_length] += 1
                current_run_char = char
                current_run_length = 1
        
        # Contar la última racha
        observed_counts[current_run_length] += 1
        
        max_len_obs = max(observed_counts.keys()) if observed_counts else 0

        # --- Frecuencias Esperadas (Ei) ---
        # Usando la fórmula proporcionada: E(Li) = 2*N * (n1/N)^i * (n2/N)^2
        expected_counts = {}
        if self.N > 0 and self.n2 > 0:
            for i in range(1, max_len_obs + 1):
                prob_n1 = self.n1 / self.N
                prob_n2 = self.n2 / self.N
                # Se utiliza la formula tal cual fue proveída en la imagen.
                ei = 2 * self.N * (prob_n1 ** i) * (prob_n2 ** 2)
                expected_counts[i] = ei
        
        return observed_counts, expected_counts

    def ejecutar(self):
        """
        Ejecuta la prueba completa y devuelve los resultados.
        """
        Oi_dict, Ei_dict = self._calcular_frecuencias()
        
        if not Oi_dict:
            return {
                'error': 'No se pudieron calcular las frecuencias. Verifique los datos.'
            }

        # Convertir a DataFrames para facilitar el manejo
        df = pd.DataFrame({
            'Oi': pd.Series(Oi_dict),
            'Ei': pd.Series(Ei_dict)
        }).sort_index().fillna(0)

        # --- Agrupar si Ei < 5 ---
        # Se agrupan desde la longitud más larga hacia atrás
        grouped_Oi = []
        grouped_Ei = []
        
        temp_Oi = 0
        temp_Ei = 0
        
        for i in reversed(df.index):
            temp_Oi += df.loc[i, 'Oi']
            temp_Ei += df.loc[i, 'Ei']
            
            if temp_Ei >= 5:
                grouped_Oi.insert(0, temp_Oi)
                grouped_Ei.insert(0, temp_Ei)
                temp_Oi = 0
                temp_Ei = 0
        
        # Si queda un grupo pequeño al final, se une con el siguiente
        if temp_Ei > 0 and grouped_Ei:
            grouped_Oi[0] += temp_Oi
            grouped_Ei[0] += temp_Ei
        elif temp_Ei > 0: # Caso en que todos los Ei son < 5
            grouped_Oi.append(temp_Oi)
            grouped_Ei.append(temp_Ei)
        
        # --- Calcular Chi-cuadrado ---
        k = len(grouped_Oi)
        grados_libertad = k - 1
        
        if grados_libertad <= 0:
            return {
                'error': f'No hay suficientes grados de libertad ({grados_libertad}) para realizar la prueba.'
            }

        chi_cuadrado_calculado = np.sum(
            (np.array(grouped_Oi) - np.array(grouped_Ei)) ** 2 / np.array(grouped_Ei)
        )
        
        valor_critico = stats.chi2.ppf(1 - self.alpha, grados_libertad)
        p_valor = 1 - stats.chi2.cdf(chi_cuadrado_calculado, grados_libertad)
        
        rechaza_h0 = chi_cuadrado_calculado > valor_critico

        resultado = {
            'estadistico': chi_cuadrado_calculado,
            'grados_libertad': grados_libertad,
            'valor_critico': valor_critico,
            'p_valor': p_valor,
            'rechaza_h0': rechaza_h0,
            'tipo_prueba': 'Longitud de Rachas Encima/Debajo (Umbral 0.5)', # Actualizado para reflejar el cambio
            'alpha': self.alpha,
            'n_total': self.n_total,
            'umbral': self.umbral, # Se agrega el umbral a los resultados
            'n1': self.n1,
            'n2': self.n2,
            'df_original': df,
            'grouped_oi': grouped_Oi,
            'grouped_ei': grouped_Ei
        }
        
        return resultado

    def mostrar_tabla_detallada(self, parent=None):
        """Muestra una ventana con la tabla detallada de la prueba."""
        resultado = self.ejecutar()

        if 'error' in resultado:
            tk.messagebox.showerror("Error", resultado['error'])
            return

        ventana = tk.Toplevel(parent) if parent else tk.Tk()
        ventana.title("Tabla Detallada - Longitud de Rachas Encima/Debajo (Umbral 0.5)") # Actualizado el título
        ventana.geometry("800x600")

        main_frame = ttk.Frame(ventana, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        titulo = ttk.Label(main_frame, text="Prueba de Longitud de Rachas (Umbral 0.5)", font=("Arial", 14, "bold")) # Actualizado el título
        titulo.pack(pady=10)

        # --- Tabla de frecuencias originales ---
        frame_original = ttk.LabelFrame(main_frame, text="Frecuencias Originales", padding="10")
        frame_original.pack(fill=tk.X, expand=True, pady=5)
        
        cols_orig = ('Longitud (i)', 'Oi', 'Ei')
        tree_orig = ttk.Treeview(frame_original, columns=cols_orig, show='headings', height=7)
        for col in cols_orig:
            tree_orig.heading(col, text=col)
            tree_orig.column(col, width=120, anchor='center')
        
        df_orig = resultado['df_original']
        for i in df_orig.index:
            tree_orig.insert('', 'end', values=(i, f"{df_orig.loc[i, 'Oi']:.0f}", f"{df_orig.loc[i, 'Ei']:.4f}"))
        
        tree_orig.pack(fill=tk.X, expand=True)

        # --- Tabla de frecuencias agrupadas y Chi-cuadrado ---
        frame_agrupado = ttk.LabelFrame(main_frame, text="Cálculo de Chi-Cuadrado (Datos Agrupados)", padding="10")
        frame_agrupado.pack(fill=tk.X, expand=True, pady=5)
        
        cols_agrup = ('Grupo', 'Oi (agrupado)', 'Ei (agrupado)', '(Oi-Ei)²/Ei')
        tree_agrup = ttk.Treeview(frame_agrupado, columns=cols_agrup, show='headings', height=5)
        for col in cols_agrup:
            tree_agrup.heading(col, text=col)
            tree_agrup.column(col, width=150, anchor='center')
        
        chi_total = 0
        grouped_oi = resultado['grouped_oi']
        grouped_ei = resultado['grouped_ei']
        for i in range(len(grouped_oi)):
            oi = grouped_oi[i]
            ei = grouped_ei[i]
            chi_contrib = (oi - ei)**2 / ei
            chi_total += chi_contrib
            tree_agrup.insert('', 'end', values=(f"Grupo {i+1}", f"{oi:.0f}", f"{ei:.4f}", f"{chi_contrib:.4f}"))

        tree_agrup.insert('', 'end', values=("TOTAL", f"{sum(grouped_oi):.0f}", f"{sum(grouped_ei):.4f}", f"{chi_total:.4f}"), tags=('total',))
        tree_agrup.tag_configure('total', background='lightblue', font=("Arial", 9, "bold"))
        tree_agrup.pack(fill=tk.X, expand=True)

        # --- Resultados ---
        frame_resultados = ttk.LabelFrame(main_frame, text="Resultados Finales", padding="10")
        frame_resultados.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Label(frame_resultados, text=f"Estadístico Chi-cuadrado (χ²): {resultado['estadistico']:.6f}").pack(anchor=tk.W)
        ttk.Label(frame_resultados, text=f"Grados de libertad: {resultado['grados_libertad']}").pack(anchor=tk.W)
        ttk.Label(frame_resultados, text=f"Valor crítico (α={self.alpha}): {resultado['valor_critico']:.6f}").pack(anchor=tk.W)
        ttk.Label(frame_resultados, text=f"P-valor: {resultado['p_valor']:.6f}").pack(anchor=tk.W)
        ttk.Label(frame_resultados, text=f"Umbral utilizado: {resultado['umbral']:.1f}").pack(anchor=tk.W) # Mostrar el umbral
        
        decision_text = "Se RECHAZA H₀ (Los datos no son independientes)" if resultado['rechaza_h0'] else "NO se rechaza H₀ (Los datos son independientes)"
        color = "red" if resultado['rechaza_h0'] else "green"
        ttk.Label(frame_resultados, text=f"Decisión: {decision_text}", foreground=color, font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
        
        return ventana

def main():
    """Función para probar el módulo independientemente."""
    # Generar datos de prueba (por ejemplo, números entre 0 y 1)
    np.random.seed(0)
    datos_test = np.random.rand(100) # Datos aleatorios entre 0 y 1

    alpha = 0.05
    
    # Crear y ejecutar prueba
    try:
        prueba = LongitudRachasEncimaDebajo(datos_test, alpha=alpha)
        
        # Mostrar tabla detallada
        ventana = prueba.mostrar_tabla_detallada()
        ventana.mainloop()

    except Exception as e:
        print(f"Error al ejecutar la prueba: {e}")

if __name__ == "__main__":
    main()