###
#Nombre del archivo: app.py
#Autor: Elena Bazo, Editado por David Serrano Henares
#Repositorio GitHub: https://github.com/tigre437/interfazv4
#Funcion: Este archivo contiene la logica de deteccion del analisis final.
###

import os
import cv2
import numpy as np
import test_color_values_DRINCZ
import pandas as pd
import matplotlib.pyplot as plt  

def detect_circles(experiment, threshold, threshold_b, radio_min, radio_max):
    # experiment="240416_144741_A_UGR240415 B_UGR240415_1_10"
    # threshold=205
    threshold_b = 0.99

    images = os.path.join(experiment, 'imagenes')

    list_images = os.listdir(images)
    list_images.sort()

    path = os.path.join(images, list_images[0])
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

    # Establezco el threshold para crear la imagen binaria (aquí iría la barra para variarlo)
    _, binary = cv2.threshold(grey, threshold, 255, cv2.THRESH_BINARY)

    # cv2.imshow('binary', binary)
    # cv2.waitKey(0)

    # Encuentro los contornos de la imagen
    contours, h = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    circle_list = []

    # Selecciono contornos cerrados de más de 5 lados, con radio de 15 a 20 píxeles 
    # cy > 50 es para obviar la parte de arriba de la imagen (antes de rotarla a veces interpretaba la marca de agua como contorno)

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, .03 * cv2.arcLength(cnt, True), True)
        if len(approx) >= 5:
            if cv2.isContourConvex(approx):
                (cx, cy), radius = cv2.minEnclosingCircle(cnt)
                # selecciono el rango de radios de los contornos que quiero determinar
                if radio_min <= radius <= radio_max: # pongo esto para que no considere el bloque
                    circle_list.append([cx, cy, radius])
                    cv2.circle(img, (int(cx), int(cy)), int(radius), (0, 255, 0), 2)
                    # cv2.circle(img, (int(cx), int(cy)), 1, (0, 0, 255), 3)

    circles = np.asarray(circle_list)

    circles = circles[circles[:, 1].argsort()] 
    circles_pcr1 = circles[0:96, :]
    circles_pcr2 = circles[96:, :]

    # Aquí ordeno los círculos detectados en función de su posición en la pcr, tengo dos listas de círculos para las dos pcr

    circles_order_pcr1 = np.zeros(shape=(96, 3))
    circles_order_pcr2 = np.zeros(shape=(96, 3))
                    
    j = 0
    for i in range(8):
        circles_aux1 = circles_pcr1[j:j+12, :]
        circles_aux1 = circles_aux1[circles_aux1[:, 0].argsort()][::-1] # Orden invertido
        
        circles_order_pcr1[j:j+12, :] = circles_aux1
        
        circles_aux2 = circles_pcr2[j:j+12, :]
        circles_aux2 = circles_aux2[circles_aux2[:, 0].argsort()][::-1] # Orden invertido
        
        circles_order_pcr2[j:j+12, :] = circles_aux2
        j += 12

    circles_order_pcr1 = circles_order_pcr1[::-1, :]
    circles_order_pcr2 = circles_order_pcr2[::-1, :]

    # Represento la imagen (a color) junto con los círculos detectados y su orden
    # Esto en teoría debería verse a medida que cambiemos el threshold, para ver que elegimos uno donde se detectan bien todos los círculos
    idx = 1
    for row in circles_order_pcr1:
        cv2.putText(img, str(idx), (int(row[0]), int(row[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
        idx += 1

    idx = 1
    for row in circles_order_pcr2:
        cv2.putText(img, str(idx), (int(row[0]), int(row[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
        idx += 1

    cv2.destroyAllWindows()

    circles_order = np.vstack((circles_order_pcr1, circles_order_pcr2))

    # OBTENCION DE LA ESCALA DE GRISES DE LOS POZOS A PARTIR DE LAS IMAGENES EN LA CARPETA
    matriz_colores_A, matriz_colores_B = test_color_values_DRINCZ.get_color_values_from_images(images, circles_order_pcr1, circles_order_pcr2)

    matriz_colores_A = np.delete(matriz_colores_A, 0, axis=1)
    matriz_colores_B = np.delete(matriz_colores_B, 0, axis=1)

    path2 = os.path.join(experiment, 'temperaturas.csv')
    time_series = pd.read_csv(path2)

    t_set = time_series.t_set
    t_ext = time_series.t_ext

    t_ext = t_ext[t_ext < -1]

    circles_index = np.array(range(1, 97))
    circles_index = circles_index.reshape([8, 12])
    circles_index = pd.DataFrame(circles_index, columns=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'], index=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])

    color_difference_A = np.diff(matriz_colores_A, axis=1)
    color_difference_B = np.diff(matriz_colores_B, axis=1)

    color_difference_A_norm = np.zeros([color_difference_A.shape[0], color_difference_A.shape[1]])
    color_difference_B_norm = np.zeros([color_difference_A.shape[0], color_difference_A.shape[1]])

    for i in range(96):
        max_A = max(color_difference_A[i, :])
        max_B = max(color_difference_B[i, :])
        if max_A != 0:
            color_difference_A_norm[i, :] = color_difference_A[i, :] / max_A
        if max_B != 0:
            color_difference_B_norm[i, :] = color_difference_B[i, :] / max_B

    color_difference = np.vstack((color_difference_A_norm, color_difference_B_norm))

    # Tengo que contar los saltos de color en cada instante de tiempo o temperatura y meterlo en una variable que será NF
    threshold_b = 0.99
    Vdrop = 0.2E-3  # en L
    # PLACA A
    N0 = 96
    NFrozen_A = np.zeros([len(t_ext)-2], dtype=int) # estoy quitando el primer cambio de color porque hay un salto grande
    temp_aux_A = np.zeros(N0)

    t_wells = t_ext + (-0.0324 * t_ext) + 0.508
    # t_wells = t_ext

    error_t_wells = np.sqrt((0.0031 * t_ext) ** 2 + (0.9676 * (0.3 + 0.005 * abs(t_ext))) ** 2 + 0.054 ** 2)

    check_color_difference_A = np.zeros([N0, len(t_ext) - 2])
    mask = np.ones(96)
    color_difference_wells_A = np.zeros(N0)

    for j in range(len(t_ext) - 2):
        print(check_color_difference_A[:, j])
        check_color_difference_A[:, j] = np.logical_and(abs(color_difference_A_norm[:, j]) > threshold_b, mask == 1)
        NFrozen_A[j] = np.sum(check_color_difference_A[:, j]) + NFrozen_A[j - 1]
        mask[check_color_difference_A[:, j] == 1] = 0
        temp_aux_A[check_color_difference_A[:, j] == 1] = t_wells.iloc[j]

    N0_A = NFrozen_A[-1]
    frozen_fraction_A = NFrozen_A / N0_A

    Dilution_factor = 1
    INP_conc_drop_A = -np.log(1 - frozen_fraction_A) * Dilution_factor / Vdrop

    plt.figure(figsize=(8, 6))
    plt.rcParams['font.size'] = 16
    plt.plot(t_wells[2:], frozen_fraction_A, marker='.', color='blue') 

    plt.grid()
    plt.xlabel('t$_{wells}$ (ºC)')
    plt.ylabel('Frozen fraction')
    plt.savefig(experiment + '/Frozen fraction A.jpg')

    # PLACA B (ABAJO)

    NFrozen_B = np.zeros([len(t_ext) - 2], dtype=int)
    temp_aux_B = np.zeros(N0)

    check_color_difference_B = np.zeros([N0, len(t_ext) - 2])
    mask = np.ones(96)
    color_difference_wells_B = np.zeros(N0)
    for j in range(len(t_ext) - 2):
        check_color_difference_B[:, j] = np.logical_and(abs(color_difference_B_norm[:, j]) > threshold_b, mask == 1)
        NFrozen_B[j] = np.sum(check_color_difference_B[:, j]) + NFrozen_B[j - 1]
        mask[check_color_difference_B[:, j] == 1] = 0
        temp_aux_B[check_color_difference_B[:, j] == 1] = t_wells.iloc[j]

    N0_B = NFrozen_B[-1]
    frozen_fraction_B = NFrozen_B / N0_B

    INP_conc_drop_B = -np.log(1 - frozen_fraction_B) * Dilution_factor / Vdrop   

    plt.figure(figsize=(8, 6))
    plt.rcParams['font.size'] = 16
    plt.plot(t_wells[2:], frozen_fraction_B, marker='.', color='blue') 

    plt.grid()
    plt.xlabel('t$_{wells}$ (ºC)')
    plt.ylabel('Frozen fraction')
    plt.savefig(experiment + '/Frozen fraction B.jpg')

    return frozen_fraction_A, frozen_fraction_B, t_wells[2:]
