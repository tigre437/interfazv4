###
#Nombre del archivo: app.py
#Autor: David Serrano Henares
#Repositorio GitHub: https://github.com/tigre437/interfazv4
#Funcion: Este archivo contiene la logica de la interfaz.
###

import os
import cv2
import json
import numpy as np
import csv
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import (
    QFileDialog, QDialog, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox, QGraphicsProxyWidget, QListWidgetItem, QDialog, QWidget
)
from PyQt6.QtCore import pyqtSlot, Qt, QTimer
from PyQt6.QtGui import QPixmap, QTransform
from interfazv1 import Ui_MainWindow  # Importa la interfaz de la ventana principal
from pygrabber.dshow_graph import FilterGraph
import datetime
from lauda import Lauda
from VideoThread import VideoThread
from detect_circles import detect_circles
import pandas



ruta_experimento_activo = None
lista_imagenes_analisis = []
temp_bloc = [0]
temp_liquid = [0]
temp_set = [0]
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)  # Configura la interfaz gráfica definida en Ui_MainWindow
        global ruta_experimento_activo
        ruta_experimento_activo = None  # Variable global para almacenar la ruta del experimento activo

        global lauda
        lauda = Lauda()  # Inicializa una instancia de Lauda
        self.video_thread = VideoThread(MainWindow)  # Crea una instancia del hilo de video

        #self.video_thread.start()  # Comenta la línea para no iniciar el hilo de video
        lauda.start()  # Inicia el hilo de lauda

        # Graficas
        scene = QtWidgets.QGraphicsScene()  # Crea una escena gráfica para graphicsView
        ff1 = QtWidgets.QGraphicsScene()  # Crea una escena gráfica para grafica1
        ff2 = QtWidgets.QGraphicsScene()  # Crea una escena gráfica para grafica2

        # Asignar el QGraphicsScene a graphicsView
        self.graphicsView.setScene(scene)
        self.grafica1.setScene(ff1)
        self.grafica2.setScene(ff2)

        # Configurar las barras de desplazamiento de graphicsView para que siempre estén desactivadas
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Configurar las barras de desplazamiento de grafica1 para que siempre estén desactivadas
        self.grafica1.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grafica1.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Configurar las barras de desplazamiento de grafica2 para que siempre estén desactivadas
        self.grafica2.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.grafica2.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Conexiones de los botones con los métodos correspondientes
        self.buttonBuscarArchivos.clicked.connect(self.filechooser)  # Conectar botón "Buscar Archivos" con filechooser
        self.buttonConfiguracion.clicked.connect(self.settings)  # Conectar botón "Configuración" con settings
        self.comboBoxFiltro.addItem("Crear un filtro nuevo ...")  # Añadir opción al comboBoxFiltro

        # Llena el combobox de cámaras disponibles
        self.fillCameras()  # Llenar comboBox con cámaras disponibles
        self.list_cameras()  # Listar cámaras disponibles

        # Conexiones de señales
        self.checkBoxHabilitarA.stateChanged.connect(self.cambiarPlacaA)
        self.checkBoxHabilitarB.stateChanged.connect(self.cambiarPlacaB)
        self.checkBoxAmbasPlacas.stateChanged.connect(self.tab_changed)
        self.checkBoxAmbasPlacas.stateChanged.connect(self.desactivarPlacaB)

        self.comboBoxCamara.currentIndexChanged.connect(self.update_camera_index)
        self.checkBoxHabilitarA.stateChanged.connect(self.cambiarPlacaA)
        self.checkBoxHabilitarB.stateChanged.connect(self.cambiarPlacaB)

        global check_option_lambda
        check_option_lambda = lambda index: self.comprobar_opcion_seleccionada(index, self.comboBoxFiltro)  # Lambda para comprobar opción seleccionada en comboBoxFiltro
        self.comboBoxFiltro.currentIndexChanged.connect(check_option_lambda)  # Conectar lambda a cambio de índice en comboBoxFiltro

        self.buttonGuardarFiltro.clicked.connect(self.guardar_datos_filtro)  # Conectar botón "Guardar Filtro" con guardar_datos_filtro
        self.buttonCancelarFiltro.clicked.connect(self.cancelar_cambios_filtro)  # Conectar botón "Cancelar Filtro" con cancelar_cambios_filtro
        self.buttonIniciar.clicked.connect(self.iniciar_experimento)  # Conectar botón "Iniciar" con iniciar_experimento

        self.buttonGuardarParamDetec.clicked.connect(self.guardar_datos_detection)  # Conectar botón "Guardar Param Detec" con guardar_datos_detection
        self.buttonCancelarParamDetec.clicked.connect(self.cancelar_cambios_detect)  # Conectar botón "Cancelar Param Detec" con cancelar_cambios_detect

        self.buttonGuardarParamTemp.clicked.connect(self.guardar_datos_temp)  # Conectar botón "Guardar Param Temp" con guardar_datos_temp
        self.buttonCancelarParamTemp.clicked.connect(self.cancelar_cambios_temp)  # Conectar botón "Cancelar Param Temp" con cancelar_cambios_temp

        self.buttonCargar.clicked.connect(self.cargar_datos_experimento)  # Conectar botón "Cargar" con cargar_datos_experimento
        self.buttonGuardar.clicked.connect(self.guardar_datos_experimento)  # Conectar botón "Guardar" con guardar_datos_experimento

        self.buttonConectarTermo.clicked.connect(self.conectarTermostato)  # Conectar botón "Conectar Termo" con conectarTermostato

        # Dimensiones para mostrar la imagen
        self.display_width = self.width() // 2  # Definir ancho de la imagen a mostrar
        self.display_height = self.height() // 2  # Definir alto de la imagen a mostrar

        # Conectar Sliders con Spin box
        self.hSliderRadioMin.valueChanged.connect(self.dSpinBoxRadioMin.setValue)  # Conectar hSliderRadioMin con dSpinBoxRadioMin
        self.hSliderRadioMax.valueChanged.connect(self.dSpinBoxRadioMax.setValue)  # Conectar hSliderRadioMax con dSpinBoxRadioMax
        self.hSliderUmbral.valueChanged.connect(self.dSpinBoxUmbral.setValue)  # Conectar hSliderUmbral con dSpinBoxUmbral

        self.hSliderTempSet.valueChanged.connect(self.dSpinBoxTempSet.setValue)  # Conectar hSliderTempSet con dSpinBoxTempSet

        # Conectar Spin boxes con Sliders
        self.dSpinBoxRadioMin.valueChanged.connect(self.hSliderRadioMin.setValue)  # Conectar dSpinBoxRadioMin con hSliderRadioMin
        self.dSpinBoxRadioMax.valueChanged.connect(self.hSliderRadioMax.setValue)  # Conectar dSpinBoxRadioMax con hSliderRadioMax
        self.dSpinBoxUmbral.valueChanged.connect(self.hSliderUmbral.setValue)  # Conectar dSpinBoxUmbral con hSliderUmbral

        # Conectar Sliders con Spin box
        self.hSliderTempSet.valueChanged.connect(self.dSpinBoxTempSet.setValue)  # Conectar hSliderTempSet con dSpinBoxTempSet
        self.hSliderTempInic.valueChanged.connect(self.dSpinBoxTempIni.setValue)  # Conectar hSliderTempInic con dSpinBoxTempIni
        self.hSliderRampa.valueChanged.connect(self.dSpinBoxTempRampa.setValue)  # Conectar hSliderRampa con dSpinBoxTempRampa
        self.hSliderImg.valueChanged.connect(self.dSpinBoxTempImg.setValue)  # Conectar hSliderImg con dSpinBoxTempImg

        # Conectar Spin boxes con Sliders
        self.dSpinBoxTempSet.valueChanged.connect(self.hSliderTempSet.setValue)  # Conectar dSpinBoxTempSet con hSliderTempSet
        self.dSpinBoxTempIni.valueChanged.connect(self.hSliderTempInic.setValue)  # Conectar dSpinBoxTempIni con hSliderTempInic
        self.dSpinBoxTempRampa.valueChanged.connect(self.hSliderRampa.setValue)  # Conectar dSpinBoxTempRampa con hSliderRampa
        self.dSpinBoxTempImg.valueChanged.connect(self.hSliderImg.setValue)  # Conectar dSpinBoxTempImg con hSliderImg

        self.buttonRecargar.clicked.connect(lambda: self.filechooser(True))  # Conectar botón "Recargar" con filechooser(True)

        self.buttonParar.clicked.connect(self.pararExperimento)  # Conectar botón "Parar" con pararExperimento

        self.listExperimentos.itemDoubleClicked.connect(self.mostrar_nombre_experimento)  # Conectar doble clic en item de listExperimentos con mostrar_nombre_experimento
        self.sliderFotos.valueChanged.connect(self.actualizar_imagen)  # Conectar cambio de valor en sliderFotos con actualizar_imagen

        self.buttonRecargar.clicked.connect(lambda index: self.filechooser(self.txtArchivos.text()))  # Conectar botón "Recargar" con filechooser(txtArchivos.text())


        self.comboBoxFiltroAn.currentIndexChanged.connect(lambda index: self.comprobar_opcion_seleccionada(index, self.comboBoxFiltroAn))  # Conectar cambio de índice en comboBoxFiltroAn con lambda que llama a comprobar_opcion_seleccionada

        self.buttonAnalizar.clicked.connect(self.analizar_imagenes)  # Conectar botón "Analizar" con analizar_imagenes

        self.buttonIrTempInic.clicked.connect(self.ir_temp_inic)  # Conectar botón "Ir Temp Inic" con ir_temp_inic

        self.buttonPararTermo.clicked.connect(self.parar_termostato)  # Conectar botón "Parar Termostato" con parar_termostato

        self.timer_rampa = QTimer(self)  # Crear un QTimer para rampa
        self.timer_temp_inicial = QTimer(self)  # Crear un QTimer para temperatura inicial
        self.timer_grafica = QTimer(self)  # Crear un QTimer para gráfica
        self.guardar_temp = QTimer(self)  # Crear un QTimer para guardar temperatura
        self.timer_tomar_fotos = QTimer(self)  # Crear un QTimer para tomar fotos

        self.timer_grafica.timeout.connect(lambda: self.grafica_temperatura(temp_bloc, temp_liquid, temp_set))
        self.timer_temp_inicial.timeout.connect(lambda: self.llevar_temperatura_inicial())
        self.guardar_temp.timeout.connect(self.guardar_temperaturas)


    ######################  DETECCION  ##########################

    def detectar_circulos(self, cv_img=None):
        """Detecta y muestra círculos en las imágenes capturadas desde la cámara."""
        # Capturar una foto utilizando el método capturar_foto()
        if cv_img is None:
            cv_img = self.video_thread.capturar_foto()

        if cv_img is not None:
            # Convertir la imagen a escala de grises
            grey = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

            # Establecer el umbral para crear la imagen binaria
            _, binary = cv2.threshold(grey, self.dSpinBoxUmbral.value(), 255, cv2.THRESH_BINARY)

            # Encontrar los contornos de la imagen binaria
            contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

            circle_list = []

            # Seleccionar contornos cerrados de más de 5 lados, con radio de 15 a 20 píxeles 
            for cnt in contours:
                approx = cv2.approxPolyDP(cnt, .03 * cv2.arcLength(cnt, True), True)
                if len(approx) >= 5:
                    if cv2.isContourConvex(approx):
                        (cx, cy), radius = cv2.minEnclosingCircle(cnt)
                        if radius >= self.dSpinBoxRadioMin.value() and radius <= self.dSpinBoxRadioMax.value():
                            circle_list.append([cx, cy, radius])

            # Convertir la lista de círculos a un array NumPy
            circles = np.array(circle_list)

            # Dibujar todos los círculos detectados en la imagen
            for idx, circle in enumerate(circles, start=1):
                cv2.circle(cv_img, (int(circle[0]), int(circle[1])), int(circle[2]), (0, 255, 0), 2)
                cv2.putText(cv_img, str(idx), (int(circle[0]), int(circle[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2, cv2.LINE_AA)

            # Dividir los círculos en dos listas de 96 si hay suficientes
            if len(circles) >= 192:
                # Ordenar los círculos por la coordenada Y
                circles = circles[circles[:, 1].argsort()]

                # Dividir los círculos en dos listas de 96 cada una
                circles_pcr1 = circles[:96]
                circles_pcr2 = circles[96:192]

                # Ordenar dentro de cada grupo de 96 por la coordenada X
                circles_pcr1 = circles_pcr1[np.argsort(circles_pcr1[:, 0])]
                circles_pcr2 = circles_pcr2[np.argsort(circles_pcr2[:, 0])]

                # Dibujar los círculos detectados en la imagen con los índices
                for idx, circle in enumerate(circles_pcr1, start=1):
                    cv2.putText(cv_img, str(idx), (int(circle[0]), int(circle[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2, cv2.LINE_AA)

                for idx, circle in enumerate(circles_pcr2, start=97):
                    cv2.putText(cv_img, str(idx), (int(circle[0]), int(circle[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2, cv2.LINE_AA)

            return cv_img

        else:
            print("Error al capturar la imagen. No se detectarán círculos.")
            return None


    ######################  ANALISIS  ##########################
    

    def desactivarPlacaB(self):
        """Desactiva los campos relacionados con la placa B si el checkbox 'Ambas Placas' está marcado, de lo contrario, los habilita."""
        if self.checkBoxAmbasPlacas.isChecked():
            self.checkBoxHabilitarB.setEnabled(False)
            self.checkBoxHabilitarA.setEnabled(False)
        else:
            self.checkBoxHabilitarB.setEnabled(True)
            self.checkBoxHabilitarA.setEnabled(True)


    def actualizarEstadoPlacaA(self, habilitar):
        """Actualiza el estado de los campos de la placa A."""
        self.txtNombrePlacaA.setEnabled(habilitar)
        self.txtVDropPlacaA.setEnabled(habilitar)
        self.txtVWashPlacaA.setEnabled(habilitar)
        self.txtFactorDilucPlacaA.setEnabled(habilitar)
        self.txtFraccFiltroPlacaA.setEnabled(habilitar)
        self.txtVelEnfriamientoPlacaA.setEnabled(habilitar)
        self.txtObservPlacaA.setEnabled(habilitar)


    def actualizarEstadoPlacaB(self, habilitar):
        """Actualiza el estado de los campos de la placa B."""
        self.txtNombrePlacaB.setEnabled(habilitar)
        self.txtVDropPlacaB.setEnabled(habilitar)
        self.txtVWashPlacaB.setEnabled(habilitar)
        self.txtFactorDilucPlacaB.setEnabled(habilitar)
        self.txtFraccFiltroPlacaB.setEnabled(habilitar)
        self.txtVelEnfriamientoPlacaB.setEnabled(habilitar)
        self.txtObservPlacaB.setEnabled(habilitar)


    def cambiarPlacaA(self):
        """Habilita o deshabilita los campos relacionados con la placa A según el estado del checkbox."""
        habilitar_b = self.checkBoxHabilitarB.isChecked()
        habilitar_a = self.checkBoxHabilitarA.isChecked()
        self.actualizarEstadoPlacaA(habilitar_a)

        # Si B está activado y A está activado, habilitar el botón de iniciar
        if habilitar_b and habilitar_a:
            self.buttonIniciar.setEnabled(True)
        # Si B está activado pero A no está activado, deshabilitar el botón de iniciar
        elif habilitar_b and not habilitar_a:
            self.buttonIniciar.setEnabled(True)
        elif habilitar_a:
            self.buttonIniciar.setEnabled(True)
        # Si B está desactivado, habilitar el botón de iniciar solo si A está desactivado
        else:
            self.buttonIniciar.setEnabled(False)

        # Habilitar el checkbox de 'Ambas Placas' solo si ambos checkboxes de A y B están desmarcados
        self.checkBoxAmbasPlacas.setEnabled(not habilitar_a and not habilitar_b)


    def cambiarPlacaB(self):
        """Habilita o deshabilita los campos relacionados con la placa B según el estado del checkbox."""
        habilitar_b = self.checkBoxHabilitarB.isChecked()
        habilitar_a = self.checkBoxHabilitarA.isChecked()
        self.actualizarEstadoPlacaB(habilitar_b)
        

        # Si B está activado y A está activado, habilitar el botón de iniciar
        if habilitar_b and habilitar_a:
            self.buttonIniciar.setEnabled(True)
        # Si B está activado pero A no está activado, deshabilitar el botón de iniciar
        elif habilitar_a and not habilitar_b:
            self.buttonIniciar.setEnabled(True)
        elif habilitar_b:
            self.buttonIniciar.setEnabled(True)
        # Si B está desactivado, habilitar el botón de iniciar solo si A está desactivado
        else:
            self.buttonIniciar.setEnabled(False)

        # Habilitar el checkbox de 'Ambas Placas' solo si ambos checkboxes de A y B están desmarcados
        self.checkBoxAmbasPlacas.setEnabled(not habilitar_a and not habilitar_b)


            
    def buscar_carpetas(self, directorio, codigo):
        """Retorna una lista de carpetas que comienzan con 'SNS' dentro del directorio dado."""
        carpetas = [nombre for nombre in os.listdir(directorio) if os.path.isdir(os.path.join(directorio, nombre))]  # Obtiene una lista de nombres de carpetas dentro del directorio
        carpetas_sns = [carpeta for carpeta in carpetas if carpeta.startswith(codigo)]  # Filtra las carpetas que comienzan con el código dado
        return carpetas_sns  # Retorna la lista de carpetas filtradas


    def filechooser(self, folder=None):
        """Abre un diálogo para seleccionar una carpeta."""
        if not folder:  # Si no se proporciona una carpeta específica
            selected_folder = QFileDialog.getExistingDirectory(self)  # Abre un diálogo para seleccionar una carpeta
            if selected_folder:
                carpeta_seleccionada = selected_folder
            else:
                carpeta_seleccionada = self.txtArchivos.text()  # Usa el valor anterior si se cancela
        else:
            carpeta_seleccionada = self.txtArchivos.text()  # Usa la carpeta proporcionada

        self.txtArchivos.setText(carpeta_seleccionada)  # Actualiza el campo de texto con la carpeta seleccionada
        carpetas_sns = self.buscar_carpetas(carpeta_seleccionada, "SNS")  # Busca las carpetas que comienzan con "SNS"
        carpetas_ugr = self.buscar_carpetas(carpeta_seleccionada, "UGR")  # Busca las carpetas que comienzan con "UGR"
        carpetas_lab = self.buscar_carpetas(carpeta_seleccionada, "LAB")  # Busca las carpetas que comienzan con "LAB"
        
        # Limpia y llena los combobox con las carpetas encontradas
        self.comboBoxFiltro.clear()
        self.comboBoxFiltroAn.clear()
        self.comboBoxFiltro.addItem("Crear un filtro nuevo ...")
        if carpetas_sns:
            for carpeta in carpetas_sns:
                self.comboBoxFiltro.addItem(carpeta)
                self.comboBoxFiltroAn.addItem(carpeta)
        if carpetas_ugr:
            for carpeta in carpetas_ugr:
                self.comboBoxFiltro.addItem(carpeta)
                self.comboBoxFiltroAn.addItem(carpeta)
        if carpetas_lab:
            for carpeta in carpetas_lab:
                self.comboBoxFiltro.addItem(carpeta)
                self.comboBoxFiltroAn.addItem(carpeta)
        
        # Muestra una advertencia si no se encuentran carpetas de filtros específicas
        if not carpetas_sns and not carpetas_ugr and not carpetas_lab:
            QMessageBox.warning(self, "Alerta", "No se encontraron carpetas de filtros 'SNS', 'UGR' o 'LAB' dentro de la carpeta seleccionada.")


    def comprobar_opcion_seleccionada(self, index, combobox):
        """Comprueba la opción seleccionada en el combobox de filtros."""
        if index == -1:  # Si no se ha seleccionado ninguna opción
            pass  # No hace nada
        elif index == 0 and combobox == self.comboBoxFiltro:  # Si se selecciona la opción de crear un nuevo filtro en el combobox de filtros
            if(self.txtArchivos.text() == None or self.txtArchivos.text() == ""):
                QMessageBox.warning(self, "Alerta", "Seleccione una carpeta para guardar los filtros antes de continuar.")  # Muestra una advertencia si no se ha seleccionado una carpeta
                self.comboBoxFiltro.currentIndexChanged.disconnect(check_option_lambda)  # Desconecta la señal para evitar recursión
                self.comboBoxFiltro.setCurrentIndex(-1)  # Reinicia el índice seleccionado
                self.comboBoxFiltro.currentIndexChanged.connect(check_option_lambda)  # Vuelve a conectar la señal
                self.filechooser()  # Abre el diálogo para seleccionar una carpeta
            nombre_carpeta = self.obtener_nombre_carpeta()  # Obtiene el nombre de la carpeta para el nuevo filtro
            if nombre_carpeta:
                self.crear_carpeta(nombre_carpeta)  # Crea la carpeta con el nombre proporcionado
        else:  # Si se selecciona una opción existente en el combobox de filtros
            if combobox == self.comboBoxFiltro:  # Si el combobox es el de filtros
                # Lee los datos de los archivos JSON correspondientes y los muestra en los campos
                datos_filtro = self.leer_json_filtro(self.txtArchivos.text() + "/" + combobox.currentText() + "/" + "filter.json")
                if (datos_filtro != None):
                    self.rellenar_datos_filtro(datos_filtro)

                datos_detection = self.leer_json_detection(self.txtArchivos.text() + "/" + combobox.currentText() + "/" + "detection.json")
                if (datos_detection != None):
                    self.rellenar_datos_detection(datos_detection)

                datos_temp = self.leer_json_temp(self.txtArchivos.text() + "/" + combobox.currentText() + "/" + "temp.json")
                if (datos_temp != None):
                    self.rellenar_datos_temp(datos_temp)
            else:
                if(combobox.currentText().startswith("LAB")):
                    self.cargar_lista_experimentos(self.txtArchivos.text())
                else:
                    self.cargar_lista_experimentos(self.txtArchivos.text() + "/" + combobox.currentText())


    def cancelar_cambios_filtro(self):
        """Cancela la edición del filtro seleccionado."""
        datos_filtro = self.leer_json_filtro(self.obtener_ruta_json("filter.json"))
        if (datos_filtro != None):
            self.rellenar_datos_filtro(datos_filtro)


    def cancelar_cambios_detect(self):
        """Cancela la edición del filtro seleccionado."""
        datos_detection = self.leer_json_detection(self.obtener_ruta_json("detection.json"))
        if (datos_detection != None):
            self.rellenar_datos_detection(datos_detection)


    def cancelar_cambios_temp(self):
        """Cancela la edición del filtro seleccionado."""
        datos_temp = self.leer_json_temp(self.obtener_ruta_json("temp.json"))
        if (datos_temp != None):
            self.rellenar_datos_temp(datos_temp)


    def obtener_nombre_carpeta(self):
        """Abre un diálogo para ingresar el nombre de la carpeta."""
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Nombre del filtro")
        
        etiqueta = QLabel("Ingrese el nombre del filtros:")  # Etiqueta para indicar al usuario qué debe ingresar
        campo_texto = QLineEdit()  # Campo de texto para que el usuario ingrese el nombre
        boton_aceptar = QPushButton("Aceptar")  # Botón para aceptar la entrada
        boton_cancelar = QPushButton("Cancelar")  # Botón para cancelar la entrada

        layout = QVBoxLayout()  # Layout para organizar los elementos
        layout.addWidget(etiqueta)  # Agregar la etiqueta al layout
        layout.addWidget(campo_texto)   # Agregar el campo de texto al layout
        layout.addWidget(boton_aceptar)  # Agregar el botón de aceptar al layout
        layout.addWidget(boton_cancelar)  # Agregar el botón de cancelar al layout

        dialogo.setLayout(layout)  # Configurar el layout para que se vea bien en el diálogo

        def aceptar():  # Función para aceptar la entrada
            nombre_carpeta = campo_texto.text()  # Obtener el nombre de la carpeta
            if nombre_carpeta:  # Si el nombre de la carpeta no es vacío
                dialogo.accept()    # Aceptar la entrada

        boton_aceptar.clicked.connect(aceptar)  # Conectar el botón de aceptar a la función aceptar
        boton_cancelar.clicked.connect(dialogo.reject)  # Conectar el botón de cancelar a la función cancelar

        if dialogo.exec() == QDialog.DialogCode.Accepted:  # Si se acepta la entrada
            return campo_texto.text()  # Devuelve el nombre de la carpeta
        else:  # Si se cancela la entrada
            return None  # Devuelve None


    def crear_carpeta(self, nombre_carpeta):
        """Crea una carpeta para el nuevo filtro."""
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d")  # Obtiene la fecha actual en formato YYYYMMDD
        nombre_carpeta_sns = f"SNS_{fecha_actual}_{nombre_carpeta}"  # Construye el nombre de la carpeta con el prefijo 'SNS', la fecha actual y el nombre proporcionado
        directorio_seleccionado = self.txtArchivos.text()  # Obtiene el directorio seleccionado desde el campo de texto en la interfaz
        
        if os.path.isdir(directorio_seleccionado):  # Verifica si el directorio seleccionado es válido
            ruta_carpeta_sns = os.path.join(directorio_seleccionado, nombre_carpeta_sns)  # Obtiene la ruta completa para la nueva carpeta
            os.makedirs(ruta_carpeta_sns)  # Crea la carpeta en la ruta especificada
            print(f"Carpeta '{nombre_carpeta_sns}' creada exitosamente en '{directorio_seleccionado}'.")  # Imprime un mensaje de éxito en la consola
            carpetas_sns = self.buscar_carpetas_sns(directorio_seleccionado)  # Busca todas las carpetas 'SNS' en el directorio
            carpetas_ugr = self.buscar_carpetas_ugr(directorio_seleccionado)  # Busca todas las carpetas 'UGR' en el directorio

            # Desconecta la señal currentIndexChanged para evitar recursión
            self.comboBoxFiltro.currentIndexChanged.disconnect(check_option_lambda)
            self.comboBoxFiltro.clear()  # Limpia el combobox de filtros
            self.comboBoxFiltro.addItem("Crear un filtro nuevo ...")  # Añade la opción para crear un filtro nuevo
            for carpeta in carpetas_sns:
                self.comboBoxFiltro.addItem(carpeta)  # Añade las carpetas 'SNS' encontradas al combobox
            for carpeta in carpetas_ugr:
                self.comboBoxFiltro.addItem(carpeta)  # Añade las carpetas 'UGR' encontradas al combobox
            self.comboBoxFiltro.setCurrentText(nombre_carpeta_sns)  # Establece el nuevo filtro creado como el filtro actualmente seleccionado

            # Crea el archivo filter.json para el nuevo filtro
            self.crear_json_filtro(ruta_carpeta_sns)
            
            # Carga los datos del filtro recién creado en la interfaz
            self.comprobar_opcion_seleccionada(1, self.comboBoxFiltro)  # Índice 1 para seleccionar el nuevo filtro en el combobox

            # Vuelve a conectar la señal currentIndexChanged para que el combobox funcione correctamente
            self.comboBoxFiltro.currentIndexChanged.connect(check_option_lambda)
            
        else:  # Si el directorio seleccionado no es válido
            print("Error: El directorio seleccionado no es válido.")  # Imprime un mensaje de error en la consola



    ######################### TERMOSTATO ################################

    def conectarTermostato(self):

        # Modifique el archivo lauda.py para que devuelva un valor si se conecta correctamente, cosa que no hace de serie
        #
        #def start(self):
        #result = self._send_command('START')
        #if result == '0K':
        #    self.standby = 0
        #    time.sleep(15)
        #return result
        #
        # Esa es la funcion MODIFICADA del archivo lauda.py que devuelve un valor si se conecta correctamente

        url = self.txtIpTermos.text()  # Obtiene la URL del termostato desde el campo de texto en la interfaz
        result = lauda.open(url)  # Intenta abrir una conexión con el termostato utilizando la URL proporcionada
        if result is None:  # Si no se obtiene ninguna respuesta
            QMessageBox.critical(self, "Error de conexion", "No se pudo conectar con el termostato, vuelva a intentarlo en unos segundos")  # Muestra un mensaje de error de conexión
        elif "Could not open" in result:  # Si se recibe un mensaje de error en la respuesta
            QMessageBox.critical(self, "Error de conexion", "No se pudo conectar con el termostato, vuelva a intentarlo en unos segundos")  # Muestra un mensaje de error de conexión
        else:  # Si se establece la conexión correctamente
            QMessageBox.information(self, "Éxito", "Conexión exitosa con el termostato")  # Muestra un mensaje de éxito de conexión


    ######################### JSON #################################

    def leer_json_filtro(self, archivo_json):
        """Lee un archivo JSON y devuelve los datos relevantes."""
        if not os.path.exists(archivo_json):
            # Si el archivo no existe, crea uno con valores por defecto
            data = {
                'label_filter': 'Sin etiqueta',
                'storage_temperature': 0,
                'sampler_id': 'Sin ID',
                'filter_position': 0,
                'air_volume': 0.0,
                'start_time': 'Sin hora de inicio',
                'end_time': 'Sin hora de fin',
                'observations': 'Sin observaciones'
            }
            with open(archivo_json, 'w') as f:
                json.dump(data, f)
            # Ahora el archivo ha sido creado, así que lo leemos
            return data

        try:
            with open(archivo_json, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Advertencia", f"El archivo '{archivo_json}' no es un archivo JSON válido.", QMessageBox.StandardButton.Ok)
            return

        return {
            'label_filter': data.get('label_filter', 'Sin etiqueta'),
            'storage_temperature': data.get('storage_temperature', 0),
            'sampler_id': data.get('sampler_id', 'Sin ID'),
            'filter_position': data.get('filter_position', 0),
            'air_volume': data.get('air_volume', 0.0),
            'start_time': data.get('start_time', 'Sin hora de inicio'),
            'end_time': data.get('end_time', 'Sin hora de fin'),
            'observations': data.get('observations', 'Sin observaciones')
        }


    def rellenar_datos_filtro(self, datos):
        """Asigna los valores correspondientes a cada campo de texto."""
        if self.tabWidget.tabText(self.tabWidget.currentIndex()) == "Experimento":
            # Asigna los valores a los campos de texto en la interfaz gráfica
            self.txtNombreFiltro.setText(datos['label_filter'])
            self.txtTempStorage.setText(str(datos['storage_temperature']))
            self.txtIdMuestreador.setText(datos['sampler_id'])
            self.txtPosFilter.setText(str(datos['filter_position']))
            self.txtAirVol.setText(str(datos['air_volume']))
            self.txtHoraInicio.setDateTime(QtCore.QDateTime.fromString(datos['start_time'], "yyyy-MM-dd hh:mm"))
            self.txtHoraFin.setDateTime(QtCore.QDateTime.fromString(datos['end_time'], "yyyy-MM-dd hh:mm"))
            
            # Verifica si hay observaciones y las asigna al campo de texto correspondiente
            if datos['observations'] is not None:
                self.txaObservFiltro.setPlainText(datos['observations'])
            else:
                self.txaObservFiltro.clear()  # Limpia el campo si las observaciones son nulas


    def crear_json_filtro(self, ruta_carpeta_sns):
        """Crea el archivo filter.json."""
        ruta_filter_json = os.path.join(ruta_carpeta_sns, 'filter.json')
        with open(ruta_filter_json, 'w') as file:
            # Escribe los datos por defecto en el archivo JSON
            json.dump({
                "label_filter": "Sin etiqueta",
                "storage_temperature": "0",
                "sampler_id": "Sin ID",
                "filter_position": "0",
                "air_volume": "0.0",
                "start_time": "2000-01-01 00:00",
                "end_time": "2000-01-01 00:00",
                "observations": "Sin observaciones"
            }, file) 


    def guardar_datos_filtro(self):
        """Guarda los datos del filtro en un archivo JSON."""
        # Obtener los datos de los campos de texto
        label = self.txtNombreFiltro.text()
        storage_temperature = self.txtTempStorage.text()
        sampler_id = self.txtIdMuestreador.text()
        filter_position = self.txtPosFilter.text()
        air_volume = self.txtAirVol.text()
        start_time = self.txtHoraInicio.dateTime().toString("yyyy-MM-dd hh:mm")
        end_time = self.txtHoraFin.dateTime().toString("yyyy-MM-dd hh:mm")
        observations = self.txaObservFiltro.toPlainText()

        # Crear un diccionario con los datos
        datos_filtro = {
            'label_filter': label,
            'storage_temperature': storage_temperature,
            'sampler_id': sampler_id,
            'filter_position': filter_position,
            'air_volume': air_volume,
            'start_time': start_time,
            'end_time': end_time,
            'observations': observations
        }

        # Obtener la ruta del archivo JSON
        ruta_json = self.obtener_ruta_json("filter.json")

        # Guardar los datos en el archivo JSON
        with open(ruta_json, 'w') as file:
            json.dump(datos_filtro, file)

        QMessageBox.information(self, "Guardado", "Los datos del filtro se han actualizado correctamente.", QMessageBox.StandardButton.Ok)


    def rellenar_datos_detection(self, datos):
        """Asigna los valores correspondientes a cada campo de texto de detección."""
        self.hSliderUmbral.setValue(datos['threshold'])
        self.dSpinBoxUmbral.setValue(datos['threshold'])
        self.hSliderRadioMin.setValue(datos['min_radius'])
        self.dSpinBoxRadioMin.setValue(datos['min_radius'])
        self.hSliderRadioMax.setValue(datos['max_radius'])
        self.dSpinBoxRadioMax.setValue(datos['max_radius'])


    def leer_json_detection(self, archivo_json):
        """Lee un archivo JSON de detección y devuelve los datos relevantes."""
        if not os.path.exists(archivo_json):
            # Si el archivo no existe, crea uno con valores por defecto
            data = {
                'threshold': self.hSliderUmbral.value(),
                'min_radius': self.dSpinBoxRadioMin.value(),
                'max_radius': self.dSpinBoxRadioMax.value()
            }
            with open(archivo_json, 'w') as f:
                json.dump(data, f)
            # Ahora el archivo ha sido creado, así que lo leemos
            return data

        try:
            with open(archivo_json, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Advertencia", f"El archivo '{archivo_json}' no es un archivo JSON válido.", QMessageBox.StandardButton.Ok)
            return

        return {
            'threshold': data.get('threshold', 240),
            'min_radius': data.get('min_radius', 9),
            'max_radius': data.get('max_radius', 11)
        }


    def guardar_datos_detection(self):
        """Guarda los datos de detección en un archivo JSON."""
        # Obtener los datos de los campos de detección
        threshold = self.dSpinBoxUmbral.value()
        min_radius = self.dSpinBoxRadioMin.value()
        max_radius = self.dSpinBoxRadioMax.value()


        # Crear un diccionario con los datos de detección
        datos_detection = {
            'threshold': threshold,
            'min_radius': min_radius,
            'max_radius': max_radius
        }

        # Obtener la ruta del archivo JSON
        ruta_json = self.obtener_ruta_json("detection.json")

        # Guardar los datos de detección en el archivo JSON
        with open(ruta_json, 'w') as file:
            json.dump(datos_detection, file)

        QMessageBox.information(self, "Guardado", "Los datos de detección se han actualizado correctamente.", QMessageBox.StandardButton.Ok)


    def leer_json_temp(self, archivo_json):
        """Lee un archivo JSON de temperatura y devuelve los datos relevantes."""
        if not os.path.exists(archivo_json):
            # Si el archivo no existe, crea uno con valores por defecto
            data = {
                'Rampa': self.dSpinBoxTempRampa.value(),
                'tempIni': self.dSpinBoxTempIni.value(),
                'tempSet': self.dSpinBoxTempSet.value(),
                'tempImg': self.dSpinBoxTempImg.value()
            }
            with open(archivo_json, 'w') as f:
                json.dump(data, f)
            # Ahora el archivo ha sido creado, así que lo leemos
            return data

        try:
            with open(archivo_json, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Advertencia", f"El archivo '{archivo_json}' no es un archivo JSON válido.", QMessageBox.StandardButton.Ok)
            return

        return {
            'Rampa': data.get('Rampa', 0.00),
            'tempIni': data.get('tempIni', 0.00),
            'tempSet': data.get('tempSet', 0.00),
            'tempImg': data.get('tempImg', 0.00)
        }

        
    def rellenar_datos_temp(self, datos):
        """Asigna los valores correspondientes a cada campo de texto de temperatura."""
        print(type(datos['Rampa']))
        self.dSpinBoxTempRampa.setValue(datos['Rampa'])
        self.dSpinBoxTempIni.setValue(datos['tempIni'])
        self.dSpinBoxTempSet.setValue(datos['tempSet'])
        self.dSpinBoxTempImg.setValue(datos['tempImg'])


    def guardar_datos_temp(self):
        """Guarda los datos de temperatura en un archivo JSON."""
        # Obtener los datos de los campos de temperatura
        temp_rampa = self.dSpinBoxTempRampa.value()
        temp_ini = self.dSpinBoxTempIni.value()
        temp_set = self.dSpinBoxTempSet.value()
        temp_img = self.dSpinBoxTempImg.value()

        # Crear un diccionario con los datos de temperatura
        datos_temp = {
            'Rampa': temp_rampa,
            'tempIni': temp_ini,
            'tempSet': temp_set,
            'tempImg': temp_img
        }

        # Obtener la ruta del archivo JSON
        ruta_json = self.obtener_ruta_json("temp.json")

        # Guardar los datos de temperatura en el archivo JSON
        with open(ruta_json, 'w') as file:
            json.dump(datos_temp, file)

        QMessageBox.information(self, "Guardado", "Los datos de temperatura se han actualizado correctamente.", QMessageBox.StandardButton.Ok)


    def obtener_ruta_json(self, archivo):
        """Obtiene la ruta completa del archivo JSON."""
        # Obtener la fecha actual en formato YYYYMMDD
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d")
        
        # Obtener la carpeta seleccionada desde el campo de texto
        carpeta_seleccionada = self.txtArchivos.text()
        
        # Verificar si se ha seleccionado un filtro en el comboBoxFiltro
        if self.comboBoxFiltro.currentText() == "":
            # Si no se ha seleccionado un filtro, usar un nombre de filtro predeterminado
            nombre_filtro = ""
        else:
            # Si se ha seleccionado un filtro, usar el nombre del filtro seleccionado
            nombre_filtro = self.comboBoxFiltro.currentText()
        
        # Componer la ruta completa del archivo JSON
        ruta_json = os.path.join(carpeta_seleccionada, nombre_filtro, archivo)
        return ruta_json
   


    ######################## GRAFICA ########################

      
    def grafica_temperatura(self, temperatura_bloque, temperatura_liquido, temperatura_consigna):
        """Pinta una gráfica utilizando PyQtGraph y la muestra en un QGraphicsView."""
        # Crear un widget de gráfico si no existe
        if not hasattr(self, 'plot_widget'):
            self.plot_widget = pg.PlotWidget()
        else:
            # Limpiar el contenido del widget existente
            self.plot_widget.clear()

        tiempo_transcurrido = np.arange(len(temperatura_bloque)) * 5 / 60  # 5 segundos por punto de datos, convertido a minutos
        print("tiempo_transcurrido", tiempo_transcurrido)

        # Actualizar los datos de la gráfica
        self.plot_widget.plot(tiempo_transcurrido, temperatura_bloque, clear=True, pen=pg.mkPen(color='r'), name='Bloque')  # Línea roja para la temperatura del bloque
        self.plot_widget.plot(tiempo_transcurrido, temperatura_liquido, clear=False, pen=pg.mkPen(color='b'), name='Líquido')  # Línea azul para la temperatura del líquido
        self.plot_widget.plot(tiempo_transcurrido, temperatura_consigna, clear=False, pen=pg.mkPen(color='#939393'), name='Set')  # Línea gris claro para la temperatura de consigna
            
        # Personalizar la apariencia del gráfico
        self.plot_widget.setBackground('k')  # Color de fondo
        self.plot_widget.setTitle('Rampa de enfriamiento')  # Título
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)  # Mostrar rejilla
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='w'))  # Color del eje x
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='w'))  # Color del eje y
        self.plot_widget.getAxis('bottom').setTextPen('w')  # Color de los números en el eje x
        self.plot_widget.getAxis('left').setTextPen('w')  # Color de los números en el eje y

        # Agregar etiquetas a los ejes x e y
        self.plot_widget.setLabel('bottom', text='Tiempo transcurrido (min)', color='w')  # Etiqueta del eje x
        self.plot_widget.setLabel('left', text='Temperatura (ºC)', color='w')  # Etiqueta del eje y

        # Mostrar la leyenda
        self.plot_widget.addLegend()


        # Si no hay un QGraphicsProxyWidget creado, crear uno nuevo
        if not hasattr(self, 'proxy'):
            self.proxy = QGraphicsProxyWidget()
            self.graphicsView.scene().addItem(self.proxy)

        self.proxy.resize(self.graphicsView.width() - 4, self.graphicsView.height() - 4)
        

        # Configurar el widget dentro del proxy
        self.proxy.setWidget(self.plot_widget)


    def grafica_frozen_fraction(self, temperatura, congelacion):
        """Pinta una gráfica utilizando PyQtGraph y la muestra en un QGraphicsView."""
        # Crear un widget de gráfico si no existe
        if not hasattr(self, 'plot_widget2'):
            self.plot_widget2 = pg.PlotWidget()
        self.plot_widget2.setBackground('k')  # Color de fondo
        self.plot_widget2.setTitle('Frozen Fraction')  # Título
        self.plot_widget2.showGrid(x=True, y=True, alpha=0.2)  # Mostrar rejilla
        self.plot_widget2.getAxis('bottom').setPen(pg.mkPen(color='w'))  # Color del eje x
        self.plot_widget2.getAxis('left').setPen(pg.mkPen(color='w'))  # Color del eje y
        self.plot_widget2.getAxis('bottom').setTextPen('w')  # Color de los números en el eje x
        self.plot_widget2.getAxis('left').setTextPen('w')  # Color de los números en el eje y
        # Agregar etiquetas a los ejes x e y
        self.plot_widget2.setLabel('bottom', text='Temperatura (ºC)', color='w')  # Etiqueta del eje x
        self.plot_widget2.setLabel('left', text='Frozen Fraction', color='w')  # Etiqueta del eje y
        # Mostrar la leyenda
        self.plot_widget2.addLegend()

        # Limpiar la escena de grafica1 antes de agregar un nuevo gráfico
        self.grafica1.scene().clear()

        # Crear un proxy widget para el plot_widget
        proxy2 = QGraphicsProxyWidget()
        proxy2.setWidget(self.plot_widget2)

        # Ajustar el tamaño del proxy para que coincida con el plot_widget
        proxy2.setPos(0, 0)
        proxy2.resize(self.grafica1.width(), self.grafica1.height())

        # Agregar el proxy al grafica1
        self.grafica1.scene().addItem(proxy2)

        # Actualizar los datos de la gráfica
        self.plot_widget2.clear()  # Limpiar cualquier dato previo en el gráfico
        congelacion = pandas.Series(congelacion)
        temperatura.index = congelacion.index

        self.plot_widget2.plot(temperatura, congelacion, pen=pg.mkPen(color='r'))


    def grafica_rampa(self, temperatura, congelacion):
        """Pinta una gráfica utilizando PyQtGraph y la muestra en un QGraphicsView."""
        # Crear un widget de gráfico si no existe
        if not hasattr(self, 'plot_widget2'):
            self.plot_widget2 = pg.PlotWidget()
        self.plot_widget2.setBackground('k')  # Color de fondo
        self.plot_widget2.setTitle('Frozen Fraction')  # Título
        self.plot_widget2.showGrid(x=True, y=True, alpha=0.2)  # Mostrar rejilla
        self.plot_widget2.getAxis('bottom').setPen(pg.mkPen(color='w'))  # Color del eje x
        self.plot_widget2.getAxis('left').setPen(pg.mkPen(color='w'))  # Color del eje y
        self.plot_widget2.getAxis('bottom').setTextPen('w')  # Color de los números en el eje x
        self.plot_widget2.getAxis('left').setTextPen('w')  # Color de los números en el eje y
        # Agregar etiquetas a los ejes x e y
        self.plot_widget2.setLabel('bottom', text='Temperatura (ºC)', color='w')  # Etiqueta del eje x
        self.plot_widget2.setLabel('left', text='Frozen Fraction', color='w')  # Etiqueta del eje y
        # Mostrar la leyenda
        self.plot_widget2.addLegend()

        # Limpiar la escena de grafica1 antes de agregar un nuevo gráfico
        self.grafica1.scene().clear()

        # Crear un proxy widget para el plot_widget
        proxy2 = QGraphicsProxyWidget()
        proxy2.setWidget(self.plot_widget2)

        # Ajustar el tamaño del proxy para que coincida con el plot_widget
        proxy2.setPos(0, 0)
        proxy2.resize(self.grafica1.width(), self.grafica1.height())

        # Agregar el proxy al grafica1
        self.grafica1.scene().addItem(proxy2)

        # Actualizar los datos de la gráfica
        self.plot_widget2.clear()  # Limpiar cualquier dato previo en el gráfico
        congelacion = pandas.Series(congelacion)
        temperatura.index = congelacion.index

        self.plot_widget2.plot(temperatura, congelacion, pen=pg.mkPen(color='r'))
   
   

    ######################### EXPERIMENTO #################################

    def obtener_ruta_experimento_json(self):
        """Obtiene la ruta completa del archivo JSON del experimento."""
        # Obtener la fecha y hora actual en formatos YYYYMMDD y HHMM respectivamente
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d")
        hora_actual = datetime.datetime.now().strftime("%H%M")
        
        # Obtener la carpeta seleccionada desde el campo de texto
        carpeta_seleccionada = self.txtArchivos.text()
        
        # Obtener el nombre del filtro seleccionado desde el comboBoxFiltro
        nombre_filtro = self.comboBoxFiltro.currentText().strip()
        
        # Construir la base del nombre del experimento con fecha y hora
        nombre_base = f"{fecha_actual}_{hora_actual}"

        rutas_json = []

        if self.checkBoxAmbasPlacas.isChecked():
            # Caso donde ambas placas están activadas
            nombre_experimento_con_fecha = f"{nombre_base}_{self.txtNombrePlacaA.text().strip()}_AB"
            if nombre_filtro:
                ruta_json = os.path.join(carpeta_seleccionada, nombre_filtro, nombre_experimento_con_fecha, "experimento.json")
            else:
                ruta_json = os.path.join(carpeta_seleccionada, f"LAB_{nombre_experimento_con_fecha}", "experimento.json")
            rutas_json.append(ruta_json)
        else:
            # Caso donde las placas A y/o B pueden estar activadas independientemente
            if self.checkBoxHabilitarA.isChecked():
                nombre_experimento_a = f"{nombre_base}_{self.txtNombrePlacaA.text().strip()}_A"
                if nombre_filtro:
                    ruta_json_a = os.path.join(carpeta_seleccionada, nombre_filtro, nombre_experimento_a, "experimento.json")
                else:
                    ruta_json_a = os.path.join(carpeta_seleccionada, f"LAB_{nombre_experimento_a}", "experimento.json")
                rutas_json.append(ruta_json_a)
            
            if self.checkBoxHabilitarB.isChecked():
                nombre_experimento_b = f"{nombre_base}_{self.txtNombrePlacaB.text().strip()}_B"
                if nombre_filtro:
                    ruta_json_b = os.path.join(carpeta_seleccionada, nombre_filtro, nombre_experimento_b, "experimento.json")
                else:
                    ruta_json_b = os.path.join(carpeta_seleccionada, f"LAB_{nombre_experimento_b}", "experimento.json")
                rutas_json.append(ruta_json_b)
        
        return rutas_json


    def obtener_ruta_experimento(self):
        """Obtiene la ruta completa del directorio del experimento."""
        # Obtener la fecha y hora actual en formatos YYYYMMDD y HHMM respectivamente
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d")
        hora_actual = datetime.datetime.now().strftime("%H%M")
        
        # Obtener la carpeta seleccionada desde el campo de texto
        carpeta_seleccionada = self.txtArchivos.text()
        
        # Obtener el nombre del filtro seleccionado desde el comboBoxFiltro
        nombre_filtro = self.comboBoxFiltro.currentText().strip()
        
        # Construir la base del nombre del experimento con fecha y hora
        nombre_base = f"{fecha_actual}_{hora_actual}"

        rutas_experimentos = []

        if self.checkBoxAmbasPlacas.isChecked():
            # Caso donde ambas placas están activadas
            nombre_experimento_con_fecha = f"{nombre_base}_{self.txtNombrePlacaA.text().strip()}_AB"
            if nombre_filtro:
                ruta_experimento = os.path.join(carpeta_seleccionada, nombre_filtro, nombre_experimento_con_fecha)
            else:
                ruta_experimento = os.path.join(carpeta_seleccionada, f"LAB_{nombre_experimento_con_fecha}")
            rutas_experimentos.append(ruta_experimento)
        else:
            # Caso donde las placas A y/o B pueden estar activadas independientemente
            if self.checkBoxHabilitarA.isChecked():
                nombre_experimento_a = f"{nombre_base}_{self.txtNombrePlacaA.text().strip()}_A"
                if nombre_filtro:
                    ruta_experimento_a = os.path.join(carpeta_seleccionada, nombre_filtro, nombre_experimento_a)
                else:
                    ruta_experimento_a = os.path.join(carpeta_seleccionada, f"LAB_{nombre_experimento_a}")
                rutas_experimentos.append(ruta_experimento_a)
            
            if self.checkBoxHabilitarB.isChecked():
                nombre_experimento_b = f"{nombre_base}_{self.txtNombrePlacaB.text().strip()}_B"
                if nombre_filtro:
                    ruta_experimento_b = os.path.join(carpeta_seleccionada, nombre_filtro, nombre_experimento_b)
                else:
                    ruta_experimento_b = os.path.join(carpeta_seleccionada, f"LAB_{nombre_experimento_b}")
                rutas_experimentos.append(ruta_experimento_b)
        
        return rutas_experimentos


    def iniciar_experimento(self):
        # Comprobar si los timer esta activos o parados
        self.timer_grafica.stop()
        # Configurar temperatura inicial en el equipo Lauda
        global temp
        temp = self.dSpinBoxTempIni.value()
        lauda.set_t_set(self.dSpinBoxTempIni.value())
        lauda.start()

        global temp_bloc
        global temp_liquid
        global temp_set
        temp_bloc = [0]
        temp_liquid = [0]
        temp_set = [0]

        # Leer datos del filtro, detección y temperatura desde archivos JSON
        datos_filtro = self.leer_json_filtro(os.path.join(self.txtArchivos.text(), self.comboBoxFiltro.currentText(), "filter.json"))
        datos_detection = self.leer_json_detection(os.path.join(self.txtArchivos.text(), self.comboBoxFiltro.currentText(), "detection.json"))
        datos_temp = self.leer_json_temp(os.path.join(self.txtArchivos.text(), self.comboBoxFiltro.currentText(), "temp.json"))

        datos_exper_a = {
            "v_drop": float(self.txtVDropPlacaA.text()),
            "v_wash": float(self.txtVWashPlacaA.text()),
            "dil_factor": float(self.txtFactorDilucPlacaA.text()),
            "filter_fraction": float(self.txtFraccFiltroPlacaA.text()),
            "cooling_rate": float(self.txtVelEnfriamientoPlacaA.text()),
            "observations_exp": self.txtObservPlacaA.toPlainText()
        }
        datos_exper_b = {
            "v_drop": float(self.txtVDropPlacaB.text()),
            "v_wash": float(self.txtVWashPlacaB.text()),
            "dil_factor": float(self.txtFactorDilucPlacaB.text()),
            "filter_fraction": float(self.txtFraccFiltroPlacaB.text()),
            "cooling_rate": float(self.txtVelEnfriamientoPlacaB.text()),
            "observations_exp": self.txtObservPlacaB.toPlainText()
        }

        # Obtener las rutas de los archivos JSON del experimento
        rutas_json = self.obtener_ruta_experimento_json()

        for ruta_json in rutas_json:
            ruta_carpeta_experimento = os.path.dirname(ruta_json)
            
            # Verificar y crear la carpeta del experimento si no existe
            if not os.path.exists(ruta_carpeta_experimento):
                os.makedirs(ruta_carpeta_experimento)

            # Verificar y eliminar el archivo JSON si ya existe
            if os.path.exists(ruta_json):
                respuesta = self.mostrar_dialogo_confirmacion("Sobreescribir experimento", "¿Estás seguro de que quieres sobreescribir los datos del experimento?")
                if not respuesta:
                    return  
                else:
                    os.remove(ruta_json)
            
            # Combinar todos los datos del experimento en un solo diccionario
            datos_experimento = {}
            datos_experimento.update(datos_filtro)
            datos_experimento.update(datos_detection)

            if "_A" in ruta_json:
                datos_experimento.update(datos_exper_a)
            elif "_B" in ruta_json:
                datos_experimento.update(datos_exper_b)
            else:
                datos_experimento.update(datos_exper_a)  # Asumir datos de la Placa A para el caso de ambas placas

            # Guardar los datos del experimento en el archivo JSON
            with open(ruta_json, 'w') as file:
                json.dump(datos_experimento, file)

            # Crear el archivo de temperaturas CSV en cada carpeta de experimento
            with open(f'{ruta_carpeta_experimento}/temperaturas.csv', 'w', newline='') as archivo_csv:
                escritor_csv = csv.writer(archivo_csv)
                escritor_csv.writerow(['t_ext', 't_int', 't_set'])

            print(ruta_carpeta_experimento)

        # Habilitar el botón de parar experimento
        self.buttonParar.setEnabled(True)

        # Guardar la configuración actual de temperatura
        self.save(datos_temp)
        
        
        self.timer_temp_inicial.start(60000)

        
        self.guardar_temp.start(5000)

        self.timer_grafica.start(5000)
        self.buttonIniciar.setEnabled(False)


    def pararExperimento(self):
        lauda.stop()
        if self.timer_rampa.isActive():
            self.timer_rampa.stop()
        if self.timer_comprobacion_fotos.isActive():
            self.timer_comprobacion_fotos.stop()
        if self.timer_grafica.isActive():
            self.timer_grafica.stop()
        if self.timer_temp_inicial.isActive():
            self.timer_temp_inicial.stop()
        if self.timer_tomar_fotos.isActive():
            self.timer_tomar_fotos.stop()
        if self.guardar_temp.isActive():
            self.guardar_temp.stop()
        self.buttonParar.setEnabled(False)
        self.buttonIniciar.setEnabled(True)


    def rampa_temperatura(self, objetivo):
        # Función para ajustar la temperatura gradualmente hacia el objetivo
        global temp
        if float(lauda.get_t_set()) > float(objetivo):
            lauda.set_t_set(temp - self.dSpinBoxTempRampa.value())
            temp = temp - self.dSpinBoxTempRampa.value()
        else:
            self.pararExperimento()


    def ir_temp_inic(self):
        # Función para ir a la temperatura inicial establecida
        lauda.set_t_set(self.dSpinBoxTempIni.value())
        lauda.start()
        

    def parar_termostato(self):
        # Función para parar el termostato
        lauda.stop()


    def llevar_temperatura_inicial(self):
        # Función para esperar a que la temperatura se estabilice cerca de la temperatura inicial
        if float(lauda.get_t_ext()) >= (float(lauda.get_t_set()) - 0.2) and float(lauda.get_t_ext()) <= (float(lauda.get_t_set()) + 0.2):
            self.timer_rampa.timeout.connect(lambda: self.rampa_temperatura(self.dSpinBoxTempSet.text()))
            self.timer_rampa.start(60000)
            self.timer_temp_inicial.stop()


    def guardar_temperaturas(self):
        # Función para guardar las temperaturas en un archivo CSV
        temp_bloc.append(float(lauda.get_t_ext()))
        temp_liquid.append(float(lauda.get_t_int()))
        temp_set.append(float(lauda.get_t_set()))
        # Evitar sobreescribir las temperaturas de la imagen
        for ruta in ruta_experimento_activo:
            with open(f'{ruta}/temperaturas.csv', 'a', newline='') as archivo_csv:
                escritor_csv = csv.writer(archivo_csv, delimiter=',')
                escritor_csv.writerow([float(lauda.get_t_ext()), float(lauda.get_t_int()), float(lauda.get_t_set())])


    def mostrar_dialogo_confirmacion(self, titulo, mensaje):
        # Función para mostrar un diálogo de confirmación
        dialogo = QMessageBox()
        dialogo.setWindowTitle(titulo)
        dialogo.setText(mensaje)
        dialogo.setIcon(QMessageBox.Icon.Question)
        dialogo.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dialogo.setDefaultButton(QMessageBox.StandardButton.No)
        respuesta = dialogo.exec()
        return respuesta == QMessageBox.StandardButton.Yes


    def tab_changed(self):
        """Maneja los cambios de estado en los checkboxes y tabs."""
        habilitar_ambas = self.checkBoxAmbasPlacas.isChecked()
        habilitar_a = self.checkBoxHabilitarA.isChecked() or habilitar_ambas
        habilitar_b = self.checkBoxHabilitarB.isChecked()

        self.actualizarEstadoPlacaA(habilitar_a)
        self.actualizarEstadoPlacaB(habilitar_b)

        if habilitar_ambas:
            self.checkBoxHabilitarA.setEnabled(False)
            self.checkBoxHabilitarB.setEnabled(False)
            self.buttonIniciar.setEnabled(True)
        else:
            self.checkBoxHabilitarA.setEnabled(True)
            self.checkBoxHabilitarB.setEnabled(True)
            self.buttonIniciar.setEnabled(False)


    ####################### CAMARA ##############################
    def update_camera_index(self, index):
        # Actualiza el índice de la cámara para mostrar la vista previa en el widget
        if self.video_thread and self.video_thread.isRunning():
            self.video_thread.stop()  # Detener el hilo existente
            self.video_thread.finished.connect(self.video_thread.deleteLater)  # Eliminar el objeto del hilo después de que termine

        self.video_thread = VideoThread(MainWindow)
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.set_camera_index(index)
        self.video_thread.start()


    def list_cameras(self):
        """Obtiene una lista de cámaras disponibles."""
        cameras = []
        filter_graph = FilterGraph()
        devices = filter_graph.get_input_devices()

        for index, device_name in enumerate(devices):
            cameras.append((index, device_name))  # Agregar el índice y el nombre del dispositivo

        return cameras


    def fillCameras(self):
        """Llena el combobox con las cámaras disponibles."""
        available_cameras = self.list_cameras()
        for camera_index, camera_name in available_cameras:
            self.comboBoxCamara.addItem(camera_name)


    def settings(self):
        # Abre la configuración de la cámara
        self.video_thread.settings()


    def save(self, datos_temp):
        # Guarda las imágenes capturadas con la cámara
        global ruta_experimento_activo
        if ruta_experimento_activo is None:
            ruta_experimento_activo = self.obtener_ruta_experimento()
        
        for ruta_imagenes in ruta_experimento_activo:
            ruta = os.path.join(ruta_imagenes, "imagenes")

            # Crear la carpeta "imagenes" si no existe
            if not os.path.exists(ruta):
                os.makedirs(ruta)

        self.timer_comprobacion_fotos = QTimer(self)
        self.timer_comprobacion_fotos.timeout.connect(lambda: self.comprobar_fotos(datos_temp))

        # Iniciar QTimer para que se ejecute cada 60 segundos (60,000 milisegundos)
        self.timer_comprobacion_fotos.start(20000)


    def comprobar_fotos(self, datos_temp):
        # Comprueba si la temperatura exterior está dentro del rango y toma fotos si es así
        global ruta_experimento_activo
        if ruta_experimento_activo is None:
            ruta_experimento_activo = self.obtener_ruta_experimento()
        if float(lauda.get_t_ext()) >= (float(datos_temp['tempImg']) - 0.2) and float(lauda.get_t_ext()) <= (float(datos_temp['tempImg']) + 0.2):
            # Escribir los datos en el archivo CSV
            for ruta in ruta_experimento_activo:
                #Escribir los datos en el archivo CSV
                with open(f'{ruta}/imagenes.csv', 'w', newline='') as archivo_csv:
                    escritor_csv = csv.writer(archivo_csv)
                    escritor_csv.writerow(['Imagen', 'Temperatura'])
            self.timer_tomar_fotos.timeout.connect(lambda: self.tomar_fotos(ruta_experimento_activo))
            self.timer_tomar_fotos.start(5000)
            
            self.timer_comprobacion_fotos.stop()


    def tomar_fotos(self, ruta_imagenes):
        # Captura imágenes con la cámara
        self.video_thread.save(ruta_imagenes, self.checkBoxHabilitarA.isChecked(), self.checkBoxHabilitarB.isChecked(), self.checkBoxAmbasPlacas.isChecked(), float(lauda.get_t_ext()))

    @pyqtSlot(np.ndarray)
    def get_available_cameras(self):
        """Obtiene las cámaras disponibles utilizando pygrabber."""
        devices = FilterGraph().get_input_devices()
        available_cameras = {}
        for device_index, device_name in enumerate(devices):
            available_cameras[device_index] = device_name
        return available_cameras


    def update_image(self, cv_img):
        """Actualiza el QLabel con una nueva imagen de OpenCV"""
        cv_img = cv2.rotate(cv_img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        if self.checkBoxPruebas.isChecked():
            qt_img = self.convert_cv_qt(self.detectar_circulos(cv_img))
        else:
            qt_img = self.convert_cv_qt(cv_img)
        
        # Escalar la imagen para que ocupe todo el espacio del QLabel
        qt_img = qt_img.scaled(self.labelCamara.size(), aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)

        # Ajustar el tamaño del widget labelCamara
        self.labelCamara.setPixmap(qt_img)
        self.labelCamara.setFixedSize(qt_img.size())


    def get_status(self):
        """Actualiza la fecha y hora en el widget datetime."""
        self.datetime.setText(f'{datetime.datetime.now():%m/%d/%Y %H:%M:%S}')


    def convert_cv_qt(self, cv_img):
        """Convierte una imagen de OpenCV a QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.AspectRatioMode.KeepAspectRatio)
        return QPixmap.fromImage(p)


    def leer_json_experimento(self):
        """Lee un archivo JSON de temperatura y devuelve los datos relevantes."""
        if (self.comboBoxFiltroAn.currentText().startswith("LAB")):
            archivo_json = self.txtArchivos.text() + "/" + self.comboBoxFiltroAn.currentText() + "/" + "experimento.json"
        else:
            archivo_json = self.txtArchivos.text() + "/" + self.comboBoxFiltroAn.currentText() + "/" + self.lblExperimentoSeleccionado.text() + "/" + "experimento.json"
        try:
            with open(archivo_json, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            QMessageBox.warning(self, "Advertencia", f"El archivo '{archivo_json}' no existe.", QMessageBox.StandardButton.Ok)
            return
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Advertencia", f"El archivo '{archivo_json}' no es un archivo JSON válido.", QMessageBox.StandardButton.Ok)
            return

        label = data.get('label_filter', '')
        storage_temperature = data.get('storage_temperature', 0.00)
        sampler_id = data.get('sampler_id', '')
        filter_position = data.get('filter_position', 0)
        air_volumen = data.get('air_volumen', 0.00)
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        observations = data.get('observations', '')
        threshold = data.get('threshold', 0.00)
        min_radius = data.get('min_radius', 0.00)
        max_radius = data.get('max_radius', 0.00)
        v_drop = data.get('v_drop', 0.00)
        v_wash = data.get('v_wash', 0.00)
        dil_factor = data.get('dil_factor', 0.00)
        filter_fraction = data.get('filter_fraction', 0.00)
        cooling_rate = data.get('cooling_rate', 0.00)
        observations_exp = data.get('observations_exp', '')

        return {
            'label_filter': label,
            'storage_temperature': storage_temperature,
            'sampler_id': sampler_id,
            'filter_position': filter_position,
            'air_volumen': air_volumen,
            'start_time': start_time,
            'end_time': end_time,
            'observations': observations,
            'threshold': threshold,
            'min_radius': min_radius,
            'max_radius': max_radius,
            'v_drop': v_drop,
            'v_wash': v_wash,
            'dil_factor': dil_factor,
            'filter_fraction': filter_fraction,
            'cooling_rate': cooling_rate,
            'observations_exp': observations_exp
        }


    def cargar_datos_experimento(self):
        """Carga los datos del experimento en los campos correspondientes."""
        datos = self.leer_json_experimento()
        self.txtNombreExperimento.setText(self.lblExperimentoSeleccionado.text())
        self.txtNombreFiltroAn.setText(datos['label_filter'])
        self.txtTempAlmacenamiento.setText(str(datos['storage_temperature']))
        self.txtIdMuestreador_2.setText(datos['sampler_id'])
        self.txtPosicionFiltro.setText(str(datos['filter_position']))
        self.txtVolAire.setText(str(datos['air_volumen']))
        self.txtHoraInicio_2.setDateTime(QtCore.QDateTime.fromString(datos['start_time'], "yyyy-MM-dd hh:mm"))
        self.txtHoraFin_2.setDateTime(QtCore.QDateTime.fromString(datos['end_time'], "yyyy-MM-dd hh:mm"))
        if datos['observations'] is not None:
            self.txtObserv.setPlainText(datos['observations'])
        else:
            self.txtObserv.clear()
        self.txtVDrop.setText(str(datos.get('v_drop', '')))
        self.txtVWash.setText(str(datos.get('v_wash', '')))
        self.txtFactorDiluc.setText(str(datos.get('dil_factor', '')))
        self.txtFraccionFiltro.setText(str(datos.get('filter_fraction', '')))
        self.txtVelEnfriamiento.setText(str(datos.get('cooling_rate', '')))
        self.txtObservExpe.setPlainText(str(datos.get('observations_exp', '')))
        self.cargar_imagenes()


    def cargar_lista_experimentos(self, ruta):
        """Carga la lista de experimentos disponibles."""
        self.listExperimentos.clear()
        carpetas_con_experiment_json = []
        if os.path.exists(ruta) and os.path.isdir(ruta):
            for elemento in os.listdir(ruta):
                if os.path.isdir(os.path.join(ruta, elemento)):
                    if 'experimento.json' in os.listdir(os.path.join(ruta, elemento)):
                        carpetas_con_experiment_json.append(elemento)
        for carpeta in carpetas_con_experiment_json:
            item = QListWidgetItem(carpeta)
            self.listExperimentos.addItem(item)
        return carpetas_con_experiment_json


    def mostrar_nombre_experimento(self, item):
        """Muestra el nombre del experimento seleccionado."""
        self.lblExperimentoSeleccionado.setText(item.text())


    def guardar_datos_experimento(self):
        """Guarda los datos del experimento en un archivo JSON."""
        nombre_experimento = self.lblExperimentoSeleccionado.text()
        nombre_filtro = self.txtNombreFiltroAn.text()
        temp_almacenamiento = float(self.txtTempAlmacenamiento.text())
        id_muestreador = self.txtIdMuestreador_2.text()
        posicion_filtro = int(self.txtPosicionFiltro.text())
        vol_aire = float(self.txtVolAire.text())
        hora_inicio = self.txtHoraInicio_2.dateTime().toString("yyyy-MM-dd hh:mm")
        hora_fin = self.txtHoraFin_2.dateTime().toString("yyyy-MM-dd hh:mm")
        observaciones = self.txtObserv.toPlainText()
        v_drop = float(self.txtVDrop.text())
        v_wash = float(self.txtVWash.text())
        factor_diluc = float(self.txtFactorDiluc.text())
        fraccion_filtro = float(self.txtFraccionFiltro.text())
        vel_enfriamiento = float(self.txtVelEnfriamiento.text())
        observaciones_exp = self.txtObservExpe.toPlainText()
        datos_experimento = {
            'label_filter': nombre_filtro,
            'storage_temperature': temp_almacenamiento,
            'sampler_id': id_muestreador,
            'filter_position': posicion_filtro,
            'air_volumen': vol_aire,
            'start_time': hora_inicio,
            'end_time': hora_fin,
            'observations': observaciones,
            'v_drop': v_drop,
            'v_wash': v_wash,
            'dil_factor': factor_diluc,
            'filter_fraction': fraccion_filtro,
            'cooling_rate': vel_enfriamiento,
            'observations_exp': observaciones_exp
        }
        archivo_json = self.txtArchivos.text() + "/" + self.comboBoxFiltroAn.currentText() + "/" + self.lblExperimentoSeleccionado.text() + "/" + "experimento.json"
        with open(archivo_json, 'w') as file:
            json.dump(datos_experimento, file)
        QMessageBox.information(self, "Guardado", "Los datos del experimento se han actualizado correctamente.", QMessageBox.StandardButton.Ok)


    def cargar_imagenes(self):
        # Ruta de la carpeta que contiene las imágenes
        if (self.comboBoxFiltroAn.currentText().startswith("LAB")):
            carpeta_imagenes = self.txtArchivos.text() + "/" + self.comboBoxFiltroAn.currentText() + "/imagenes"
            carpeta_experimento = self.txtArchivos.text() + "/" + self.comboBoxFiltroAn.currentText()
        else:
            carpeta_imagenes = self.txtArchivos.text() + "/" + self.comboBoxFiltroAn.currentText() + "/" + self.lblExperimentoSeleccionado.text() + "/imagenes"
            carpeta_experimento = self.txtArchivos.text() + "/" + self.comboBoxFiltroAn.currentText() + "/" + self.lblExperimentoSeleccionado.text()
        # Lista para almacenar las imágenes ordenadas como QPixmap
        global lista_imagenes_analisis
        lista_imagenes_analisis = []

        # Obtener la lista de nombres de archivos en la carpeta
        archivos_en_carpeta = os.listdir(carpeta_imagenes)

        # Filtrar solo los archivos de imagen (suponiendo que solo quieres imágenes)
        imagenes = [archivo for archivo in archivos_en_carpeta if archivo.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

        # Ordenar las imágenes por nombre de archivo
        imagenes.sort()

        # Abrir el archivo CSV
        with open(f"{carpeta_experimento}/imagenes.csv", newline='') as csvfile:
            reader = csv.reader(csvfile)
            datos_csv = list(reader)

        # Cargar cada imagen como QPixmap y agregarla a la lista
        for imagen_nombre in imagenes:
            # Crea la ruta de la imagen
            ruta_imagen = os.path.join(carpeta_imagenes, imagen_nombre)
            
            # Carga la imagen como QPixmap
            pixmap = QPixmap(ruta_imagen)
            
            # Aplica cualquier transformación necesaria
            pixmap = pixmap.transformed(QTransform().rotate(-90))
            factor_ajuste = min(self.MostrarPlacaA.width() / pixmap.width(), self.MostrarPlacaA.height() / pixmap.height())
            pixmap = pixmap.scaled(pixmap.width() * factor_ajuste, pixmap.height() * factor_ajuste, Qt.AspectRatioMode.KeepAspectRatio)
            
            # Obtener datos del CSV correspondientes a esta imagen
            nombre_imagen_csv = imagen_nombre.split('.')[0]  # Eliminar la extensión de archivo
            datos_imagen_csv = [fila for fila in datos_csv if fila[0] == nombre_imagen_csv]
            temperatura_imagen = datos_imagen_csv[0][1] if datos_imagen_csv else 'N/A'
            
            # Crea una instancia de la clase Imagen y agrega a la lista
            imagen = Imagen(imagen_nombre, pixmap, temperatura_imagen)
            lista_imagenes_analisis.append(imagen)

        self.sliderFotos.setMaximum(len(lista_imagenes_analisis) - 1) 
        
        self.MostrarPlacaA.setPixmap(lista_imagenes_analisis[0].get_pixmap())
        self.lblImagenA.setText(lista_imagenes_analisis[0].get_nombre())

        
        # Método para actualizar la imagen en un QLabel según el índice seleccionado por un QSlider
    

    def actualizar_imagen(self):
        # Obtener el índice seleccionado por el slider
        indice_imagen = self.sliderFotos.value()
        # Cargar la imagen y mostrarla en el QLabel
        self.MostrarPlacaA.setPixmap(lista_imagenes_analisis[indice_imagen].get_pixmap())
        self.lblImagenA.setText(lista_imagenes_analisis[indice_imagen].get_nombre())
        self.lblTempA.setText(str(lista_imagenes_analisis[indice_imagen].get_temp()))

    # Método para analizar imágenes y graficar la fracción congelada
    def analizar_imagenes(self):
        # Obtener la carpeta del experimento
        carpeta_experimento = self.txtArchivos.text() + "/" + self.comboBoxFiltroAn.currentText() + "/" + self.lblExperimentoSeleccionado.text()
        # Obtener los datos del experimento
        datos_experimento = self.leer_json_experimento()
        threshold = datos_experimento['threshold']
        radio_min = datos_experimento['min_radius']
        radio_max = datos_experimento['max_radius']
        # Detectar círculos y obtener datos para graficar
        ffa, ffb, tw = detect_circles(carpeta_experimento, threshold, 0.99, radio_min, radio_max)
        self.grafica_frozen_fraction(tw, ffa)

####################### OBJETO FOTO ###########################

class Imagen:
    # Clase para representar una imagen con su nombre y temperatura
    def __init__(self, nombre, pixmap, temp):
        self._nombre = nombre
        self._pixmap = pixmap
        self._temp = temp

    def get_nombre(self):
        return self._nombre

    def set_nombre(self, nombre):
        self._nombre = nombre

    def get_pixmap(self):
        return self._pixmap

    def set_pixmap(self, pixmap):
        self._pixmap = pixmap

    def get_temp(self):
        return (str(self._temp) + "º")

    def set_temp(self, temp):
        self._temp = temp

# Creación de la aplicación y ventana principal
app = QtWidgets.QApplication([])
window = MainWindow()
window.show()
app.exec()
