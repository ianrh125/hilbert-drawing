# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 10:35:41 2019

@author: ianrh
"""

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import math

imageLayers = []

"""
ScaleUp affects the scale of the hilbert curve itself, effectively reducing the number of iterations by this value
imageScale determines how the image will be scaled before the curve is drawn.
minCurve detemines the minimum density of the curve at any given point
"""
ScaleUp = 0
imageScale = 1
minCurve = 16

#Function for creating the list of points for the curve to follow
def ListPoints(y, x, level, direction, bonus):
    
    # evaluating whether the specific section of the curve is detailed enough to match the shading in the relevant section of image
    if(level <= ScaleUp or imageLayers[level][y][x]+bonus < 2**(level+9+ScaleUp)):
        return [[y * 2**level, x * 2**level, 2**level]]
    else:
        
        #creating four points to increase the section of the curve to the next iteration
        output = []
        addBonus = 2**(level+5 + ScaleUp)
        if(direction == 0):
            output.extend(ListPoints(y*2, x*2, level-1, 1, bonus/8))
            output.extend(ListPoints(y*2+1, x*2, level-1, 0, bonus/8+addBonus))
            output.extend(ListPoints(y*2+1, x*2+1, level-1, 0, bonus/8+addBonus*2))
            output.extend(ListPoints(y*2, x*2+1, level-1, 3, bonus/8+addBonus*3))
        elif(direction == 1):
            output.extend(ListPoints(y*2, x*2, level-1, 0, bonus/8+0))
            output.extend(ListPoints(y*2, x*2+1, level-1, 1, bonus/8+addBonus))
            output.extend(ListPoints(y*2+1, x*2+1, level-1, 1, bonus/8+addBonus*2))
            output.extend(ListPoints(y*2+1, x*2, level-1, 2, bonus/8+addBonus*3))
        elif(direction == 2):
            output.extend(ListPoints(y*2+1, x*2+1, level-1, 3, bonus/8+0))
            output.extend(ListPoints(y*2, x*2+1, level-1, 2, bonus/8+addBonus))
            output.extend(ListPoints(y*2, x*2, level-1, 2, bonus/8+addBonus*2))
            output.extend(ListPoints(y*2+1, x*2, level-1, 1, bonus/8+addBonus*3))
        elif(direction == 3):
            output.extend(ListPoints(y*2+1, x*2+1, level-1, 2, 0))
            output.extend(ListPoints(y*2+1, x*2, level-1, 3, bonus/8+addBonus))
            output.extend(ListPoints(y*2, x*2, level-1, 3, bonus/8+addBonus*2))
            output.extend(ListPoints(y*2, x*2+1, level-1, 0, bonus/8+addBonus*3))
        return output
            
im = Image.open("C:/Image_filepath")
np_im = np.array(im)
print("input size:",np_im.shape)
print("square size:",max(np_im.shape[0], np_im.shape[1]))
size = 2 ** math.ceil(math.log(np_im.shape[0]*imageScale,2))
grayscale = np.zeros((size, size))

# converting the image to grayscale
for i in range(size):
    for j in range(size):
        
        # various systems for handling images with grayscale, RBG, or RBG and opacity data
        try:
            referencePixel = np_im[int(i/imageScale)][int(j/imageScale)]
            if(len(np_im.shape) == 3):
                if(len(referencePixel) == 4):
                    grayscale[i][j] = (255 - int(math.sqrt(referencePixel[0]**2*0.21 + referencePixel[1]**2*0.72 + referencePixel[2]**2*0.07))) * referencePixel[3] / 255
                    if(i == 0 and j == 0):
                        print("foo")
                else:
                    grayscale[i][j] = 255 - int(math.sqrt(referencePixel[0]**2*0.21 + referencePixel[1]**2*0.72 + referencePixel[2]**2*0.07))
                    if(i == 0 and j == 0):
                        print("bar")
            else:
                grayscale[i][j] = 255 - referencePixel
                if(i == 0 and j == 0):
                    print("boo")
        except:
            grayscale[i][j] = 0
            if(i == 0 and j == 0):
                print("far")
        grayscale[i][j] = max(grayscale[i][j],minCurve)
            
# scaling the grayscale to the power of 2 closest to the imageScale parameter
print("final size:",grayscale.shape)
imageLayers.append(grayscale)

# creating copies of the original image, each scaled down 50% from the last
while(len(imageLayers[-1]) > 1):
    layerSize = int(len(imageLayers[-1])/2)
    newLayer = np.zeros((layerSize,layerSize))
    for i in range(layerSize):
        for j in range(layerSize):
            newLayer[i][j] = imageLayers[-1][i*2][j*2]+imageLayers[-1][i*2+1][j*2]+imageLayers[-1][i*2][j*2+1]+imageLayers[-1][i*2+1][j*2+1]
    imageLayers.append(newLayer)
    
# running function to generate a list of points for the curve to follow
pointsList = ListPoints(0, 0, len(imageLayers)-1,0,0)
xPositions = []
yPositions = []
xLevels = []
yLevels = []
for i in pointsList:
    yPositions.append(i[0]+i[2]/2)
    xPositions.append(i[1]+i[2]/2)
    yLevels.append(i[2])
    xLevels.append(i[2])
originalX = xPositions[:]
originalY = yPositions[:]
# tweaking posion values of points to snap to 90 degree angles with points of higher iteration levels
for a in range(-1,8):
    for i in range(len(pointsList)-1):
        if(xPositions[i] != xPositions[i+1] and yPositions[i] != yPositions[i+1]):
            if(abs(originalX[i]-originalX[i+1]) > abs(originalY[i]-originalY[i+1])):
                if(yLevels[i] > yLevels[i+1]):
                    yPositions[i] = yPositions[i+1]
                    yLevels[i] = yLevels[i+1]
                elif(yLevels[i] < yLevels[i+1]):
                    yPositions[i+1] = yPositions[i]
                    yLevels[i+1] = yLevels[i]
                else:
                    print("Same Levels Y")
            elif(abs(originalX[i]-originalX[i+1]) < abs(originalY[i]-originalY[i+1])):
                if(xLevels[i] > xLevels[i+1]):
                    xPositions[i] = xPositions[i+1]
                    xLevels[i] = xLevels[i+1]
                elif(xLevels[i] < xLevels[i+1]):
                    xPositions[i+1] = xPositions[i]
                    xLevels[i+1] = xLevels[i]
                else:
                    print("Same Levels X")
            else:
                print("Diagonal")

duplicates = 0
# scanning the list for items that don't line up. Used for finding error in previous pass
for i in range(len(pointsList) - 1):
    if(xPositions[i] != xPositions[i+1] and yPositions[i] != yPositions[i+1]):
        duplicates += 1
        print("X1:", xPositions[i])
        print("Y1:", yPositions[i])
        print("X2:", xPositions[i+1])
        print("Y2:", yPositions[i+1])
        if(duplicates < 5):
            plt.figure(figsize=(5,5))
            plt.plot(xPositions[(i-10):(i+10)], yPositions[(i-10):(i+10)], marker=',', markersize=2, mfc='black')
print("duplicates:", duplicates)

print("Size:", size)

# reducing the position values to integers to work with rendering 
for i in range(len(xPositions)):
    xPositions[i] = int(xPositions[i])
    yPositions[i] = int(yPositions[i])    

if(duplicates == 0):
    printArray = np.zeros((size,size))
    
    xDraw = xPositions[0]
    yDraw = yPositions[0]
    # drawing the hilbert curve, taking 1 pixel steps towards the next point and marking the corresponding pixel black
    for i in range(len(xPositions)):
        while(xDraw != xPositions[i] or yDraw != yPositions[i]):
            printArray[int(yDraw)][int(xDraw)] = 1
            if(xDraw == xPositions[i]):
                yDraw -= (yDraw-yPositions[i])/abs(yDraw-yPositions[i])
            elif(yDraw == yPositions[i]):
                xDraw -= (xDraw-xPositions[i])/abs(xDraw-xPositions[i])
    # plotting the array to an image
    dpi = 80
    width = size/dpi
    height = size/dpi
    fig = plt.figure(figsize=(width, height), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1], frameon=False, aspect=1)
    ax.imshow(printArray, cmap='Greys', interpolation = 'none')
else:
    plt.figure(figsize=(10,10))
    plt.plot(xPositions, yPositions, marker=',', markersize=2, mfc='black')