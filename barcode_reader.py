import cv2
import numpy as np
import matlab.engine


class BarcodeReader(object):
    
    def barcode_processing_nico(img_rgb):
        
        # Convert to HSV (Hue-Saturation-Value), pick hue
        img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
        hue = img_hsv[..., 0]
        
        # https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
        # Otsu's Binarization to pick threshold for bimodal distribution - not sure if that always works?
        _, mask = cv2.threshold(hue, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Count white pixels for each column
        vcount = (mask > 0).astype(np.uint8).sum(axis=0).astype(np.uint8)
        
        # Another Otsu to get a good threshold value for white pixels per column - note that max height of image must be less than 256
        threshold, mask = cv2.threshold(vcount, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        mask = ~mask
        
        # Generate image with same shape as input and repeat mask vertically
        barcode_img = np.repeat(mask.reshape(1,-1), img_rgb.shape[0], axis=0)
        #cv2.imwrite("C:/dev/data/barcode_out.png", barcode_img)
        
        ### This is hard coded and will need to be fixed at some point - EWH
        
        cv2.imwrite("C:/dev/data/barcode_out.png", barcode_img)
        barcode_path = "C:/dev/data/barcode_out.png"
        return barcode_path

    def barcode_reader_matlab():

        eng = matlab.engine.start_matlab()
        eng.barcode_reader(nargout=0)
        eng.quit()
        
        return 0
        
    def fetch_barcode_num():
        with open('C:/dev/data/barcode_file.txt', 'r') as f:
            barcode_num = f.readlines()
        return barcode_num

###############################################################################

#   Older Code from John Price

###############################################################################
#class BarcodeReader(object):
#    ''' barcode reader '''
#    def __init__(self, filename='barcode.tiff'):
#        self.filename = filename
#        self.barcode = ''
#
#    def read_barcode_from_file(self, fpath):
#        ''' synchronously read a barcode from a file'''
#        #fpath = 'C:/dev/data/barcode.jpg'
#        #print('fpath = ' + fpath)
#        p = Popen(['C:/Program Files (x86)/ZBar/bin/zbarimg.exe', '--raw', fpath], 
#                   stdout=PIPE, stderr=PIPE, stdin=PIPE)
#        barcode = p.stdout.read().strip()
#        p.stdout.close()
#        p.kill()
#        #print('Zbarcode = ' + str(barcode))
#        return barcode
#
#    def read_barcode(self, gray_im, enhance_image=False):
#        ''' from a grayscale image, extract the barcode '''
#        if gray_im is not None:
#            if enhance_image:
#                gray_im = cv2.medianBlur(gray_im, 7)
#
#            cv2.imwrite(self.filename, gray_im)
#            #print('Filename = ' + self.filename) # JHP temp
#            self.barcode = self.read_barcode_from_file(self.filename)
#            return self.barcode


