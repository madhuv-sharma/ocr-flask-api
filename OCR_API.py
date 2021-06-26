from difflib import SequenceMatcher
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS, cross_origin
from flask_ngrok import run_with_ngrok
import numpy as np
import pandas as pd
import csv, cv2, json, pytesseract, sys

# Initialize the app
app = Flask(__name__)
cors = CORS(app)
run_with_ngrok(app)

def error_handle(error_message, code=1, status=500, mimetype='application/json'):
    return Response(json.dumps({"success" : False, "message": error_message, "data": { "modelname": "" }, "code": code }), status=status, mimetype=mimetype)

def success_handle(output, status=200, mimetype='application/json'):
    return Response(output, status=status, mimetype=mimetype)

def checkDim(image):
   dimensions = image.shape
   if dimensions[0] < 990 or dimensions[1] < 1600 :
      return error_handle("Input Image should be of minimum dimensions 990*1600!")
   return cv2.resize(image, (1600, 991), interpolation = cv2.INTER_AREA)

def automatic_brightness_and_contrast(image, clip_hist_percent=1):
   gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   hist = cv2.calcHist([gray],[0],None,[256],[0,256])
   hist_size = len(hist)
   accumulator = []
   accumulator.append(float(hist[0]))
   for index in range(1, hist_size):
      accumulator.append(accumulator[index -1] + float(hist[index]))
   maximum = accumulator[-1]
   clip_hist_percent *= (maximum/100.0)
   clip_hist_percent /= 2.0
   minimum_gray = 0
   while accumulator[minimum_gray] < clip_hist_percent:
      minimum_gray += 1
   maximum_gray = hist_size -1
   while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
      maximum_gray -= 1
   alpha = 255 / (maximum_gray - minimum_gray)
   beta = -minimum_gray * alpha
   auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
   return auto_result

def preprocess(image):
   img = checkDim(image)
   auto_result = automatic_brightness_and_contrast(img)
   gray_image = cv2.cvtColor(auto_result, cv2.COLOR_BGR2GRAY)
   
   median = cv2.medianBlur(gray_image,9)
   
   blur = cv2.GaussianBlur(gray_image, (3,3), 0)
   ret, thresh2 = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
   kernel = np.ones((5,5), np.uint8)
   dilation = cv2.dilate(thresh2, kernel, iterations=1)   
   return (median, dilation, img)

def extract(median, dilation):
   csvFile=r"C:\Users\pc\Desktop\TECHWEIRDO\2. OCR for Canadian Driving Licence\BoundingBoxData.csv" # Will vary
   col_list = ["Field", "Text", "Conf"]
   with open(csvFile, 'r') as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=',')
      df = csv.DictReader(csv_file, usecols=col_list)
      lc = 0
      for row in csv_reader:
         if lc > 0 :
            x=int(row[3])
            xw=int(row[4])
            y=int(row[5])
            yh=int(row[6])
            text1 = pytesseract.image_to_string( median[y:yh, x:xw] )
            text3 = pytesseract.image_to_string( dilation[y:yh, x:xw] )
            arr1 = [3, 4]
            # arr2 = [1, 2, 7, 9]
            arr3 = [5, 6, 8, 10]
            if lc in arr1 :
               text=text1
            elif lc in arr3 :
               text=text3
            else:
               text=""
            row[1]=text
         lc+=1
   return json.dumps(df)

@app.route('/')
def welcome():
   return '''
   Welcome!
   '''

@app.route('/index')
def index():
   return '''
   /api/check to check Canadian Driving Licence
   /api/ocr for Candian Driving Licence OCR
   '''

@app.route('/api/check')
@cross_origin
def licCheck():
   pytesseract.pytesseract.tesseract_cmd = r"C:\Users\pc\AppData\Local\Tesseract-OCR\tesseract.exe" # Location will vary
   if 'file' not in request.files:
      raise error_handle('Image is required!')
   file = request.files['file']
   image = cv2.imread(file)
   cv2.waitKey(0)
   median, dilation, x = preprocess(image)
   temp1 = median[50:110 , 617:1027]
   temp3 = dilation[50:110 , 617:1027]
   st1 = pytesseract.image_to_string(temp1)
   st3 = pytesseract.image_to_string(temp3)
   if SequenceMatcher(None, "Driver's Licence", st3.strip()).ratio() > 0.5 or SequenceMatcher(None, "Driver's Licence", st1.strip()).ratio() > 0.5 :
      return success_handle("Canadian Driving Licence received as input. You are good to go!")
   else:
      return error_handle("Input image may not be a Canadian Driving Licence")

'''
def make_json(csvFilePath, jsonFilePath):
   fieldnames = ("Field", "Text", "Conf")
   with open(csvFilePath, 'r') as csvfile:
      reader = csv.DictReader(csvfile , fieldnames)
      rows = list(reader)
   with open(jsonFilePath, 'w') as jsonfile:
      json.dump(rows,jsonfile)
'''

@app.route("/api/ocr", methods=['POST','GET'])
def ocr():
   if request.method == 'POST':
      try:
         pytesseract.pytesseract.tesseract_cmd = r"C:\Users\pc\AppData\Local\Tesseract-OCR\tesseract.exe" # Location will vary
         if 'file' not in request.files:
            raise error_handle('Image is required!')
         file = request.files['file']
         image = cv2.imread(file)
         cv2.waitKey(0)
         median, dilation, x = preprocess(image)

         # Getting Bounding Box Coordinates and their respective confidence values :
         # print(pytesseract.image_to_data(dilation))

         return success_handle(extract(median, dilation))

      except Exception as e:
            return error_handle(str(e))
   return '''
      <!DOCTYPE HTML>
      <title>Face Match</title>
      <h1>Upload two images</h1>
      <form method=post enctype=multipart/form-data>
      <input type=image name=file1>
      <input type=image name=file2>
      <input type=submit value=Upload>
      </form>
      '''

app.run(debug=True)