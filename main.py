import argparse
import os
import cv2.cv2 as cv2
import numpy as np

def transfertColor(input,ref,output):
    pass

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input img", type=str)
    parser.add_argument("-s", "--src", help="Source img", type=str)
    parser.add_argument("-o", "--output", help="Output img", type=str)
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parseArguments()
    transfertColor(args.input,args.src,args.output)