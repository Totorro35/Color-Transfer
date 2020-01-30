import argparse
import os
import glob
import cv2.cv2 as cv2
import math
import numpy as np

def computeColor(src, mean_src, stdDev_src, mean_ref, stdDev_ref):
    val = src - mean_src
    coeff = stdDev_ref/stdDev_src
    result = coeff*val + mean_ref
    return result

def FloatToUint8(image):
    image= np.clip(image, 0, 255)
    image=image.astype(np.uint8)
    return image

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input video", type=str)
    parser.add_argument("-o", "--output", help="Output vido", type=str)
    parser.add_argument("-p", "--palette", help="Palette", type=str)
    args = parser.parse_args()

    return args

def interpolePalette(palette,coeff):
    val = coeff % (len(palette))
    idxA = math.floor(val)
    idxB = idxA + 1
    if(idxB==len(palette)):
        idxB=0
    imgA = palette[idxA]
    imgB = palette[idxB]
    inter = (val-idxA)/(idxB-idxA)
    return FloatToUint8((1-inter)*imgA+(inter)*imgB)

def transfert(src,ref,gamma=1.0):
    img_src=src
    #img_src = adjust_gamma(src,gamma)
    #img_src = BGRtoLalphabeta(img_src)

    img_ref=ref
    #img_ref = adjust_gamma(ref,gamma)
    #img_ref = BGRtoLalphabeta(img_ref)

    mean_src, stddev_src = cv2.meanStdDev(img_src)
    mean_ref, stddev_ref = cv2.meanStdDev(img_ref)
    split_src = cv2.split(img_src)
    img_out = cv2.merge((computeColor(split_src[0], mean_src[0], stddev_src[0], mean_ref[0], stddev_ref[0]),
                         computeColor(split_src[1], mean_src[1], stddev_src[1], mean_ref[1], stddev_ref[1]),
                         computeColor(split_src[2], mean_src[2], stddev_src[2], mean_ref[2], stddev_ref[2])))

    #img_out = LalphabetatoBGR(img_out)
    img_out = FloatToUint8(img_out)

    return img_out

def main(inputPath,outputPath,palettePath):
    DIR_PATH = os.path.dirname(os.path.abspath(__file__))

    #Load Palette
    paletteNameList = glob.glob(palettePath+"*.png")
    paletteNameList=sorted(paletteNameList)

    palette = []
    for imgName in paletteNameList:
        print(imgName)
        img = cv2.imread(imgName)
        palette.append(img)

    paletteSize = len(palette)

    # Create a VideoCapture object
    cap = cv2.VideoCapture(inputPath)

    # Check if camera opened successfully
    if (cap.isOpened() == False): 
        print("Unable to read camera feed")
 
    # Default resolutions of the frame are obtained.The default resolutions are system dependent.
    # We convert the resolutions from float to integer.
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
    out = cv2.VideoWriter(outputPath,cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width,frame_height))

    cpt=0
    while(True):
        print(cpt/30)
        ret, frame = cap.read()

        if ret == True:
            ref = interpolePalette(palette,cpt/100)
            result = transfert(frame,ref)

            out.write(result)
            #cv2.imshow('frame',result)
             # Press Q on keyboard to stop recording
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break
        # Break the loop
        else:
            break

        cpt+=1
 
    # When everything done, release the video capture and video write objects
    cap.release()
    out.release()

    # Closes all the frames
    cv2.destroyAllWindows()

if __name__ == '__main__':
    args = parseArguments()
    main(args.input,args.output,args.palette)