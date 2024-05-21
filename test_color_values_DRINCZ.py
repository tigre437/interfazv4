import cv2
import os
import numpy as np


def get_color_values_from_images(folder, circles_A,circles_B):
    images = []
    color_values_A = []
    color_values_B = []
    grey_mean_circles_A =[]
    grey_mean_circles_B =[]
    grey_std_circles_A=[]
    grey_std_circles_B=[]

    
    for filename in sorted(os.listdir(folder)):
        img = cv2.imread(os.path.join(folder,filename), cv2.IMREAD_COLOR)
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        # grey = img[:,:,0]
        if grey is not None:
            images.append(grey)
    grey_mean = np.mean(images, axis = 0)
    grey_std = np.std(images, axis = 0)
        
    for i in range(0,len(circles_A)):
        grey_mean_circles_A_i = np.mean(grey_mean[round(circles_A[i,1])-round(0.6*circles_A[i,2]):round(circles_A[i,1])+round(0.6*circles_A[i,2]),round(circles_A[i,0])-round(0.6*circles_A[i,2]):round(circles_A[i,0])+round(0.6*circles_A[i,2])])
        grey_mean_circles_B_i = np.mean(grey_mean[round(circles_B[i,1])-round(0.6*circles_B[i,2]):round(circles_B[i,1])+round(0.6*circles_B[i,2]),round(circles_B[i,0])-round(0.6*circles_B[i,2]):round(circles_B[i,0])+round(0.6*circles_B[i,2])])
        grey_std_circles_A_i = np.mean(grey_std[round(circles_A[i,1])-round(0.6*circles_A[i,2]):round(circles_A[i,1])+round(0.6*circles_A[i,2]),round(circles_A[i,0])-round(0.6*circles_A[i,2]):round(circles_A[i,0])+round(0.6*circles_A[i,2])])
        grey_std_circles_B_i = np.mean(grey_std[round(circles_B[i,1])-round(0.6*circles_B[i,2]):round(circles_B[i,1])+round(0.6*circles_B[i,2]),round(circles_B[i,0])-round(0.6*circles_B[i,2]):round(circles_B[i,0])+round(0.6*circles_B[i,2])])
        
        grey_mean_circles_A.append(grey_mean_circles_A_i)
        grey_mean_circles_B.append(grey_mean_circles_B_i)
        grey_std_circles_A.append(grey_std_circles_A_i)
        grey_std_circles_B.append(grey_std_circles_B_i)
        
    for j in range(0,len(images)):
        for i in range(0,len(circles_A)):
            color_values_i_A=(np.mean(images[j][round(circles_A[i,1])-round(0.6*circles_A[i,2]):round(circles_A[i,1])+round(0.6*circles_A[i,2]),round(circles_A[i,0])-round(0.6*circles_A[i,2]):round(circles_A[i,0])+round(0.6*circles_A[i,2])]) - grey_mean_circles_A[i])/grey_std_circles_A[i]     
            color_values_i_B=(np.mean(images[j][round(circles_B[i,1])-round(0.6*circles_B[i,2]):round(circles_B[i,1])+round(0.6*circles_B[i,2]),round(circles_B[i,0])-round(0.6*circles_B[i,2]):round(circles_B[i,0])+round(0.6*circles_B[i,2])]) - grey_mean_circles_B[i])/grey_std_circles_B[i]

            color_values_A.append(color_values_i_A)
            color_values_B.append(color_values_i_B)

                
    color_values1_A = np.array(color_values_A)
    matriz_colores_A = color_values1_A.reshape(len(circles_A),len(images),order='F')    #return matriz_colores
    color_values1_B = np.array(color_values_B)
    matriz_colores_B = color_values1_B.reshape(len(circles_B),len(images),order='F')    #return matriz_colores
    return matriz_colores_A,matriz_colores_B

