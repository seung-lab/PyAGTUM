#from __future__ import print_function
#import cv2
#import numpy as np
#from pyzbar.pyzbar import decode
#  
## Make one method to decode the barcode
#class BarcodeReader(object):
#    def barcodereader(img):
#        # Decode the barcode image
#        #blurred = cv2.blur(img, (7, 7))
#        #cv2.imshow('image',blurred); cv2.waitKey(0)
#        detectedBarcodes = decode(img)
#        
#        print(detectedBarcodes)
#          
#        # If not detected then print the message
#        if not detectedBarcodes:
#            return_barcode = 'NA'
#            #print("Barcode Not Detected or your barcode is blank/corrupted!")
#        else:
#           
#              # Traverse through all the detected barcodes in image
#            for barcode in detectedBarcodes: 
#               
#                # Locate the barcode position in image
#                (x, y, w, h) = barcode.rect
#                 
#                # Put the rectangle in image using
#                # cv2 to heighlight the barcode
#                cv2.rectangle(img, (x-10, y-10),
#                              (x + w+10, y + h+10),
#                              (255, 0, 0), 2)
#                 
#                if barcode.data!="":
#                   
#                # Print the barcode data
#                    #print(barcode.data)
#                    #print(barcode.type)
#                    return_barcode = barcode.data.decode('utf-8')
#                    
#        return return_barcode
#
#path = 'C:/dev/data/barcode.png'
#path_2 = 'C:/Users/jprice/Desktop/Zhihao/210323-barcode_test/AW_Capture_cropped.png'
#img = cv2.imread(path)
#
## 
### making border around image using copyMakeBorder
##borderoutput = cv2.copyMakeBorder(
##    img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[255, 255, 255])
## 
### showing the image with border
##cv2.imshow('image',borderoutput); cv2.waitKey(0)
##cv2.imwrite('C:/dev/data/barcode_border.png', borderoutput)
#
#img = np.array(img)
#
##import imutils
##    
##
##image = cv2.imread(path)
##resized = imutils.resize(image, width=300)
##ratio = image.shape[0] / float(resized.shape[0])
### convert the resized image to grayscale, blur it slightly,
### and threshold it
###gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
##blurred = cv2.GaussianBlur(image, (5, 5), 0)
##cv2.imshow('image',blurred); cv2.waitKey(0)
##thresh = cv2.threshold(blurred, 10, 255, cv2.THRESH_BINARY)[1]
### find contours in the thresholded image and initialize the
### shape detector
##
##cv2.imshow('image',thresh); cv2.waitKey(0)
##
##
##new_image = image[image <= 40] = 255
##cv2.imshow('image',new_image); cv2.waitKey(0)
#
##img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    
##print(img.shape)
##barcode = BarcodeReader.barcodereader(img)
##print(barcode)
#
#################################################################################
#
#
#import os
#import time
#import numpy as np
#from subprocess import Popen, PIPE
#import cv2
#
#class BarcodeReader_JP(object):
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
##        p.stdout.close()
##        p.kill()
#        #print('Zbarcode = ' + str(barcode))
#        return barcode
#
#    def read_barcode(self, gray_im, enhance_image=True):
#        ''' from a grayscale image, extract the barcode '''
#        if gray_im is not None:
#            if enhance_image:
#                print("entered enhance")
#                gray_im = cv2.medianBlur(gray_im, 7)
#                cv2.imshow('image',gray_im); cv2.waitKey(0)
#
#            cv2.imwrite(self.filename, gray_im)
#            #print('Filename = ' + self.filename) # JHP temp
#            self.barcode = self.read_barcode_from_file(self.filename)
#            return self.barcode
#        
###path = r'C:\Users\jprice\Desktop\Zhihao\210317-2nd_200_section_run\210322-test_bar_code_f.tif'
##path = r'C:\Users\jprice\Desktop\Zhihao\210323-barcode_test\AW_Capture_cropped.png'
#im = cv2.imread(path_2)
#
##gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
#
##barcode = BarcodeReader_JP(path).read_barcode(im)
##print(f"This is the barcode: {barcode}")
#
##################################################################################
#from pyzbar import pyzbar
#
#class Barcode_reader_2(object):
#    def find_barcode(image):
#        # find the barcodes in the image and decode each of the barcodes
#        barcodes = pyzbar.decode(image)
#        
#        # loop over the detected barcodes
#        for barcode in barcodes:
#        	# extract the bounding box location of the barcode and draw the
#        	# bounding box surrounding the barcode on the image
#        	(x, y, w, h) = barcode.rect
#        	cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
#        	# the barcode data is a bytes object so if we want to draw it on
#        	# our output image we need to convert it to a string first
#        	barcodeData = barcode.data.decode("utf-8")
#        	barcodeType = barcode.type
#        	# draw the barcode data and barcode type on the image
#        	text = "{} ({})".format(barcodeData, barcodeType)
#        	cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
#        		0.5, (0, 0, 255), 2)
#        	# print the barcode type and data to the terminal
#        	print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
#        # show the output image
#        cv2.imshow("Image", image)
#        cv2.waitKey(0)
#        return barcodeData
#        
##barcode = Barcode_reader_2.find_barcode(im)
##print(barcode)
#        
#    
##################################################################################
#
#
#
#import pyzbar.pyzbar as pyzbar
#import numpy as np
#import cv2
#
#def decode_2(im) :
#  # Find barcodes and QR codes
#  decodedObjects = pyzbar.decode(im)
#  # Print results
#  for obj in decodedObjects:
#      print('Type : ', obj.type)
#      print('Data : ', obj.data,'\n')
#  return decodedObjects
## Display barcode and QR code location
#def display(im, decodedObjects):
#  # Loop over all decoded objects
#  for decodedObject in decodedObjects:
#    points = decodedObject.polygon
#    # If the points do not form a quad, find convex hull
#    if len(points) > 4 :
#      hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
#      hull = list(map(tuple, np.squeeze(hull)))
#    else :
#      hull = points;
#    # Number of points in the convex hull
#    n = len(hull)
#    # Draw the convext hull
#    for j in range(0,n):
#      cv2.line(im, hull[j], hull[ (j+1) % n], (255,0,0), 3)
#  # Display results
#  cv2.imshow("Results", im);
#  cv2.waitKey(0);
## Main
#  
##
##decodedObjects = decode(im)
##display(im, decodedObjects)
#
####################################################################################
#import cv2
#import numpy as np
#from skimage import io      # Only needed for web grabbing images, use cv2.imread for local images
#
#def vert_edge_detect(path):
#    # Read image from web (is already grayscale)
#    image = io.imread(path)
#    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#    
#    # Apply adaptive threshold
#    image_thr = cv2.adaptiveThreshold(image, 255, cv2.THRESH_BINARY_INV, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 51, 0)
#    
#    # Apply morphological opening with vertical line kernel
#    kernel = np.ones((image.shape[0], 1), dtype=np.uint8) * 255
#    image_mop = cv2.morphologyEx(image_thr, cv2.MORPH_OPEN, kernel)
#    
#    # Canny edge detection
#    image_canny = cv2.Canny(image_mop, 1, 3)
#    
#    # Get pixel values from the input image (force RGB/BGR on given input) within stripes
#    image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
#    pixels = image_bgr[image_mop > 0, :]
#    print(pixels)
#    
#    # (Visualization) Output
#    cv2.imshow('image', image)
#    cv2.imshow('image_thr', image_thr)
#    cv2.imshow('image_mop', image_mop)
#    cv2.imshow('image_canny', image_canny)
#    cv2.waitKey(0)
#    cv2.destroyAllWindows()

