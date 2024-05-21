import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QGraphicsView, QGraphicsScene, QWidget
from PyQt6.QtCore import Qt
import numpy as np
import pyqtgraph as pg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Prueba de Pintar Gráfica")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.graphicsView = QGraphicsView()
        self.layout.addWidget(self.graphicsView)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.plot_widget = None

        self.pintar_grafica()

    def pintar_grafica(self):
        # Datos de ejemplo
        t_wells = np.arange(100)
        frozen_fraction_B = np.sin(np.linspace(0, 2 * np.pi, 100))
        error_t_wells = np.random.normal(0, 0.1, 100)

        # Crear un widget de gráfico si no existe
        if not self.plot_widget:
            self.plot_widget = pg.PlotWidget()
        else:
            # Limpiar la gráfica anterior
            self.scene.removeItem(self.proxy)

        tiempo_transcurrido = np.arange(len(t_wells)) * 5 / 60  # 5 segundos por punto de datos, convertido a minutos

        # Actualizar los datos de la gráfica
        self.plot_widget.plot(tiempo_transcurrido, frozen_fraction_B, pen='b')  # Línea azul para la temperatura del líquido
        self.plot_widget.fillBetween(tiempo_transcurrido, frozen_fraction_B - error_t_wells, frozen_fraction_B + error_t_wells, brush=(0, 0, 255, 100))

        # Personalizar la apariencia del gráfico
        self.plot_widget.setBackground('k')  # Color de fondo
        self.plot_widget.setTitle('B')  # Título
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)  # Mostrar rejilla
        self.plot_widget.getAxis('bottom').setPen((255, 255, 255))  # Color del eje x
        self.plot_widget.getAxis('left').setPen((255, 255, 255))  # Color del eje y
        self.plot_widget.getAxis('bottom').setTextPen((255, 255, 255))  # Color de los números en el eje x
        self.plot_widget.getAxis('left').setTextPen((255, 255, 255))  # Color de los números en el eje y

        # Agregar etiquetas a los ejes x e y
        self.plot_widget.setLabel('bottom', text='timestamp (s)', color=(255, 255, 255))  # Etiqueta del eje x
        self.plot_widget.setLabel('left', text='temperature (ºC)', color=(255, 255, 255))  # Etiqueta del eje y

        # Mostrar la leyenda
        self.plot_widget.addLegend()

        # Crear un proxy widget para el plot_widget
        self.proxy = self.scene.addWidget(self.plot_widget)

        # Ajustar el tamaño del proxy para que coincida con el plot_widget
        self.proxy.setPos(0, 0)
        self.proxy.resize(self.graphicsView.width() - 2, self.graphicsView.height() - 2)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
