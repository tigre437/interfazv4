# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:14:16 2024

@author: Elena Bazo
"""

import os
import cv2
import numpy as np

experiment = '240416_144741_A_UGR240415 B_UGR240415_1_10'

images = os.path.join(experiment, 'images')

list_images = os.listdir(images)
list_images.sort()

path = os.path.join(images, list_images[0])
img = cv2.imread(path, cv2.IMREAD_COLOR)
img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

# print(grey.mean())
# print(np.median(grey))
# print(grey.std())
# cv2.imshow('grey', grey)
# cv2.waitKey(0)

#Establezco el threshold para crear la imagen binaria (aquí iría la barra para variarlo)
threshold = 205
_, binary = cv2.threshold(grey, threshold, 255, cv2.THRESH_BINARY)

cv2.imshow('binary', binary)
cv2.waitKey(0)

#Encuentro los contornos de la imagen
contours,h = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

circle_list = []

#Selecciono contornos cerrados de más de 5 lados, con radio de 15 a 20 píxeles 
# cy>50 es para obviar la parte de arriba de la imagen (antes de rotarla a veces interpretaba la marca de agua como contorno)

for cnt in contours:
    approx = cv2.approxPolyDP(cnt, .03 * cv2.arcLength(cnt, True), True)
    # cv2.drawContours(img, cnt, -1, (0, 0, 255), 2, cv2.LINE_AA)
    # cv2.imshow('contour', img)
    # cv2.waitKey(0)    
    #print(len(approx))
    if len(approx)>=5:
        if cv2.isContourConvex(approx):
            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
            #selecciono el rango de radios de los contornos que quiero determinar
            if radius >=15 and radius <= 20 and cy > 50: #pongo esto para que no considere el bloque
                circle_list.append([cx, cy, radius])
                cv2.circle(img, (int(cx), int(cy)), int(radius), (0, 255, 0), 2)
                # cv2.circle(img, (int(cx), int(cy)), 1, (0, 0, 255), 3)

circles = np.asarray(circle_list)

circles = circles[circles[:,1].argsort()] 
circles_pcr1 = circles[0:96,:]
circles_pcr2 = circles[96:,:]

# Aquí ordeno los círculos detectados en función de su posición en la pcr, tengo dos listas de círculos para las dos pcr

circles_order_pcr1=np.zeros(shape=(96, 3))	
circles_order_pcr2=np.zeros(shape=(96, 3))
                
j=0
for i in range(8):
    circles_aux1 = circles_pcr1[j:j+12,:]
    circles_aux1=circles_aux1[circles_aux1[:,0].argsort()]
    
    circles_order_pcr1[j:j+12,:]=circles_aux1
    
    circles_aux2 = circles_pcr2[j:j+12,:]
    circles_aux2=circles_aux2[circles_aux2[:,0].argsort()]
    
    circles_order_pcr2[j:j+12,:]=circles_aux2
    j+=12

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

cv2.imshow(f'circles', img)
cv2.waitKey(0) 

cv2.destroyAllWindows()

circles_order = np.vstack((circles_order_pcr1,circles_order_pcr2))