#########################################################################################################
    
#imagem = cv2.bitwise_not(img)
#cv2.imshow('image_canny', imagem)
#cv2.waitKey(0)
    
    
###################################################################################

##========================
## Import Libraies
##========================
#import numpy as np
##import cv2 as cv
#import matplotlib.pyplot as plt 
#from pyzbar import pyzbar
#
##------------------------
## Read Image
##========================
#img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
#
## #------------------------
## # Morphology
## #========================
## # Closing
## #------------------------
#closed = cv2.morphologyEx(img, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 21)))
#
## #------------------------
## # Statistics
## #========================
#print(img.shape)
#dens = np.sum(img, axis=0)
#mean = np.mean(dens)
#print(mean)
#
##------------------------
## Thresholding
##========================
#thresh = closed.copy()
#for idx, val in enumerate(dens):
#    if val< 10800:
#        thresh[:,idx] = 100
#
#(_, thresh2) = cv2.threshold(thresh, 0, 25, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#
##------------------------
## plotting the results
##========================
#plt.figure(num='barcode')
#
#plt.subplot(221)
#plt.imshow(img, cmap='gray')
#plt.title('Original')
#plt.axis('off')
#
#plt.subplot(224)
#plt.imshow(thresh, cmap='gray')
#plt.title('Thresholded')
#plt.axis('off')
#
#plt.subplot(223)
#plt.imshow(thresh2, cmap='gray')
#plt.title('Result')
#plt.axis('off')
#
#plt.subplot(222)
#plt.hist(dens)
#plt.axvline(dens.mean(), color='k', linestyle='dashed', linewidth=1)
#plt.title('dens hist')
#
#plt.show()
#
##------------------------
## Printing the Output
##========================
#barcodes = pyzbar.decode(thresh2)
#print(barcodes)

