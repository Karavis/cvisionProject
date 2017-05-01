import cv2
import numpy
import sys

names = {'0':'ALEX', '1':'MILIN', '2':'NICO', '3': 'PUNEETH'}

CASCADE = './data/haarcascade_frontalface_alt1.xml'
face_finder = cv2.CascadeClassifier(CASCADE)

recognizer = cv2.createEigenFaceRecognizer()
recognizer.load('model.xml')

IMAGEFPATH = './images/raw/alex/img5.jpg'

# if len(sys.argv) is not 2:
# 	print("Invalid arguments: try 'python main.py <image.jpg>'")
# 	sys.exit(1)

if len(sys.argv) is 2:
	IMAGEFPATH = sys.argv[1]

image = cv2.imread(IMAGEFPATH)
imageCopy = cv2.imread(IMAGEFPATH)
gray = cv2.imread(IMAGEFPATH, cv2.IMREAD_GRAYSCALE)
imageGR = cv2.resize(gray, (256, 256))
imageR = cv2.resize(image, (image.shape[1]//3, image.shape[0]//3))

minSize = min(image.shape[0], image.shape[1])/10

cv2.imshow("base", imageR)
cv2.waitKey(0)

faces = face_finder.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=5, minSize=(minSize, minSize), flags=cv2.CASCADE_SCALE_IMAGE)

print "{} faces detected".format(len(faces))

iteration = 0
for (x, y, w, h) in faces:
	iteration += 1
	roi = image[y:y+h, x:x+w]
	roiG = gray[y:y+h, x:x+w]

	roiR = cv2.resize(roi, (256, 256))
	roiGR = cv2.resize(roiG, (256, 256))

	prediction = recognizer.predict(roiGR)

	print 'Predicted: {}; Confidence: {}'.format(names[str(prediction[0])], prediction[1])

	cv2.putText(imageCopy, names[str(prediction[0])], (x, y), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0), 4)
	cv2.rectangle(imageCopy,(x,y),(x+w,y+h),(255,0,0),2)

	cv2.imshow("face {}".format(iteration), roi)
	cv2.waitKey(0)


imageCopy = cv2.resize(imageCopy, (imageCopy.shape[1]//3, imageCopy.shape[0]//3))
cv2.imshow("final", imageCopy)
cv2.waitKey(0)
cv2.destroyAllWindows()







