import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import sys
from triangle import triangulate, plot as tplot
from operator import methodcaller

class triangulateMap(object):

    def __init__(self, fileInContours, fileOutContours):
        self.fileInContours = fileInContours
        self.fileOutContours = fileOutContours
        self.contours = None

    '''
    Funciones auxiliares
    '''
    #calcula los centros de los contornos de la imagen
    def centerPointsContours(self, contours):
        maxX = 0
        minX = sys.maxint + 1
        maxY = 0
        minY = sys.maxint + 1
        for i in range(len(contours)):
            if(maxX<contours[i][0]): maxX = contours[i][0]
            if(maxY<contours[i][1]): maxY = contours[i][1]
            if(minX>contours[i][0]): minX = contours[i][0]
            if(minY>contours[i][1]): minY = contours[i][1]

        return (int((maxX+minX)/2), int((maxY+minY)/2))

    #transforma el formato de contornos a un arreglo de tuplas
    def contourToArray(self, contour):
        arr = []
        for i in range(len(contour)):
            if (i == 0):
                auxVer = (contour[i][0][0],contour[i][0][1])
                arr.append(auxVer)
            else:
                arr.append((contour[i][0][0],contour[i][0][1]))
        arr.append(auxVer)
        return arr

    #calcula la media de las areas de los poligonos
    def calcAreaMedium(self, areas):
        medium = 0
        print("Check\n")
        for i in range(len(areas)):
            print(areas[i])
            medium += areas[i]
        print("areas len: ",  len(areas))
        print("medium: ", int(medium/float(len(areas))))
        return int(medium/float(len(areas)))

    #calcula el area de un poligono
    def calcAreaPolygon(self, polygon):
        area = 0
        for i in range(len(polygon)-1):
            area += (polygon[i][0]*polygon[i+1][1] - polygon[i+1][0]*polygon[i][1])
        return abs(area/float(2))

    #calcula el centrolde de un poligono
    #ref: https://en.wikipedia.org/wiki/Centroid#Of_a_polygon
    def calcCentroid(self, polygon, area):
        xSum = 0
        for i in range(len(polygon)-1):
            xSum += int(polygon[i][0] + polygon[i+1][0])*int(polygon[i][0]*polygon[i+1][1] - polygon[i+1][0]*polygon[i][1])
        xSum = abs(xSum/int(6*area))

        ySum = 0
        for j in range(len(polygon)-1):
            ySum += int(polygon[i][1] + polygon[i+1][1])*int(polygon[i][0]*polygon[i+1][1] - polygon[i+1][0]*polygon[i][1])
        ySum = abs(ySum/int(6*area))

        print((xSum, ySum))
        return (xSum, ySum)

    #devuelve la imagen, su tamano y los contornos de la imagen
    def getImContoursAndSize(self, file):
        im = cv.imread(file)
        imgray = 255 - cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        sizeIm = tuple(im.shape[0::1])
        ret, thresh = cv.threshold(imgray, 200, 255, 0)
        im2, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        return im, sizeIm, contours


    '''
    Visualizadores
    '''
    #visualiza las areas de los contornos de una imagen
    def viewArea(self, file):
        im, sizeIm, contours = self.getImContoursAndSize(file)
        medium = 0
        for i in range(len(contours)):
            crop_img_copy = im[0:sizeIm[0], 0:sizeIm[1]]
            cv.drawContours(crop_img_copy, contours, i, (0,255,0), 3)
            auxArr = self.contourToArray(contours[i])
            area = self.calcAreaPolygon(auxArr)
            print(area)
            plt.figure(area)
            plt.imshow(crop_img_copy)
            plt.show()

    #visualiza las areas de los contornos de la imagen de referencia
    def viewAreaContours(self):
        self.viewArea(self.fileInContours)

    #para visualizar los contornos en general
    def viewExtract(self, file, index):
        im, sizeIm, contours = self.getImContoursAndSize(file)
        crop_img_copy = im[0:sizeIm[0], 0:sizeIm[1]]
        cv.drawContours(crop_img_copy, contours, index, (0,255,0), 3)
        print(len(contours))
        plt.imshow(crop_img_copy)
        plt.show()

    #para visualizar los contornos de los vagones por trozos, si el parametro
    #index es -1 mostrara todos los contornos de la imagen, si es cualquier
    #indice mayor que -1, mostrara solo un contorno en especifico
    def viewExtractContours(self, index):
        self.viewExtract(self.fileInContours, index)

    #para visualizar la triangulacion
    def plotTriangles(self, array):
        plt.figure(figsize=(14, 14))
        ax = plt.subplot(111, aspect='equal')
        tplot.plot(ax, **array)
        plt.show()

    '''
    Funciones principales
    '''
    #deprecated
    def getCentroidsHoles(self, contours):
        arrCont = []
        arrArea = []
        arrAux = None
        for i in range(len(contours)):
            arrAux = self.contourToArray(contours[i])
            arrCont.append(arrAux)
            arrArea.append(self.calcAreaPolygon(arrAux))

        medium = self.calcAreaMedium(arrArea)

        auxString = ""
        auxIndex = 0
        auxCoord = None
        for i in range(len(arrCont)):
            if(arrArea[i]>medium):
                auxCoord = self.calcCentroid(arrCont[i], arrArea[i])
                auxString += str(auxIndex) + " " + str(auxCoord[0]) + " " + str(auxCoord[1]) + "\n"
                auxIndex += 1
        return str(auxIndex) + "\n" + auxString

    #Obtiene los centros de los poligonos que no seran triangulados
    def getHoles(self, contours):
        arrAreaCont = []
        arrAux = None
        for i in range(len(contours)):
            arrAux = self.contourToArray(contours[i])
            arrAreaCont.append((self.calcAreaPolygon(arrAux), arrAux))

        #ordenamos para descartar las 2 areas mas grandes
        arrAreaCont.sort(reverse=True)

        auxString = ""
        auxCoord = None
        for i in range(2,len(arrAreaCont)):
            auxCoord = self.centerPointsContours(arrAreaCont[i][1])
            auxString += str(i-2) + " " + str(auxCoord[0]) + " " + str(auxCoord[1]) + "\n"

        return str(len(arrAreaCont)-2) + "\n" + auxString

    #crea un archivo con los vertices indezados y las
    def extractToFile(self, fileIn, fileOut):
        im, sizeIm, contours = self.getImContoursAndSize(fileIn)
        self.contours = contours
        print(sizeIm)
        lenTotal = 0
        fileOut1 = open(fileOut, "w")
        #obtenemos el numero de vertices totales
        for i in range(len(contours)):
            lenTotal += len(contours[i])

        fileOut1.write(str(lenTotal+4)+" 2 0 0\n")
        fileOut1.write("1 0 0\n")
        fileOut1.write("2 "+ str(sizeIm[1]) +" 0\n")
        fileOut1.write("3 "+ str(sizeIm[1]) + " " +  str(sizeIm[0]) +"\n")
        fileOut1.write("4 0 " +  str(sizeIm[0]) +"\n")
        auxEdges = str(lenTotal+4)+" 0\n" +"1 1 2\n" + "2 2 3\n" + "3 3 4\n" + "4 4 1\n"
        auxCount = 5
        auxLast = 1
        for i in range(len(contours)):
            lenCont = len(contours[i])
            for j in range(lenCont):
                fileOut1.write(str(auxCount)+ " " + str(contours[i][j][0][0]) + " " + str(contours[i][j][0][1])+ "\n")
                if(j != lenCont-1):
                    auxEdges = auxEdges+str(auxCount)+" "+str(auxCount)+" "+str(auxCount+1)+"\n"
                    auxCount+=1
            auxEdges += str(auxCount)+" "+str(auxCount)+" "+str(auxLast)+"\n"
            auxCount+=1
            auxLast = auxCount

        #ponemos las aristas
        fileOut1.write(auxEdges)
        #ponemos la posicion de los hoyos
        fileOut1.write(self.getHoles(contours))

        fileOut1.close()

    #funcion que llama a extractToFile con los archivos previamente cargados
    def extractContours(self):
        self.extractToFile(self.fileInContours, self.fileOutContours)

    #generamos el output de la trinagulacion como una tupla que consta de un
    #diccionario y la matriz de adyacencia
    def createOutputTriangles(self, array):
        #generamos un diccionario con los vertices y sus indices (que seran las llaves)
        dictVertex = {}
        for i in range(len(array['vertices'])):
            dictVertex[i] = (array['vertices'][i][0],array['vertices'][i][1])

        #metemos los segmentos originales primero
        adjMatrix = np.zeros((len(array['vertices']), len(array['vertices'])))
        adjMatrix.astype(int)
        for j in range(len(array['segments'])):
            adjMatrix[array['segments'][j][0]][array['segments'][j][1]] = 1

        #metemos las triangulaciones
        for k in range(len(array['triangles'])):
            adjMatrix[array['triangles'][k][0]][array['triangles'][k][1]] = 1
            adjMatrix[array['triangles'][k][1]][array['triangles'][k][2]] = 1
            adjMatrix[array['triangles'][k][2]][array['triangles'][k][0]] = 1

        im, sizeIm, contours = self.getImContoursAndSize(self.fileInContours)
        arrayContours = [self.contourToArray(arr) for arr in contours]

        return (dictVertex, adjMatrix, arrayContours)

    #convierte el archivo de salida en un diccionario para triangular el mapa
    #con la biblioteca triangulate
    def readPoly(self,file_name):
        output = {'vertices': None, 'holes': None, 'segments': None}
        print(file_name)
        file = open(file_name, 'r')
        lines = file.readlines()
        file.close()
        lines = [x.strip('\n').split() for x in lines]

        #vertices
        vertices= []
        N_vertices, dimension, attr, bdry_markers = [int(x) for x in lines[0]]
        # We assume attr = bdrt_markers = 0
        for k in range(N_vertices):
            label, x, y = [items for items in lines[k+1]]
            vertices.append([float(x), float(y)])
        output['vertices']=np.array(vertices)

        #aristas
        segments = []
        N_segments, bdry_markers = [int(x) for x in lines[N_vertices+1]]
        for k in range(N_segments):
            label, pointer_1, pointer_2 = [items for items in lines[N_vertices+k+2]]
            segments.append([int(pointer_1)-1, int(pointer_2)-1])
        output['segments'] = np.array(segments)

        #hoyos
        N_holes = int(lines[N_segments+N_vertices+2][0])
        holes = []
        for k in range(N_holes):
            label, x, y = [items for items in lines[N_segments + N_vertices + 3 + k]]
            holes.append([float(x), float(y)])

        output['holes'] = np.array(holes)
        return output

    #funcion que genera la triangulacion del camino disponible en el vagon
    #regresa una tupla que constara de:
    #en la primera entrada un diccionario con oos vertices
    #en la segunda una matriz de adyacencia
    #en la ultima entrada un arreglo de arreglos con los poligonos que abstraen
    #las paredes, tubos y asientos del vagon
    def triangleFeatures(self, file, plotTriangle):
        fileOut3 = self.readPoly(file)
        cndt = triangulate(fileOut3, 'p')
        if(plotTriangle): self.plotTriangles(cndt)
        return self.createOutputTriangles(cndt)

    #funcion que llama a triangleFeatures con el archivo de salida previamente cargado
    def triangleContours(self, plotTriangle):
        return self.triangleFeatures(self.fileOutContours, plotTriangle)

    #manda a llamar todas las funciones que se requieren para generar los datos
    #si el parametro plotTriangle es True, desplegara la visualizacion de la triangulaciones
    #caso contrario, solo generara la tupla y el archivo resultante
    def generateTriangularMesh(self, plotTriangle):
        self.extractContours()
        data = self.triangleContours(plotTriangle)
        return data


#Modo de uso
ext = triangulateMap('./images/car.png', './output/car_features.poly')
aux = ext.generateTriangularMesh(False)
print(aux)
