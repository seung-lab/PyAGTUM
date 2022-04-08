# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 19:52:56 2022

@author: jprice
"""

from datetime import datetime

e = 'error'
time_now = datetime.now()


with open('C:/Users/jprice/Desktop/ERROR_test_EWH_32322.txt', 'a') as f:
    f.write(f'Post Camera: Error: {e}, Time: {time_now}')