# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 14:51:11 2022

@author: jprice
"""

from PIL import Image, ImageFilter
import numpy as np 
import cv2

import time

#Read image
im = Image.open(r'C:\dev\data\eric_post_cam_image.png' )
#Display image
#im.show()

width, height = im.size

im_cropped = im.crop((500,height/3,850,3*height / 5))

#im_cropped.show()

##Applying a filter to the image
#im_sharp = im.filter( ImageFilter.SHARPEN )
##Saving the filtered image to a new file
#im_sharp.save( r'C:\Users\jprice\Desktop\image_sharpened.jpg', 'JPEG' )
#im_sharp.show()
#
##Splitting the image into its respective bands, i.e. Red, Green,
##and Blue for RGB
#r,g,b = im_sharp.split()
#
##Viewing EXIF data embedded in image
#exif_data = im._getexif()
#exif_data

im_cropped = im_cropped.save(r'C:\dev\data\eric_post_cam_image_cropped.png')


clahefilter = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16,16))


img = cv2.imread(r'C:\dev\data\eric_post_cam_image_cropped.png')

