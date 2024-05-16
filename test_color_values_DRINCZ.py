import cv2
import os
import numpy as np

def get_color_values_from_images(folder, circles_A, circles_B):
    # Inicialización de listas para almacenar datos
    images = []  # Almacena las imágenes en escala de grises
    color_values_A = []  # Almacena los valores de color normalizados para los círculos de interés A
    color_values_B = []  # Almacena los valores de color normalizados para los círculos de interés B
    grey_mean_circles_A = []  # Almacena los valores medios de gris para las regiones circulares de interés A
    grey_mean_circles_B = []  # Almacena los valores medios de gris para las regiones circulares de interés B
    grey_std_circles_A = []  # Almacena las desviaciones estándar de gris para las regiones circulares de interés A
    grey_std_circles_B = []  # Almacena las desviaciones estándar de gris para las regiones circulares de interés B
    
    # Iterar sobre las imágenes en el directorio especificado
    for filename in sorted(os.listdir(folder)):
        # Leer la imagen en color y convertirla a escala de grises
        img = cv2.imread(os.path.join(folder, filename), cv2.IMREAD_COLOR)
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Agregar la imagen a la lista
        if grey is not None:
            images.append(grey)
    
    # Calcular los valores medios de gris y las desviaciones estándar de gris para todas las imágenes
    grey_mean = np.mean(images, axis=0)
    grey_std = np.std(images, axis=0)
    
    # Iterar sobre los círculos de interés
    for i in range(0, len(circles_A)):
        # Calcular los valores medios de gris y las desviaciones estándar de gris para las regiones circulares de interés A y B
        grey_mean_circles_A_i = np.mean(grey_mean[round(circles_A[i, 1]) - round(0.6 * circles_A[i, 2]):round(circles_A[i, 1]) + round(0.6 * circles_A[i, 2]), round(circles_A[i, 0]) - round(0.6 * circles_A[i, 2]):round(circles_A[i, 0]) + round(0.6 * circles_A[i, 2])])
        grey_mean_circles_B_i = np.mean(grey_mean[round(circles_B[i, 1]) - round(0.6 * circles_B[i, 2]):round(circles_B[i, 1]) + round(0.6 * circles_B[i, 2]), round(circles_B[i, 0]) - round(0.6 * circles_B[i, 2]):round(circles_B[i, 0]) + round(0.6 * circles_B[i, 2])])
        grey_std_circles_A_i = np.mean(grey_std[round(circles_A[i, 1]) - round(0.6 * circles_A[i, 2]):round(circles_A[i, 1]) + round(0.6 * circles_A[i, 2]), round(circles_A[i, 0]) - round(0.6 * circles_A[i, 2]):round(circles_A[i, 0]) + round(0.6 * circles_A[i, 2])])
        grey_std_circles_B_i = np.mean(grey_std[round(circles_B[i, 1]) - round(0.6 * circles_B[i, 2]):round(circles_B[i, 1]) + round(0.6 * circles_B[i, 2]), round(circles_B[i, 0]) - round(0.6 * circles_B[i, 2]):round(circles_B[i, 0]) + round(0.6 * circles_B[i, 2])])
        
        # Agregar los valores calculados a las listas correspondientes
        grey_mean_circles_A.append(grey_mean_circles_A_i)
        grey_mean_circles_B.append(grey_mean_circles_B_i)
        grey_std_circles_A.append(grey_std_circles_A_i)
        grey_std_circles_B.append(grey_std_circles_B_i)
        
    # Iterar sobre las imágenes y los círculos de interés
    for j in range(0, len(images)):
        for i in range(0, len(circles_A)):
            # Extraer los valores de píxeles de las regiones circulares de interés A y B en cada imagen
            roi_A = images[j][round(circles_A[i, 1]) - round(0.6 * circles_A[i, 2]):round(circles_A[i, 1]) + round(0.6 * circles_A[i, 2]), round(circles_A[i, 0]) - round(0.6 * circles_A[i, 2]):round(circles_A[i, 0]) + round(0.6 * circles_A[i, 2])]
            roi_B = images[j][round(circles_B[i, 1]) - round(0.6 * circles_B[i, 2]):round(circles_B[i, 1]) + round(0.6 * circles_B[i, 2]), round(circles_B[i, 0]) - round(0.6 * circles_B[i, 2]):round(circles_B[i, 0]) + round(0.6 * circles_B[i, 2])]
            
           # print("ROI A:", roi_A.shape)
           # print("ROI B:", roi_B.shape)
            
            # Calcular los valores medios de gris y las desviaciones estándar de gris para las regiones circulares de interés A y B
            grey_mean_circles_A_i = np.mean(roi_A)
            grey_mean_circles_B_i = np.mean(roi_B)
            grey_std_circles_A_i = np.std(roi_A)
            grey_std_circles_B_i = np.std(roi_B)
            
           # print("Grey mean A:", grey_mean_circles_A_i)
           # print("Grey mean B:", grey_mean_circles_B_i)
           # print("Grey std A:", grey_std_circles_A_i)
           # print("Grey std B:", grey_std_circles_B_i)
            
            # Calcular los valores de color normalizados para las regiones circulares de interés A y B
            color_values_i_A = (np.mean(roi_A) - grey_mean_circles_A_i) / grey_std_circles_A_i
            color_values_i_B = (np.mean(roi_B) - grey_mean_circles_B_i) / grey_std_circles_B_i

           # print("Color values A:", color_values_i_A)
           # print("Color values B:", color_values_i_B)

            # Agregar los valores normalizados a las listas correspondientes
            color_values_A.append(color_values_i_A)
            color_values_B.append(color_values_i_B)

            


    # Reorganizar los valores normalizados en matrices 2D para cada conjunto de círculos de interés
    color_values1_A = np.array(color_values_A)
    matriz_colores_A = color_values1_A.reshape(len(circles_A), len(images), order='F')
    color_values1_B = np.array(color_values_B)
    matriz_colores_B = color_values1_B.reshape(len(circles_B), len(images), order='F')
    

    # Devolver las matrices de valores de color normalizados para los círculos de interés A y B
    return matriz_colores_A, matriz_colores_B
