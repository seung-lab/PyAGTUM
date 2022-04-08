 #EWH: setup necessary location, etc. 
import pandas as pd
import cv2
path_to_luxell_file = 'C:/Users/jprice/Downloads/Spool#1050-250 QA Datasheet 4-1-2021 (sample of current milling quality).csv' 
#path_to_luxell_images = self.textEdit_Luxell_image_location_2.toPlainText()

#wb = pd.read_csv(path_to_luxell_file)
#df = pd.DataFrame(wb, columns = ['Slot #', 'Wrinkle Code', 'QA Code', 'Luxel R/N', 'Thickness (nm)', 'Comments'])

#print(df)

#
#wb = pd.read_csv(path_to_luxell_file, skiprows=13)
#df = pd.DataFrame(wb, columns = ['Slot #', 'Wrinkle Code', 
#                                 'QA Code', 'Luxel R/N', 
#                                 'Thickness (nm)', 
#                                 'Comments'])
##print(df)
#sheet_num = 246
#QA_code = df['QA Code']
#
##print(QA_code)
#
#QA_code_aperture = QA_code[sheet_num]
#
#print(QA_code_aperture)



barcode_number = 199

if barcode_number <= 9:
    barcode_image_file = f'/000{barcode_number}.jpg'
if 10 <= barcode_number <= 99:
    barcode_image_file = f'/00{barcode_number}.jpg'
if 100 <= barcode_number <= 999:
    barcode_image_file = f'/0{barcode_number}.jpg'
if 1000 <= barcode_number <= 9999:
    barcode_image_file = f'/{barcode_number}.jpg'

path = f'C:/Users/jprice/Downloads/Spool#1050-250 Inspection 4-1-2021-20220120T154213Z-001/Spool#1050-250 Inspection 4-1-2021{barcode_image_file}'

path_1 = '/C/OS/soemthing'
number= '/0004.jpg'
string_add = path_1 + number
print(string_add)

#print(path)
Qimg = cv2.imread(path)

Qimg_cropped = Qimg[300:1050, 750:1700]

cv2.imshow("name", Qimg_cropped)
cv2.waitKey(0)

