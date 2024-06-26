###
#Nombre del archivo: app.py
#Autor: David Serrano Henares
#Repositorio GitHub: https://github.com/tigre437/interfazv4
#Funcion: Este archivo contiene el manejo de la cámara e imagenes.
###

import cv2
import os
import datetime
from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np
import csv

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, clase):
        super().__init__()
        self.cap = None
        self._run_flag = True
        self.app = clase

    def run(self):
        # Captura desde la cámara web
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        while self._run_flag:
            ret, cv_img = self.cap.read()
            if ret:
                # Emitir la señal con el fotograma capturado
                self.change_pixmap_signal.emit(cv_img)
        # Apagar el sistema de captura
        self.cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

    def settings(self):
        # Abrir la configuración de la cámara
        self.cap.set(cv2.CAP_PROP_SETTINGS, 1)

    def capturar_foto(self):
        """Captura una foto y la devuelve"""
        ret, cv_img = self.cap.read()
        height, width, _ = cv_img.shape
        print(height, width)
        return cv_img

    def save(self, ruta_experimento, PlacaA, PlacaB, doble, temperatura):
        # Obtener la fecha y hora actual
        now = datetime.datetime.now()
        # Formatear la fecha y hora en el formato deseado, por ejemplo: HHMMSS
        timestamp = now.strftime("%H%M%S")
        # Capturar una foto
        cv_img = self.capturar_foto()
        print("FOTO")
        if cv_img is not None:
            if not doble:
                print("not doble")
                height, width, _ = cv_img.shape
                if PlacaA:
                    print("A")
                    
                    cv_img = cv_img[:, :width // 2]  # Recortar la mitad izquierda de la imagen
                    # Añadir texto rojo abajo a la izquierda con la temperatura de la imagen
                    cv2.putText(cv_img, str(round(temperatura, 2)), (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
                    try:
                        cv2.imwrite(os.path.join(f"{ruta_experimento[0]}/imagenes", f"{timestamp}.jpg"), cv_img)
                    except Exception as e:
                        print(f"Error al guardar la imagen: {e}")
                    # Abrir el archivo CSV y escribir el timestamp y la temperatura
                    with open(os.path.join(f"{ruta_experimento[0]}", f"imagenes.csv"), 'a', newline='') as csv_file:
                        escritor_csv = csv.writer(csv_file)
                        escritor_csv.writerow([timestamp, temperatura])
                    

                if PlacaB:
                    print("B")
                    
                    cv_img_B = cv_img[:, width // 2:]  # Recortar la mitad derecha de la imagen
                    # Añadir texto rojo abajo a la derecha con la temperatura de la imagen
                    new_width = width // 2
                    cv2.putText(cv_img_B, str(round(temperatura, 2)), (new_width - 10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
                    try:
                        cv2.imwrite(os.path.join(f"{ruta_experimento[1]}/imagenes", f"{timestamp}.jpg"), cv_img_B)
                    except Exception as e:
                        print(f"Error al guardar la imagen: {e}")
                    # Abrir el archivo CSV y escribir el timestamp y la temperatura
                    with open(os.path.join(f"{ruta_experimento[1]}", f"imagenes.csv"), 'a', newline='') as csv_file:
                        escritor_csv = csv.writer(csv_file)
                        escritor_csv.writerow([timestamp, temperatura])
                    
            else:
                try:
                    cv2.putText(cv_img, str(round(temperatura, 2)), (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
                    cv2.imwrite(os.path.join(f"{ruta_experimento}/imagenes", f"{timestamp}.jpg"), cv_img)
                except Exception as e:
                    print(f"Error al guardar la imagen: {e}")
                # Abrir el archivo CSV y escribir el timestamp y la temperatura
                with open(os.path.join(f"{ruta_experimento}", f"imagenes.csv"), 'a', newline='') as csv_file:
                    escritor_csv = csv.writer(csv_file)
                    escritor_csv.writerow([timestamp, temperatura])
        else:  # Si la imagen no se pudo capturar
            print("Error al capturar la imagen. No se guardará.")

    def set_camera_index(self, index):
        """Establece el índice del dispositivo de captura"""
        self.camera_index = index
