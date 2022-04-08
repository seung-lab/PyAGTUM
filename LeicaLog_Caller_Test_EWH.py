# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 11:01:25 2022

@author: jprice
"""

import pandas as pd
import cv2
import numpy as np

path = r"C:/dev/logs/LEICAchopper_20220128105852.csv"

wb = pd.read_csv(path)
df = pd.DataFrame(wb, columns = ['Time', 'Value'])

print(df)