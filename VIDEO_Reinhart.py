import argparse
import os
import glob
import cv2.cv2 as cv2
import math
import numpy as np
import colour_transfer

def FloatToUint8(image):
    image= np.clip(image, 0, 255)
    image=image.astype(np.uint8)
    return image

def computeColor(src, mean_src, stdDev_src, mean_ref, stdDev_ref):
    val = src - mean_src
    coeff = stdDev_ref/stdDev_src
    result = coeff*val + mean_ref
    return result

# https://www.pyimagesearch.com/2015/10/05/opencv-gamma-correction/
def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(image, table)

# https://stackoverflow.com/questions/32696138/converting-from-rgb-to-l%CE%B1%CE%B2-color-spaces-and-converting-it-back-to-rgb-using-open
def BGRtoLalphabeta(img_in):
    split_src = cv2.split(img_in)
    L = 0.3811*split_src[2]+0.5783*split_src[1]+0.0402*split_src[0]
    M = 0.1967*split_src[2]+0.7244*split_src[1]+0.0782*split_src[0]
    S = 0.0241*split_src[2]+0.1288*split_src[1]+0.8444*split_src[0]

    L = np.where(L == 0.0, 1.0, L)
    M = np.where(M == 0.0, 1.0, M)
    S = np.where(S == 0.0, 1.0, S)

    _L = (1.0 / math.sqrt(3.0)) * ((1.0000 * np.log10(L)) + (1.0000 * np.log10(M)) + (1.0000 * np.log10(S)))
    Alph = (1.0 / math.sqrt(6.0)) * ((1.0000 * np.log10(L)) + (1.0000 * np.log10(M)) + (-2.0000 * np.log10(S)))
    Beta = (1.0 / math.sqrt(2.0)) * ((1.0000 * np.log10(L)) + (-1.0000 * np.log10(M)) + (-0.0000 * np.log10(S)))

    img_out = cv2.merge((_L, Alph, Beta))
    return img_out

def LalphabetatoBGR(img_in):
    split_src = cv2.split(img_in)
    _L = split_src[0]*1.7321
    Alph = split_src[1]*2.4495
    Beta = split_src[2]*1.4142

    L = (0.33333*_L) + (0.16667 * Alph) + (0.50000 * Beta)
    M = (0.33333 * _L) + (0.16667 * Alph) + (-0.50000 * Beta)
    S = (0.33333 * _L) + (-0.33333 * Alph) + (0.00000 * Beta)

    L = np.power(10, L)
    M = np.power(10, M)
    S = np.power(10, S)
    
    L = np.where(L == 1.0, 0.0, L)
    M = np.where(M == 1.0, 0.0, M)
    S = np.where(S == 1.0, 0.0, S)
    
    R = 4.36226*L-3.58076*M+0.1193*S
    G = -1.2186*L+2.3809*M-0.1624*S
    B = 0.0497*L-0.2439*M+1.2045*S

    img_out = cv2.merge((B, G, R))
    return img_out

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input video", type=str)
    parser.add_argument("-o", "--output", help="Output vido", type=str)
    parser.add_argument("-p", "--palette", help="Palette", type=str)
    args = parser.parse_args()

    return args

def interpolePalette(palette,coeff):
    val = coeff * (len(palette)-1)
    idxA = math.floor(val)
    idxB = idxA + 1
    imgA = palette[idxA]
    imgB = palette[idxB]
    inter = (val-idxA)/(idxB-idxA)
    return FloatToUint8((1-inter)*imgA+(inter)*imgB)

def transfert(src,ref,gamma=1.0):
    img_src = adjust_gamma(src,gamma)
    img_src = BGRtoLalphabeta(img_src)

    img_ref = adjust_gamma(ref,gamma)
    img_ref = BGRtoLalphabeta(img_ref)

    mean_src, stddev_src = cv2.meanStdDev(img_src)
    mean_ref, stddev_ref = cv2.meanStdDev(img_ref)
    split_src = cv2.split(img_src)
    img_out = cv2.merge((computeColor(split_src[0], mean_src[0], stddev_src[0], mean_ref[0], stddev_ref[0]),
                         computeColor(split_src[1], mean_src[1], stddev_src[1], mean_ref[1], stddev_ref[1]),
                         computeColor(split_src[2], mean_src[2], stddev_src[2], mean_ref[2], stddev_ref[2])))

    img_out = LalphabetatoBGR(img_out)
    img_out = FloatToUint8(img_out)

    return img_out

def main(inputPath,outputPath,palettePath):
    FRAMERATE=25
    DIR_PATH = os.path.dirname(os.path.abspath(__file__))

    #Video to Img

    if os.path.exists(DIR_PATH+'/cache'):
        cmd = "rm -r "+DIR_PATH+"/cache"
        os.system(cmd)

    os.makedirs(DIR_PATH+'/cache')
    os.makedirs(DIR_PATH+'/cache/input')

    cmd="ffmpeg -i "+inputPath+" -vf fps="+str(FRAMERATE)+" "+DIR_PATH+"/cache/input/frame%04d.png -hide_banner"
    os.system(cmd)

    #Load Palette
    paletteNameList = glob.glob(palettePath+"*.png")
    paletteNameList=sorted(paletteNameList)

    palette = []
    for imgName in paletteNameList:
        print(imgName)
        img = cv2.imread(imgName)
        palette.append(img)

    paletteSize = len(palette)

    #Compute Transfert
    os.makedirs(DIR_PATH+'/cache/output')

    imgNameList = glob.glob(DIR_PATH+'/cache/input/'+"*.png")
    imgNameList=sorted(imgNameList)
    videoSize = len(imgNameList)

    cpt=0;
    for imgName in imgNameList:
        print(imgName)
        print("{0} %".format(cpt/videoSize * 100))
        img = cv2.imread(imgName)
        ref = interpolePalette(palette,cpt/videoSize)

        result = transfert(img,ref)
        #result = colour_transfer.colour_transfer_mkl(img,ref)

        filepath = os.path.basename(imgName)
        cv2.imwrite(DIR_PATH+'/cache/output/'+filepath,result)
        cpt+=1

    #IMG to video
    cmd = "ffmpeg -framerate "+str(FRAMERATE)+" -pattern_type glob -i \'"+DIR_PATH+"/cache/output/*.png\' -c:v libx264 -pix_fmt yuv420p "+outputPath
    os.system(cmd)


if __name__ == '__main__':
    args = parseArguments()
    main(args.input,args.output,args.palette)

