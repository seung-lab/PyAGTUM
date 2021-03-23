


import os
import time
import numpy as np
from subprocess import Popen, PIPE
import cv2

class BarcodeReader(object):
    ''' barcode reader '''
    def __init__(self, filename='barcode.tiff'):
        self.filename = filename
        self.barcode = ''

    def read_barcode_from_file(self, fpath):
        ''' synchronously read a barcode from a file'''
        #fpath = 'C:/dev/data/barcode.jpg'
        #print('fpath = ' + fpath)
        p = Popen(['C:/Program Files (x86)/ZBar/bin/zbarimg.exe', '--raw', fpath], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        barcode = p.stdout.read().strip()
        print('Zbarcode = ' + str(barcode))
        return barcode

    def read_barcode(self, gray_im, enhance_image=False):
        ''' from a grayscale image, extract the barcode '''
        if gray_im is not None:
            if enhance_image:
                gray_im = cv2.medianBlur(gray_im, 7)

            cv2.imwrite(self.filename, gray_im)
            print('Filename = ' + self.filename) # JHP temp
            self.barcode = self.read_barcode_from_file(self.filename)
            return self.barcode






path = r'C:\Users\jprice\Desktop\Zhihao\210317-2nd_200_section_run\210322-Capture_defect_test_barcode-1.jpg'

im = cv2.imread(path)

gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)




barcode = br.read_barcode (gray)



path = r'C:\Users\jprice\Desktop\Zhihao\210317-2nd_200_section_run\210322-Capture_defect_test_barcode-2f.tif'


path = r'C:\Users\jprice\Desktop\Zhihao\210323-barcode_test\AW_Capture_cropped.png'
im = cv2.imread(path)
gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)


cv2.imshow('image',gray); cv2.waitKey(0)

