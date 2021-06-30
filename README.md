# ocr-flask-api

I had created an OCR for Canadian Driving Licences, which first checked whether the input image is valid or not. If valid, it returned a JSON object which contained assorted data of all the information contained in the license - First Name, Sur Name, Address, ID #, Date Of Issue, Date Of Expiry, Reference #, Height, Sex and Date of Birth. To do so, I had preprocessed each images by 'hit and trial'ing various techniques - Mean, Adaptive and Otsu's Thresholding, Contrasting, Gaussian Blurring etc from the OpenCV and Scikit - Learn modules. This had to be done so as to get the best possible combination of preprocessing which would facilitate text recognition. First, I had used the image_to_data function of pytesseract to get the Bounding Box Coordinates of each phrase and their respective confidence values. Then I finalised two types of preprocessing which would facilitate the output of the majority of fields in the Driving Licence. Initially, I checked the dimensions of the input image and resized it according to my need. I had shrunk the bigger images and returned an error for smaller ones. Afterwards, the brightness and contrast of the image were fixed automatically[1]. Finally, I had preprocessed[2] the input into two different images. First one was just median blur and the second was gaussian blur along with dilation. Broadly, there are two types of fonts in the Canadian Driving Licence on the basis of their size and boldness. The small and thin fonts can be simply read in the median blurred image and the comparatively bigger and bolder ones can be read by gaussian blurring and dilation. The ones which are of some other type cause erroneous results as both preprocessed images aren't suitable for them. Actually, both preprocessed images do give 100% correct text response, but when the image is not cropped. To assort each field under their respective title the image is cropped into their respective bounding boxes so as to get only the text which is expected.

To program the OCR I had used csv (to input the information about the Bounding Box Coordinates), cv2 (for image processing, saving and display), difflib(to check whether input image is Canadian Driving License)[3], json (to store the output text field-wise), numpy (for faster calculations), pytesseract(to obtain the bounding box coordinates of the text (both word-by-word and character-by-character) and convert the input image to text) and sys (to exit the program) modules in Python.

Later on, I had made a Flask API from this.


    Sources:

    [1]		https://stackoverflow.com/a/56909036/8586764

    [2]		https://docs.opencv.org/master/index.html

    [3]		https://docs.python.org/3/library/difflib.html
