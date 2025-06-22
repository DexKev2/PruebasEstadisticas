import pandas as pd
from collections import defaultdict
import math
from scipy.stats import norm
import tkinter as tk
from tkinter import ttk

class RachasEncimaDebajo:
    def __init__(self, datos, alpha=0.05):
        """
        Inicializa la prueba de rachas encima y debajo
        
        Args:
            datos: array de números aleatorios
            alpha: nivel de significancia
        """
        self.datos = datos
        self.alpha = alpha
        self.numeros = datos.tolist() if hasattr(datos, 'tolist') else list(datos)
        
        # Variables para almacenar resultados
        self.simbolos = []
        self.n1 = 0  # total de símbolos positivos
        self.n2 = 0  # total de símbolos negativos
        self.grupos = []
        self.B = 0  # total de grupos
        self.conteo_longitudes = defaultdict(int)
        self.tabla = None
        
        # Estadísticos de la prueba
        self.mu_B = 0
        self.sigma2_B = 0
        self.sigma_B = 0
        self.z_prueba = 0
        self.z_teorico = 0
        self.p_valor = 0
        
    def ejecutar(self):
        """
        Ejecuta la prueba de rachas completa
        
        Returns:
            dict: Diccionario con los resultados de la prueba
        """
        try:
            # Paso 1: Convertir números a símbolos (+ o -)
            self._convertir_a_simbolos()
            
            # Paso 2: Contar cantidad de símbolos individuales
            self._contar_simbolos()
            
            # Paso 3: Agrupar símbolos consecutivos iguales
            self._agrupar_simbolos()
            
            # Paso 4: Contar grupos por longitud
            self._contar_longitudes()
            
            # Paso 5: Crear tabla
            self._crear_tabla()
            
            # Paso 6: Calcular estadísticos
            self._calcular_estadisticos()
            
            # Paso 7: Evaluar hipótesis
            return self._evaluar_hipotesis()
            
        except Exception as e:
            return {
                'error': True,
                'mensaje': f"Error en la prueba de rachas: {str(e)}",
                'tipo_prueba': 'Prueba de Rachas',
                'alpha': self.alpha
            }
    
    def _convertir_a_simbolos(self):
        """Convierte números a símbolos (+ o -)"""
        self.simbolos = ['+' if x >= 0.5 else '-' for x in self.numeros]
    
    def _contar_simbolos(self):
        """Cuenta la cantidad de símbolos individuales"""
        self.n1 = self.simbolos.count('+')  # total de símbolos positivos
        self.n2 = self.simbolos.count('-')  # total de símbolos negativos
    
    def _agrupar_simbolos(self):
        """Agrupa símbolos consecutivos iguales"""
        if not self.simbolos:
            return
            
        self.grupos = []
        longitud = 1
        simbolo_actual = self.simbolos[0]
        self.B = 0
        
        for i in range(1, len(self.simbolos)):
            if self.simbolos[i] == simbolo_actual:
                longitud += 1
            else:
                self.grupos.append((simbolo_actual, longitud))
                self.B += 1
                simbolo_actual = self.simbolos[i]
                longitud = 1
        
        # Agregar el último grupo
        self.grupos.append((simbolo_actual, longitud))
        self.B += 1
    
    def _contar_longitudes(self):
        """Cuenta grupos por longitud"""
        self.conteo_longitudes = defaultdict(int)
        for _, longitud in self.grupos:
            self.conteo_longitudes[longitud] += 1
    
    def _crear_tabla(self):
        """Crea tabla con los resultados"""
        self.tabla = pd.DataFrame({
            'LONGITUD': sorted(self.conteo_longitudes.keys()),
            'TOTAL': [self.conteo_longitudes[k] for k in sorted(self.conteo_longitudes.keys())]
        })
    
    def _calcular_estadisticos(self):
        """Calcula los estadísticos de la prueba"""
        # Cálculo de μB
        self.mu_B = (2 * self.n1 * self.n2) / (self.n1 + self.n2) + 1
        
        # Cálculo de σ²B (varianza de B)
        self.sigma2_B = (2 * self.n1 * self.n2 * (2 * self.n1 * self.n2 - self.n1 - self.n2)) / ((self.n1 + self.n2) ** 2 * (self.n1 + self.n2 - 1))
        
        # Cálculo de σB (desviación estándar de B)
        self.sigma_B = math.sqrt(self.sigma2_B)
        
        # Cálculo de z (valor estandarizado)
        if self.sigma_B != 0:
            self.z_prueba = abs((self.B - self.mu_B) / self.sigma_B)
        else:
            self.z_prueba = 0
        
        # Z teórico para prueba bilateral
        self.z_teorico = norm.ppf(1 - self.alpha / 2)
        
        # Cálculo del p-valor
        self.p_valor = 2 * (1 - norm.cdf(abs(self.z_prueba)))
    
    def _evaluar_hipotesis(self):
        """Evalúa la hipótesis y retorna los resultados"""
        rechaza_h0 = abs(self.z_prueba) > self.z_teorico
        
        return {
            'estadistico': self.z_prueba,
            'valor_critico': self.z_teorico,
            'p_valor': self.p_valor,
            'rechaza_h0': rechaza_h0,
            'tipo_prueba': 'Prueba de Rachas',
            'alpha': self.alpha,
            'B': self.B,
            'mu_B': self.mu_B,
            'sigma_B': self.sigma_B,
            'n1': self.n1,
            'n2': self.n2,
            'total_datos': len(self.numeros)
        }
    
    def obtener_tabla_detallada(self):
        """
        Retorna la tabla detallada con longitudes y frecuencias
        
        Returns:
            pd.DataFrame: Tabla con longitudes y totales
        """
        return self.tabla
    
    def obtener_grupos_detallados(self):
        """
        Retorna información detallada de los grupos
        
        Returns:
            list: Lista de tuplas (símbolo, longitud)
        """
        return self.grupos
    
    def obtener_simbolos(self):
        """
        Retorna la secuencia de símbolos
        
        Returns:
            list: Lista de símbolos (+ o -)
        """
        return self.simbolos
    
    def mostrar_tabla_detallada(self, parent=None):
        """
        Muestra una ventana con la tabla detallada de la prueba de rachas
        
        Args:
            parent: Ventana padre de tkinter
        """
        ventana = tk.Toplevel(parent if parent else tk.Tk())
        ventana.title("Detalle - Prueba de Rachas")
        ventana.geometry("800x600")
        
        # Crear notebook para pestañas
        notebook = ttk.Notebook(ventana)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña 1: Estadísticos principales
        frame_estadisticos = ttk.Frame(notebook)
        notebook.add(frame_estadisticos, text="Estadísticos")
        
        # Crear texto con estadísticos
        text_estadisticos = tk.Text(frame_estadisticos, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar_estadisticos = ttk.Scrollbar(frame_estadisticos, orient="vertical", command=text_estadisticos.yview)
        text_estadisticos.configure(yscrollcommand=scrollbar_estadisticos.set)
        
        estadisticos_info = f"""PRUEBA DE RACHAS - ESTADÍSTICOS DETALLADOS
{'='*50}

DATOS BÁSICOS:
• Total de datos: {len(self.numeros)}
• Símbolos '+' (≥ 0.5): {self.n1}
• Símbolos '-' (< 0.5): {self.n2}
• Total de grupos (B): {self.B}

ESTADÍSTICOS DE LA PRUEBA:
• Media esperada (μB): {self.mu_B:.6f}
• Varianza (σ²B): {self.sigma2_B:.6f}
• Desviación estándar (σB): {self.sigma_B:.6f}
• Estadístico Z calculado: {self.z_prueba:.6f}
• Valor crítico Z: {self.z_teorico:.6f}
• P-valor: {self.p_valor:.6f}
• Nivel de significancia (α): {self.alpha}

DECISIÓN:
• {'Se RECHAZA H0' if abs(self.z_prueba) > self.z_teorico else 'NO se rechaza H0'}
• {'Los datos NO son aleatorios' if abs(self.z_prueba) > self.z_teorico else 'Los datos son aleatorios'}

INTERPRETACIÓN:
La prueba de rachas evalúa si los datos son aleatorios mediante el análisis
de grupos consecutivos de símbolos iguales. Un número muy alto o muy bajo
de grupos puede indicar falta de aleatoriedad.
"""
        
        text_estadisticos.insert(tk.END, estadisticos_info)
        text_estadisticos.config(state=tk.DISABLED)
        
        text_estadisticos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_estadisticos.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pestaña 2: Tabla de longitudes
        frame_tabla = ttk.Frame(notebook)
        notebook.add(frame_tabla, text="Tabla de Longitudes")
        
        # Crear treeview para la tabla
        tree_tabla = ttk.Treeview(frame_tabla, columns=('Longitud', 'Total'), show='headings', height=15)
        tree_tabla.heading('Longitud', text='Longitud de Grupo')
        tree_tabla.heading('Total', text='Frecuencia')
        tree_tabla.column('Longitud', width=150, anchor='center')
        tree_tabla.column('Total', width=150, anchor='center')
        
        # Llenar la tabla
        if self.tabla is not None:
            for _, row in self.tabla.iterrows():
                tree_tabla.insert('', tk.END, values=(row['LONGITUD'], row['TOTAL']))
        
        scrollbar_tabla = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree_tabla.yview)
        tree_tabla.configure(yscrollcommand=scrollbar_tabla.set)
        
        tree_tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_tabla.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Pestaña 3: Secuencia de símbolos
        frame_simbolos = ttk.Frame(notebook)
        notebook.add(frame_simbolos, text="Secuencia de Símbolos")
        
        text_simbolos = tk.Text(frame_simbolos, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar_simbolos = ttk.Scrollbar(frame_simbolos, orient="vertical", command=text_simbolos.yview)
        text_simbolos.configure(yscrollcommand=scrollbar_simbolos.set)
        
        # Mostrar primeros datos y sus símbolos
        simbolos_info = "CONVERSIÓN DE DATOS A SÍMBOLOS\n"
        simbolos_info += "="*40 + "\n\n"
        simbolos_info += "Criterio: '+' si dato ≥ 0.5, '-' si dato < 0.5\n\n"
        simbolos_info += "Primeros 50 datos:\n"
        simbolos_info += f"{'Índice':<6} {'Dato':<10} {'Símbolo':<8}\n"
        simbolos_info += "-" * 25 + "\n"
        
        for i in range(min(50, len(self.numeros))):
            simbolos_info += f"{i+1:<6} {self.numeros[i]:<10.4f} {self.simbolos[i]:<8}\n"
        
        if len(self.numeros) > 50:
            simbolos_info += f"\n... y {len(self.numeros) - 50} datos más\n"
        
        simbolos_info += f"\nSECUENCIA COMPLETA DE SÍMBOLOS:\n"
        simbolos_info += "".join(self.simbolos)
        
        simbolos_info += f"\n\nGRUPOS IDENTIFICADOS:\n"
        simbolos_info += f"{'Grupo':<6} {'Símbolo':<8} {'Longitud':<8}\n"
        simbolos_info += "-" * 25 + "\n"
        
        for i, (simbolo, longitud) in enumerate(self.grupos[:20]):  # Mostrar primeros 20 grupos
            simbolos_info += f"{i+1:<6} {simbolo:<8} {longitud:<8}\n"
        
        if len(self.grupos) > 20:
            simbolos_info += f"\n... y {len(self.grupos) - 20} grupos más\n"
        
        text_simbolos.insert(tk.END, simbolos_info)
        text_simbolos.config(state=tk.DISABLED)
        
        text_simbolos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_simbolos.pack(side=tk.RIGHT, fill=tk.Y)
        
        if parent is None:
            ventana.mainloop()