import argparse
import cv2.cv2 as cv2
import numpy as np
import glob
import math

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Source img", type=str)
    parser.add_argument("-o", "--output", help="Output img", type=str)
    args = parser.parse_args()

    return args

def main(inputPath,outputPath):
    imagesNameList = glob.glob(inputPath+"*.png")

    imgArray = []
    for imgName in imagesNameList:
        img = cv2.imread(imgName)
        imgArray.append(img)

    output = imgArray[0]

    nbImages = len(imgArray)
    print("Nb Image = {0}".format(nbImages))
    for i in range(len(imgArray[0])) :
        for j in range(len(imgArray[0][0])) :
            for c in range(3) :
                val = j / len(imgArray[0][0]) * (nbImages-1)
                idA = math.floor(val)
                idB = math.floor(val) + 1
                A = imgArray[idA][i][j][c]
                B = imgArray[idB][i][j][c]
                coeff = (val-idA)/(idB-idA)
                output[i][j][c] = (1-coeff)*A+(coeff)*B

    cv2.imwrite(outputPath,output)

if __name__ == '__main__':
    args = parseArguments()
    main(args.input,args.output)