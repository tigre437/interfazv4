from PyQt6.QtCore import QThread, pyqtSignal
import pyqtgraph as pg

class ActualizarGraficaThread(QThread):
    update_signal = pyqtSignal(list, list, list)

    def __init__(self, lauda_instance):
        super().__init__()
        self.lauda = lauda_instance

    def run(self):
        global temp_bloc, temp_liquid, temp_set
        
        # Generar valores aleatorios para las temperaturas
        nuevo_valor_bloque = self.lauda.get_t_ext()
        nuevo_valor_liquido = self.lauda.get_t_int()
        nuevo_valor_consigna = self.lauda.get_t_set()

        # Verificar si los valores son números válidos antes de agregarlos a las listas
        if isinstance(nuevo_valor_bloque, (int, float)) and \
        isinstance(nuevo_valor_liquido, (int, float)) and \
        isinstance(nuevo_valor_consigna, (int, float)):
            
            # Añadir el nuevo valor a cada lista de temperatura
            temp_bloc.append(nuevo_valor_bloque)
            temp_liquid.append(nuevo_valor_liquido)
            temp_set.append(nuevo_valor_consigna)
        else:
            # Si algún valor no es un número válido, no lo agregues a las listas
            print("Alguno de los valores de temperatura no es válido:", nuevo_valor_bloque, nuevo_valor_liquido, nuevo_valor_consigna)

        self.update_signal.emit(temp_bloc, temp_liquid, temp_set)