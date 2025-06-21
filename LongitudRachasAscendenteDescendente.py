import numpy as np
import pandas as pd
from scipy import stats
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
from math import factorial

class LongitudRachasAscendenteDescendente:
    def __init__(self, datos, alpha=0.05):
        self.datos = np.array(datos)
        self.alpha = alpha
        self.n_total = len(self.datos)
        
        if self.n_total < 2:
            raise ValueError("El conjunto de datos debe contener al menos 2 elementos.")

        self.secuencia_signos = self._generar_secuencia_signos()
        self.N_comparaciones = len(self.secuencia_signos)
        
        # Debug: Imprimir información
        print(f"Debug: Datos de entrada: {len(self.datos)} elementos")
        print(f"Debug: Secuencia de signos: {len(self.secuencia_signos)} elementos")
        print(f"Debug: Primeros 20 signos: {''.join(self.secuencia_signos[:20])}")

    def _generar_secuencia_signos(self):
        signos = []
        for i in range(1, self.n_total):
            if self.datos[i] > self.datos[i-1]:
                signos.append('+')
            elif self.datos[i] < self.datos[i-1]:
                signos.append('-')
            # Si son iguales, no agregamos nada (se omite)
        return signos

    def _calcular_frecuencias(self):
        print(f"Debug: Calculando frecuencias...")
        observed_counts = defaultdict(int)
        
        if not self.secuencia_signos:
            print("Debug: No hay secuencia de signos")
            return {}, {}

        # Calcular rachas correctamente
        rachas = []
        if len(self.secuencia_signos) > 0:
            current_char = self.secuencia_signos[0]
            current_length = 1
            
            for i in range(1, len(self.secuencia_signos)):
                if self.secuencia_signos[i] == current_char:
                    current_length += 1
                else:
                    rachas.append(current_length)
                    current_char = self.secuencia_signos[i]
                    current_length = 1
            
            # Agregar la última racha
            rachas.append(current_length)
        
        print(f"Debug: Rachas encontradas: {rachas}")
        
        # Contar frecuencias observadas
        for longitud in rachas:
            observed_counts[longitud] += 1
        
        print(f"Debug: Frecuencias observadas: {dict(observed_counts)}")
        
        # Calcular frecuencias esperadas
        expected_counts = {}
        max_len_obs = max(observed_counts.keys()) if observed_counts else 0
        
        print(f"Debug: Longitud máxima observada: {max_len_obs}")
        
        total_rachas = len(rachas)
        print(f"Debug: Total de rachas: {total_rachas}")
        
        if total_rachas > 0:
            for i in range(1, max_len_obs + 1):
                try:
                    if i == 1:
                        prob_li = 1/3
                    elif i == 2:
                        prob_li = 1/6
                    else:
                        # Fórmula: P(Li = i) = 2/((i+1)!(i+2))
                        prob_li = 2 / (factorial(i+1) * (i+2))
                    
                    ei = total_rachas * prob_li
                    expected_counts[i] = ei
                    print(f"Debug: L={i}, P(L={i})={prob_li:.6f}, E={ei:.6f}")
                    
                except (ZeroDivisionError, OverflowError) as e:
                    print(f"Debug: Error calculando probabilidad para i={i}: {e}")
                    expected_counts[i] = 0
        
        print(f"Debug: Frecuencias esperadas: {expected_counts}")
        return observed_counts, expected_counts

    def ejecutar(self):
        print("Debug: Iniciando ejecución...")
        
        try:
            Oi_dict, Ei_dict = self._calcular_frecuencias()
            
            if not Oi_dict:
                error_msg = 'No se pudieron calcular las frecuencias. Datos insuficientes.'
                print(f"Debug: {error_msg}")
                return {'error': error_msg}

            print(f"Debug: Oi_dict: {Oi_dict}")
            print(f"Debug: Ei_dict: {Ei_dict}")

            # Crear DataFrame
            df = pd.DataFrame({
                'Oi': pd.Series(Oi_dict),
                'Ei': pd.Series(Ei_dict)
            }).sort_index().fillna(0)
            
            print(f"Debug: DataFrame creado:\n{df}")

            # Agrupar para que Ei >= 5
            grouped_Oi = []
            grouped_Ei = []
            
            temp_Oi = 0
            temp_Ei = 0
            
            # Recorrer desde el final para agrupar
            indices_ordenados = sorted(df.index, reverse=True)
            for i in indices_ordenados:
                temp_Oi += df.loc[i, 'Oi']
                temp_Ei += df.loc[i, 'Ei']
                
                print(f"Debug: Procesando i={i}, temp_Oi={temp_Oi}, temp_Ei={temp_Ei}")
                
                if temp_Ei >= 5.0:
                    grouped_Oi.insert(0, temp_Oi)
                    grouped_Ei.insert(0, temp_Ei)
                    print(f"Debug: Grupo creado - Oi={temp_Oi}, Ei={temp_Ei}")
                    temp_Oi = 0
                    temp_Ei = 0
            
            # Si queda algo sin agrupar
            if temp_Oi > 0 or temp_Ei > 0:
                if len(grouped_Ei) > 0:
                    grouped_Oi[0] += temp_Oi
                    grouped_Ei[0] += temp_Ei
                    print(f"Debug: Agregado al primer grupo - Total Oi={grouped_Oi[0]}, Ei={grouped_Ei[0]}")
                else:
                    grouped_Oi.append(temp_Oi)
                    grouped_Ei.append(temp_Ei)
                    print(f"Debug: Nuevo grupo creado - Oi={temp_Oi}, Ei={temp_Ei}")

            print(f"Debug: Grupos finales - Oi: {grouped_Oi}, Ei: {grouped_Ei}")

            # Validar que tenemos datos suficientes
            if len(grouped_Oi) < 2:
                error_msg = f'Se necesitan al menos 2 grupos para la prueba Chi-cuadrado. Solo se tienen {len(grouped_Oi)} grupos.'
                print(f"Debug: {error_msg}")
                return {'error': error_msg}

            k = len(grouped_Oi)
            grados_libertad = k - 1
            
            print(f"Debug: k={k}, grados_libertad={grados_libertad}")

            # Calcular Chi-cuadrado
            chi_cuadrado_calculado = 0
            for i in range(len(grouped_Oi)):
                if grouped_Ei[i] > 0:
                    contrib = (grouped_Oi[i] - grouped_Ei[i]) ** 2 / grouped_Ei[i]
                    chi_cuadrado_calculado += contrib
                    print(f"Debug: Grupo {i+1} - Contribución: {contrib:.6f}")
            
            print(f"Debug: Chi-cuadrado calculado: {chi_cuadrado_calculado}")
            
            valor_critico = stats.chi2.ppf(1 - self.alpha, grados_libertad)
            p_valor = 1 - stats.chi2.cdf(chi_cuadrado_calculado, grados_libertad)
            
            rechaza_h0 = chi_cuadrado_calculado > valor_critico
            
            print(f"Debug: Valor crítico: {valor_critico}")
            print(f"Debug: P-valor: {p_valor}")
            print(f"Debug: Rechaza H0: {rechaza_h0}")

            resultado = {
                'estadistico': chi_cuadrado_calculado,
                'grados_libertad': grados_libertad,
                'valor_critico': valor_critico,
                'p_valor': p_valor,
                'rechaza_h0': rechaza_h0,
                'tipo_prueba': 'Longitud de Rachas Ascendente/Descendente',
                'alpha': self.alpha,
                'n_total_datos': self.n_total,
                'n_comparaciones': self.N_comparaciones,
                'df_original': df,
                'grouped_oi': grouped_Oi,
                'grouped_ei': grouped_Ei
            }
            
            print("Debug: Resultado calculado exitosamente")
            return resultado
            
        except Exception as e:
            error_msg = f'Error durante la ejecución: {str(e)}'
            print(f"Debug: {error_msg}")
            import traceback
            traceback.print_exc()
            return {'error': error_msg}

    def mostrar_tabla_detallada(self, parent=None):
        print("Debug: Iniciando mostrar_tabla_detallada")
        resultado = self.ejecutar()

        if 'error' in resultado:
            print(f"Debug: Error en resultado: {resultado['error']}")
            if parent:
                messagebox.showerror("Error", resultado['error'])
            else:
                print(f"Error: {resultado['error']}")
            return None

        try:
            ventana = tk.Toplevel(parent) if parent else tk.Tk()
            ventana.title("Tabla Detallada - Longitud de Rachas Ascendente/Descendente")
            ventana.geometry("900x700")

            main_frame = ttk.Frame(ventana, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)

            titulo = ttk.Label(main_frame, text="Prueba de Longitud de Rachas Ascendente/Descendente", 
                             font=("Arial", 14, "bold"))
            titulo.pack(pady=10)

            # Información de la secuencia
            frame_info = ttk.LabelFrame(main_frame, text="Información de la Secuencia", padding="10")
            frame_info.pack(fill=tk.X, pady=5)
            
            secuencia_text = ''.join(self.secuencia_signos[:50])
            if len(self.secuencia_signos) > 50:
                secuencia_text += "..."
            
            ttk.Label(frame_info, text=f"Secuencia de signos: {secuencia_text}").pack(anchor=tk.W)
            ttk.Label(frame_info, text=f"Longitud de la secuencia: {len(self.secuencia_signos)}").pack(anchor=tk.W)

            # Tabla de frecuencias originales
            frame_original = ttk.LabelFrame(main_frame, text="Frecuencias Originales", padding="10")
            frame_original.pack(fill=tk.X, expand=True, pady=5)
            
            # Crear scrollbar para la tabla
            frame_tree_orig = ttk.Frame(frame_original)
            frame_tree_orig.pack(fill=tk.BOTH, expand=True)
            
            cols_orig = ('Longitud (i)', 'Oi', 'Ei', 'Probabilidad')
            tree_orig = ttk.Treeview(frame_tree_orig, columns=cols_orig, show='headings', height=6)
            
            scrollbar_orig = ttk.Scrollbar(frame_tree_orig, orient=tk.VERTICAL, command=tree_orig.yview)
            tree_orig.configure(yscrollcommand=scrollbar_orig.set)
            
            for col in cols_orig:
                tree_orig.heading(col, text=col)
                tree_orig.column(col, width=120, anchor='center')
            
            df_orig = resultado['df_original']
            for i in df_orig.index:
                prob = df_orig.loc[i, 'Ei'] / sum(df_orig['Ei']) if sum(df_orig['Ei']) > 0 else 0
                tree_orig.insert('', 'end', values=(
                    i, 
                    f"{df_orig.loc[i, 'Oi']:.0f}", 
                    f"{df_orig.loc[i, 'Ei']:.4f}",
                    f"{prob:.4f}"
                ))
            
            tree_orig.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar_orig.pack(side=tk.RIGHT, fill=tk.Y)

            # Tabla de datos agrupados
            frame_agrupado = ttk.LabelFrame(main_frame, text="Cálculo de Chi-Cuadrado (Datos Agrupados)", padding="10")
            frame_agrupado.pack(fill=tk.X, expand=True, pady=5)
            
            cols_agrup = ('Grupo', 'Oi (agrupado)', 'Ei (agrupado)', '(Oi-Ei)²/Ei')
            tree_agrup = ttk.Treeview(frame_agrupado, columns=cols_agrup, show='headings', height=6)
            for col in cols_agrup:
                tree_agrup.heading(col, text=col)
                tree_agrup.column(col, width=150, anchor='center')
            
            chi_total = 0
            grouped_oi = resultado['grouped_oi']
            grouped_ei = resultado['grouped_ei']
            
            for i in range(len(grouped_oi)):
                oi = grouped_oi[i]
                ei = grouped_ei[i]
                chi_contrib = (oi - ei)**2 / ei if ei > 0 else 0 
                chi_total += chi_contrib
                tree_agrup.insert('', 'end', values=(
                    f"Grupo {i+1}", 
                    f"{oi:.0f}", 
                    f"{ei:.4f}", 
                    f"{chi_contrib:.4f}"
                ))

            tree_agrup.insert('', 'end', values=(
                "TOTAL", 
                f"{sum(grouped_oi):.0f}", 
                f"{sum(grouped_ei):.4f}", 
                f"{chi_total:.4f}"
            ), tags=('total',))
            tree_agrup.tag_configure('total', background='lightblue', font=("Arial", 9, "bold"))
            tree_agrup.pack(fill=tk.X, expand=True)

            # Resultados finales
            frame_resultados = ttk.LabelFrame(main_frame, text="Resultados Finales", padding="10")
            frame_resultados.pack(fill=tk.X, expand=True, pady=10)
            
            ttk.Label(frame_resultados, text=f"Estadístico Chi-cuadrado (χ²): {resultado['estadistico']:.6f}").pack(anchor=tk.W)
            ttk.Label(frame_resultados, text=f"Grados de libertad: {resultado['grados_libertad']}").pack(anchor=tk.W)
            ttk.Label(frame_resultados, text=f"Valor crítico (α={self.alpha}): {resultado['valor_critico']:.6f}").pack(anchor=tk.W)
            ttk.Label(frame_resultados, text=f"P-valor: {resultado['p_valor']:.6f}").pack(anchor=tk.W)
            ttk.Label(frame_resultados, text=f"Número total de datos: {resultado['n_total_datos']}").pack(anchor=tk.W)
            ttk.Label(frame_resultados, text=f"Número de comparaciones: {resultado['n_comparaciones']}").pack(anchor=tk.W)
            
            decision_text = "Se RECHAZA H₀ (Los datos NO son independientes / NO son aleatorios)" if resultado['rechaza_h0'] else "NO se rechaza H₀ (Los datos son independientes / son aleatorios)"
            color = "red" if resultado['rechaza_h0'] else "green"
            ttk.Label(frame_resultados, text=f"Decisión: {decision_text}", 
                     foreground=color, font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=5)
            
            print("Debug: Ventana creada exitosamente")
            return ventana
            
        except Exception as e:
            error_msg = f"Error al mostrar la tabla: {str(e)}"
            print(f"Debug: {error_msg}")
            import traceback
            traceback.print_exc()
            if parent:
                messagebox.showerror("Error", error_msg)
            return None

