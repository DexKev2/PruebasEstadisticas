import numpy as np
import pandas as pd
from scipy import stats
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

class RachasEncimaDebajo:
    """
    Realiza la prueba de rachas por encima y por debajo de un umbral (0.5).
    Esta prueba evalúa la aleatoriedad de una secuencia de datos basándose
    en el número total de rachas (secuencias de valores consecutivos
    por encima o por debajo del umbral).
    """
    def __init__(self, datos, alpha=0.05):
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

        # Definimos el umbral como 0.5, como se indicó
        self.umbral = 0.5 
        
        # Generar secuencia de '+' y '-' basada en el umbral
        self.secuencia = ['+' if dato >= self.umbral else '-' for dato in self.datos] # Cambiado a >= para incluir el 0.5 si es exacto
        
        # Contar n1 (número de valores >= umbral) y n2 (número de valores < umbral)
        self.n1 = self.secuencia.count('+')
        self.n2 = self.secuencia.count('-')

        # Si n1 o n2 es cero, la prueba no puede realizarse adecuadamente
        if self.n1 == 0 or self.n2 == 0:
            raise ValueError("No hay suficientes valores por encima y por debajo del umbral para realizar la prueba de rachas.")

    def _calcular_numero_rachas(self):
        """Calcula el número de rachas observadas (R)."""
        if not self.secuencia:
            return 0
        
        rachas_observadas = 0
        if len(self.secuencia) > 0:
            rachas_observadas = 1 # La primera racha siempre existe si hay elementos
            for i in range(1, len(self.secuencia)):
                if self.secuencia[i] != self.secuencia[i-1]:
                    rachas_observadas += 1
        return rachas_observadas

    def ejecutar(self):
        """
        Ejecuta la prueba de rachas por encima y por debajo.
        Retorna un diccionario con los resultados.
        """
        try:
            R = self._calcular_numero_rachas()

            # Fórmulas para la media y varianza del número de rachas (R)
            # para muestras grandes (n1 > 20 y n2 > 20)
            # E(R) = (2 * n1 * n2) / (n1 + n2) + 1
            # Var(R) = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1))

            # Para n1 o n2 <= 20, se suelen usar tablas o aproximaciones
            # Para simplificar y seguir el enfoque de Chi-cuadrado si es necesario,
            # usaremos la aproximación normal para n grande.
            # Sin embargo, la prueba de rachas "encima/debajo" generalmente usa Z-test o tablas para R.
            # Adaptamos para que se parezca al chi-cuadrado si es lo que necesitas.
            # No obstante, lo más común es un Z-test para el número de rachas.

            # Calcular la media esperada de rachas E(R)
            ER = (2 * self.n1 * self.n2) / (self.n1 + self.n2) + 1

            # Calcular la varianza esperada de rachas Var(R)
            # Aseguramos que el denominador no sea cero si n_total es 1
            if (self.n1 + self.n2 - 1) == 0:
                VarR = 0 # O manejar como error
            else:
                VarR = (2 * self.n1 * self.n2 * (2 * self.n1 * self.n2 - self.n1 - self.n2)) / \
                        ((self.n1 + self.n2)**2 * (self.n1 + self.n2 - 1))
            
            # Desviación estándar
            std_R = np.sqrt(VarR)

            # Estadístico Z (aproximación normal)
            # Z = (R - E(R)) / sqrt(Var(R))
            if std_R == 0:
                z_calculado = 0 # O manejar como error
            else:
                z_calculado = (R - ER) / std_R

            # Valor crítico para una prueba bilateral
            z_critico = stats.norm.ppf(1 - self.alpha / 2)
            
            # P-valor bilateral
            p_valor = 2 * (1 - stats.norm.cdf(abs(z_calculado)))

            rechaza_h0 = abs(z_calculado) > z_critico

            resultado = {
                'numero_rachas_observado': R,
                'n1': self.n1,
                'n2': self.n2,
                'media_esperada_rachas': ER,
                'varianza_esperada_rachas': VarR,
                'estadistico_z': z_calculado,
                'valor_critico_z': z_critico,
                'p_valor': p_valor,
                'rechaza_h0': rechaza_h0,
                'tipo_prueba': 'Rachas por encima/debajo del umbral (0.5)',
                'alpha': self.alpha,
                'n_total_datos': self.n_total,
                'umbral': self.umbral
            }
            
            return resultado
            
        except ValueError as ve:
            return {'error': str(ve)}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'error': f'Error durante la ejecución: {str(e)}'}

    def mostrar_tabla_detallada(self, parent=None):
        """
        Muestra los resultados detallados de la prueba en una ventana de Tkinter.
        """
        resultado = self.ejecutar()

        if 'error' in resultado:
            if parent:
                messagebox.showerror("Error", resultado['error'])
            else:
                print(f"Error: {resultado['error']}")
            return None

        try:
            ventana = tk.Toplevel(parent) if parent else tk.Tk()
            ventana.title("Tabla Detallada - Prueba de Rachas Encima/Debajo del Umbral")
            ventana.geometry("700x500")

            main_frame = ttk.Frame(ventana, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            titulo = ttk.Label(main_frame, text="Prueba de Rachas Encima/Debajo del Umbral", 
                             font=("Arial", 14, "bold"))
            titulo.pack(pady=10)

            # Información de la secuencia
            frame_info = ttk.LabelFrame(main_frame, text="Información de la Secuencia y Umbral", padding="10")
            frame_info.pack(fill=tk.X, pady=5)
            
            secuencia_text = ''.join(self.secuencia[:50])
            if len(self.secuencia) > 50:
                secuencia_text += "..."
            
            ttk.Label(frame_info, text=f"Secuencia de signos: {secuencia_text}").pack(anchor=tk.W)
            ttk.Label(frame_info, text=f"Longitud de la secuencia: {len(self.secuencia)}").pack(anchor=tk.W)
            ttk.Label(frame_info, text=f"Umbral utilizado: {self.umbral}").pack(anchor=tk.W)
            ttk.Label(frame_info, text=f"Número de valores por encima/igual al umbral (n1): {resultado['n1']}").pack(anchor=tk.W)
            ttk.Label(frame_info, text=f"Número de valores por debajo del umbral (n2): {resultado['n2']}").pack(anchor=tk.W)


            # Resultados de la prueba
            frame_resultados = ttk.LabelFrame(main_frame, text="Resultados de la Prueba", padding="10")
            frame_resultados.pack(fill=tk.X, expand=True, pady=10)
            
            ttk.Label(frame_resultados, text=f"Número de rachas observadas (R): {resultado['numero_rachas_observado']:.0f}").pack(anchor=tk.W)
            ttk.Label(frame_resultados, text=f"Media esperada de rachas E(R): {resultado['media_esperada_rachas']:.4f}").pack(anchor=tk.W)
            ttk.Label(frame_resultados, text=f"Varianza esperada de rachas Var(R): {abs(resultado['varianza_esperada_rachas']):.4f}").pack(anchor=tk.W)
            ttk.Label(frame_resultados, text=f"Estadístico Z calculado: {abs(resultado['estadistico_z']):.6f}").pack(anchor=tk.W)
            ttk.Label(frame_resultados, text=f"Valor crítico Z (α={self.alpha}): {resultado['valor_critico_z']:.6f}").pack(anchor=tk.W)
            ttk.Label(frame_resultados, text=f"P-valor: {resultado['p_valor']:.6f}").pack(anchor=tk.W)
            
            decision_text = "Se RECHAZA H₀ (Los datos NO son aleatorios)" if resultado['rechaza_h0'] else "NO se rechaza H₀ (Los datos son aleatorios)"
            color = "red" if resultado['rechaza_h0'] else "green"
            ttk.Label(frame_resultados, text=f"Decisión: {decision_text}", 
                     foreground=color, font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
            
            return ventana
            
        except Exception as e:
            error_msg = f"Error al mostrar la tabla: {str(e)}"
            import traceback
            traceback.print_exc()
            if parent:
                messagebox.showerror("Error", error_msg)
            return None

def main_rachas_encima_debajo():
    print("=== INICIANDO PRUEBA DE RACHAS ENCIMA/DEBAJO ===")
    
    # Datos de prueba:
    # 1. Aleatorios (deberían ser aleatorios)
    np.random.seed(42)
    datos_aleatorios = np.random.rand(50) # Números aleatorios entre 0 y 1

    # 2. No aleatorios (tendencia, menos rachas)
    datos_no_aleatorios_1 = np.array([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3, 0.8, 0.9])
    
    # 3. No aleatorios (alternancia rápida, más rachas)
    datos_no_aleatorios_2 = np.array([0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4, 0.6, 0.1, 0.9, 0.2, 0.8])

    alpha = 0.05
    
    # Prueba con datos aleatorios
    print("\n--- Prueba con datos aleatorios ---")
    try:
        prueba_aleatorios = RachasEncimaDebajo(datos_aleatorios, alpha=alpha)
        resultado_aleatorios = prueba_aleatorios.ejecutar()
        
        if 'error' in resultado_aleatorios:
            print(f"Error en la prueba: {resultado_aleatorios['error']}")
        else:
            print(f"Rachas Observadas (R): {resultado_aleatorios['numero_rachas_observado']}")
            print(f"E(R): {resultado_aleatorios['media_esperada_rachas']:.4f}")
            print(f"Z-calculado: {resultado_aleatorios['estadistico_z']:.6f}")
            print(f"P-valor: {resultado_aleatorios['p_valor']:.6f}")
            print(f"Decisión: {'Rechaza H0' if resultado_aleatorios['rechaza_h0'] else 'No rechaza H0'}")
        
        ventana_aleatorios = prueba_aleatorios.mostrar_tabla_detallada()
        if ventana_aleatorios:
            ventana_aleatorios.mainloop()

    except Exception as e:
        print(f"Error general en prueba aleatoria: {e}")

    # Prueba con datos no aleatorios (tendencia)
    print("\n--- Prueba con datos no aleatorios (tendencia) ---")
    try:
        prueba_no_aleatorios_1 = RachasEncimaDebajo(datos_no_aleatorios_1, alpha=alpha)
        resultado_no_aleatorios_1 = prueba_no_aleatorios_1.ejecutar()
        
        if 'error' in resultado_no_aleatorios_1:
            print(f"Error en la prueba: {resultado_no_aleatorios_1['error']}")
        else:
            print(f"Rachas Observadas (R): {resultado_no_aleatorios_1['numero_rachas_observado']}")
            print(f"E(R): {resultado_no_aleatorios_1['media_esperada_rachas']:.4f}")
            print(f"Z-calculado: {resultado_no_aleatorios_1['estadistico_z']:.6f}")
            print(f"P-valor: {resultado_no_aleatorios_1['p_valor']:.6f}")
            print(f"Decisión: {'Rechaza H0' if resultado_no_aleatorios_1['rechaza_h0'] else 'No rechaza H0'}")
        
        ventana_no_aleatorios_1 = prueba_no_aleatorios_1.mostrar_tabla_detallada()
        if ventana_no_aleatorios_1:
            ventana_no_aleatorios_1.mainloop()

    except Exception as e:
        print(f"Error general en prueba no aleatoria 1: {e}")

if __name__ == "__main__":
    main_rachas_encima_debajo()