####################################################################################

import cv2
import numpy as np
#import scipy.misc

#path = 'C:/dev/data/barcode.png'
#
#img = cv2.imread(path)

def barcode_find_reconstruct(img):
    # creating mask using thresholding over `red` channel (use better use histogram to get threshoding value)
    # I have used 200 as thershoding value it can be different for different images
    ret, mask = cv2.threshold(img[:, :,2], 100, 255, cv2.THRESH_BINARY)
    
    mask3 = np.zeros_like(img)
    mask3[:, :, 0] = mask
    mask3[:, :, 1] = mask
    mask3[:, :, 2] = mask
    
    # extracting `orange` region using `biteise_and`
    orange = cv2.bitwise_and(img, mask3)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img  = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    # extracting non-orange region
    gray = cv2.bitwise_and(img, 255 - mask3)
    
    # orange masked output
    out = gray + orange
    
    #cv2.imshow('orange', orange)
    #cv2.imshow('gray', gray)
    #cv2.imshow('output', out)
    #cv2.waitKey(0)
    
    #EWH: trying to make all but the black pixels gray. 
    bandw_array = np.array(gray)
    #print(np.shape(bandw_array))
    #print(len(bandw_array[0:]))
    #print(len(bandw_array[0]))
    #print(range(len(bandw_array)))
    #print(bandw_array[200][200][1])
    for i in range(len(bandw_array[0:])):
        for h in range(len(bandw_array[0])):
            for j in range(3):
                if bandw_array[i][h][j] > 0:
                    bandw_array[i][h][j] = 255
    
    #print(bandw_array[200][200][1])
    
    
    
    cv2.imshow('black and white image', bandw_array)
    cv2.waitKey(0)
        
    #========================
    # Import Libraies
    #========================
    #import cv2 as cv
    import matplotlib.pyplot as plt 
    from pyzbar import pyzbar
    
    #------------------------
    # Read Image
    #========================
    #img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img_gray = cv2.cvtColor(bandw_array, cv2.COLOR_BGR2GRAY)
    # #------------------------
    # # Morphology
    # #========================
    # # Closing
    # #------------------------
    closed = cv2.morphologyEx(img_gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 21)))
    
    # #------------------------
    # # Statistics
    # #========================
    print(img_gray.shape)
    dens = np.sum(img_gray, axis=0)
    mean = np.mean(dens)
    print(mean)
    
    #------------------------
    # Thresholding
    #========================
    thresh = closed.copy()
    for idx, val in enumerate(dens):
        if val< 10800:
            thresh[:,idx] = 100
    
    (_, thresh2) = cv2.threshold(thresh, 0, 25, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    #------------------------
    # plotting the results
    #========================
    plt.figure(num='barcode')
    
    plt.subplot(221)
    plt.imshow(img_gray, cmap='gray')
    plt.title('Original')
    plt.axis('off')
    
    plt.subplot(224)
    plt.imshow(thresh, cmap='gray')
    plt.title('Thresholded')
    plt.axis('off')
    
    plt.subplot(223)
    plt.imshow(thresh2, cmap='gray')
    plt.title('Result')
    plt.axis('off')
    
    plt.subplot(222)
    plt.hist(dens)
    plt.axvline(dens.mean(), color='k', linestyle='dashed', linewidth=1)
    plt.title('dens hist')
    
    plt.show()
    
    #------------------------
    # Printing the Output
    #========================
    barcodes = pyzbar.decode(thresh2)
    print(barcodes)
    
    print(np.shape(thresh2))
    print(len(thresh2[0:]))
    print(len(thresh2[0]))
    
    for i in range(len(thresh2[0:])):
        for h in range(len(thresh2[0])):
            if thresh2[i][h] > 0:
                thresh2[i][h] = 255
                    
    cv2.imwrite('C:/dev/data/barcode_process_1_result.png', thresh2)
    




##############################################################################


#clahefilter = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16,16))
#
#
#img = cv2.imread(path)

def HSV_plusmore_filtering(img):
    img = img.copy()
    
    ## crop if required 
    #FACE
    x,y,h,w = 550,250,400,300
    # img = img[y:y+h, x:x+w]
    
    #NORMAL
    # convert to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grayimg = gray
    
    
    GLARE_MIN = np.array([0, 0, 50],np.uint8)
    GLARE_MAX = np.array([0, 0, 225],np.uint8)
    
    hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    
    #HSV
    frame_threshed = cv2.inRange(hsv_img, GLARE_MIN, GLARE_MAX)
        
    
    #INPAINT
    mask1 = cv2.threshold(grayimg , 220, 255, cv2.THRESH_BINARY)[1]
    result1 = cv2.inpaint(img, mask1, 0.1, cv2.INPAINT_TELEA) 
    
    
    
    #CLAHE
    claheCorrecttedFrame = clahefilter.apply(grayimg)
    
    #COLOR 
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    lab_planes = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    lab_planes[0] = clahe.apply(lab_planes[0])
    lab = cv2.merge(lab_planes)
    clahe_bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    
    #INPAINT + HSV
    result = cv2.inpaint(img, frame_threshed, 0.1, cv2.INPAINT_TELEA) 
    
    
    #HSV+ INPAINT + CLAHE
    lab1 = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
    lab_planes1 = cv2.split(lab1)
    clahe1 = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    lab_planes1[0] = clahe1.apply(lab_planes1[0])
    lab1 = cv2.merge(lab_planes1)
    clahe_bgr1 = cv2.cvtColor(lab1, cv2.COLOR_LAB2BGR)
    
    
    
    
    # fps = 1./(time.time()-t1)
    # cv2.putText(clahe_bgr1    , "FPS: {:.2f}".format(fps), (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255))    
     
    cv2.imshow("HSV + INPAINT + CLAHE   ", clahe_bgr1)
    cv2.waitKey(0)
    
    # Break with esc key
    
    
    
    
    cv2.destroyAllWindows()

###############################################################################


  
#hsv_image = cv2.imread('C:/dev/data/hsv_h.png')
#hsv_image_invert = np.invert(hsv_image)
#cv2.imwrite('C:/dev/data/hsv_h_invert.png', hsv_image_invert)
#
##-----Converting image to LAB Color model----------------------------------- 
#lab= cv2.cvtColor(hsv_image_invert, cv2.COLOR_BGR2LAB)
##cv2.imshow("lab",lab)
#
##-----Splitting the LAB image to different channels-------------------------
#l, a, b = cv2.split(lab)
##cv2.imshow('l_channel', l)
##cv2.imshow('a_channel', a)
##cv2.imshow('b_channel', b)
#
##-----Applying CLAHE to L-channel-------------------------------------------
#clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
#cl = clahe.apply(l)
##cv2.imshow('CLAHE output', cl)
#
##-----Merge the CLAHE enhanced L-channel with the a and b channel-----------
#limg = cv2.merge((cl,a,b))
##cv2.imshow('limg', limg)
#
##-----Converting image from LAB Color model to RGB model--------------------
#final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
##cv2.imwrite('C:/dev/data/CLAHE_barcode_image.png',final)
##cv2.imshow('final', final)
##cv2.waitKey(0)

path = 'C:/dev/data/barcode.png'

#from dbr import BarcodeReader, EnumBarcodeFormat, EnumBarcodeFormat_2, BarcodeReaderError
#
#reader = BarcodeReader()
#
#para = BarcodeReader.init_dls_connection_parameters()
#para.organization_id = "100849540"
#
#BarcodeReader.init_license_from_dls(para)
#        
#settings = reader.get_runtime_settings()
#settings.barcode_format_ids = EnumBarcodeFormat.BF_ALL
##settings.barcode_format_ids_2 = EnumBarcodeFormat_2.BF2_POSTALCODE | EnumBarcodeFormat_2.BF2_DOTCODE
#settings.excepted_barcodes_count = 32
#reader.update_runtime_settings(settings)
#
#try:
#   barcode_img = nico_is_genius(path)
#   image = barcode_img
#   text_results = reader.decode_file(image)
#   if text_results != None:
#      for text_result in text_results:
#         print("Barcode Format : " + text_result.barcode_format_string)
#         if len(text_result.barcode_format_string) == 0:
#            print("Barcode Format : " + text_result.barcode_format_string_2)
#         else:
#            print("Barcode Format : " + text_result.barcode_format_string)
#         print("Barcode Text : " + text_result.barcode_text)
#except BarcodeReaderError as bre:
#   print(bre)
#
#print(np.shape(final))
#final_crop = final[60:228, 0:1000]
#
#cv2.imshow('image', final_crop)
#cv2.waitKey(0)
#
#
#john_path = 'C:/dev/data/CLAHE_barcode_image.png'
#
#print("Whats up")


#reader = BarcodeReader()
#
##EWH: this has a 30 day trial on it.
#para = BarcodeReader.init_dls_connection_parameters()
#para.organization_id = "100849540"
#
#BarcodeReader.init_license_from_dls(para)
#        
#settings = reader.get_runtime_settings()
#settings.barcode_format_ids = EnumBarcodeFormat.BF_ALL
##settings.barcode_format_ids_2 = EnumBarcodeFormat_2.BF2_POSTALCODE | EnumBarcodeFormat_2.BF2_DOTCODE
#settings.excepted_barcodes_count = 32
#reader.update_runtime_settings(settings)
#
#barcode_path = 'C:/dev/data/barcode_out.png'
#
#text_results = reader.decode_file(barcode_path)
#if text_results != None:
#    print(text_results)
#
#    for text_result in text_results:
#        print("Barcode Format : " + text_result.barcode_format_string)
#        if len(text_result.barcode_format_string) == 0:
#            print("Barcode Format : " + text_result.barcode_format_string_2)
#        else:
#            print("Barcode Format : " + text_result.barcode_format_string)
#            print("Barcode Text : " + text_result.barcode_text)
#            barcode_num = text_result.barcode_text
#else: 
#    barcode_num = 'NA'
#    
#print(barcode_num)

    
    
    
#################################################################################
import cv2
import numpy as np

def nico_is_genius(path):
    img_rgb = cv2.imread(path)
    
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
    cv2.imwrite("C:/dev/data/barcode_out.png", barcode_img) 
    return barcode_img

from pyzbar import pyzbar

image = cv2.imread('C:/dev/data/barcode_out.png')

from pyzbar.pyzbar import ZBarSymbol
from pyzbar.pyzbar import decode
from PIL import Image
#Look for just qrcode
banana = decode(Image.open('C:/dev/data/barcode_out.png'), symbols=[ZBarSymbol.I25])
print(banana)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