def main_asc_desc():
    print("=== INICIANDO PRUEBAS ===")
    
    # Datos de prueba más simples
    np.random.seed(42)
    datos_test_aleatorios = np.random.rand(50)  # Reducir tamaño para debug
    datos_test_tendencia = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])  # Datos simples

    alpha = 0.05
    
    print("\n--- Prueba con datos de tendencia simple ---")
    try:
        print("Creando instancia de prueba...")
        prueba_tendencia = LongitudRachasAscendenteDescendente(datos_test_tendencia, alpha=alpha)
        
        print("Ejecutando prueba...")
        resultado_tendencia = prueba_tendencia.ejecutar()
        
        if 'error' in resultado_tendencia:
            print(f"Error en la prueba: {resultado_tendencia['error']}")
        else:
            print(f"✓ Prueba ejecutada exitosamente")
            print(f"Chi-cuadrado: {resultado_tendencia['estadistico']:.6f}")
            print(f"P-valor: {resultado_tendencia['p_valor']:.6f}")
            print(f"Decisión: {'Rechaza H0' if resultado_tendencia['rechaza_h0'] else 'No rechaza H0'}")
        
        print("Mostrando tabla...")
        ventana_tendencia = prueba_tendencia.mostrar_tabla_detallada()
        if ventana_tendencia:
            print("Ventana creada, iniciando mainloop...")
            ventana_tendencia.mainloop()
        else:
            print("No se pudo crear la ventana")

    except Exception as e:
        print(f"Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main_asc_desc()