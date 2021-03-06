import cv2
import numpy
import sys

# Dictionary of names for display purposes
#names = {'0':'ALEX', '1':'ANDREW', '2':'EILEEN', '3':'MICHAEL', '4': 'MILIN', '5':'NICO', '6':'PAT', '7':'PUNEETH'}
names = {'0':'ALEX', '1':'EILEEN', '2':'MILIN', '3':'NICO', '4':'PUNEETH'}

# Base text for face labeling
BASETEXT = '{} {}'

# face detector classifier
# CASCADE = '/home/puneeth/public_html/facefinder/scripts/data/haarcascade_frontalface_alt1.xml'
CASCADE = './data/haarcascade_frontalface_alt1.xml'

# Default image filepath. Can be changed if an argument is passed 
# in via terminal
#IMAGEFPATH = '/home/puneeth/public_html/facefinder/scripts/images/raw/alex/img5.jpg'
IMAGEFPATH = './images/raw/alex/img5.jpg'

# Given a cascade face finder, and an image to workong
# returns a list of faces found in the image in the format (x, y, w, h)
# describing a rectangle around the face
def detect_faces(face_finder, image):

	# Min size is 1/10 of the smaller dimension of (height, width). 
	# Anything smaller than that will be discarded. 
	minSize = min(image.shape[0], image.shape[1])/10

	# Find all of the faces in the picture
	faces = face_finder.detectMultiScale(image, scaleFactor=1.01, minNeighbors=5, minSize=(minSize, minSize), flags=cv2.CASCADE_SCALE_IMAGE)

	print "{} faces detected".format(len(faces))

	return faces

# Given:
# 	recognizer: a trained face recognizer
# 	faces: a list of faces in the form (x, y, w, h)
#	image: the base image
#	gray: the base image, but grayscale
# 	labeledImage: a copy of the base image to be edited
# Returns a labeled image with boxes and labels for each face
def predict_faces(recognizer, faces, image, gray, labeledImage):
	# For each face, mark it with a blue square, run the recognizer 
	# against it, and label the square
	outList = list()
	iteration = 0
	for (x, y, w, h) in faces:
		iteration += 1
		# roi = region of interest, G = greyscale, R = resized, 
		# N = normalized
		roi = image[y:y+h, x:x+w]
		roiG = gray[y:y+h, x:x+w]

		roiR = cv2.resize(roi, (256, 256))
		roiGR = cv2.resize(roiG, (256, 256))

		# Normalize
		roiNGR = cv2.equalizeHist(roiGR)

		# Predict with the recognizer
		prediction = recognizer.predict(roiNGR)
		outList.append(prediction[0])

	return outList
'''
		print '{}: Predicted: {}; Confidence: {}'.format(iteration, names[str(prediction[0])], prediction[1])

		# Add rectangle and text label to faces
		cv2.putText(labeledImage, BASETEXT.format(iteration, names[str(prediction[0])]), (x, y-5), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0), 4)
		cv2.rectangle(labeledImage,(x,y),(x+w,y+h),(255,0,0),2)
'''
		# Show all of the detected faces 
		#cv2.imshow("face {}".format(iteration), roi)
		#cv2.waitKey(0)


def label_faces(all_predictions, faces, image):
	iteration = 0
	for (x, y, w, h) in faces:
		predictions = all_predictions[iteration]
		#prediction = numpy.argmax(predictions)
		prediction = numpy.argwhere(predictions == numpy.amax(predictions))
		prediction = prediction.flatten().tolist()
		string = ''
		for p in prediction:
			string += names[str(p)]
			string += ' '
		print '{}: Predicted: {}'.format(iteration+1, string)

		# Add rectangle and text label to faces
		cv2.putText(image, BASETEXT.format(iteration+1, string), (x, y-5), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 0), 4)
		cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)

		iteration += 1
	return image


if __name__ == '__main__':
	# If an argument has been passed in then that is the target image
	if len(sys.argv) is 2:
		IMAGEFPATH = sys.argv[1]

        NEWIMAGEFPATH = IMAGEFPATH.split(".")[0] + "_FINAL." + IMAGEFPATH.split(".")[1]

	# Reads images in normal format, greyscale, and scaled to 256x256
	image = cv2.imread(IMAGEFPATH)
	labeledImage = cv2.imread(IMAGEFPATH)
	gray = cv2.imread(IMAGEFPATH, cv2.IMREAD_GRAYSCALE)
	imageGR = cv2.resize(gray, (256, 256))
	imageR = cv2.resize(image, (image.shape[1]//3, image.shape[0]//3))

	# Display the input image, just as a sanity check
	#cv2.imshow("base", imageR)
	#cv2.waitKey(0)

	face_finder = cv2.CascadeClassifier(CASCADE)
	faces = detect_faces(face_finder, gray)

	# Since the recognizer is kind of inaccurate, what if we 
	# use multiple recognizers and pick the prediction with
	# the most votes?
	recognizers = list()

	#Lets do 3 of each type of recognizer (Eigen, Fisher, LBPH)
	for i in range(3):
		recognizer = cv2.createEigenFaceRecognizer()
		#filen = '/home/puneeth/public_html/facefinder/scripts/models/modelE{}.xml'.format(i+1)
		filen = './models/modelE{}.xml'.format(i+1)
		print "loading {}".format(filen)
		recognizer.load(filen)
		recognizers.append(recognizer)

	for i in range(3):
		recognizer = cv2.createFisherFaceRecognizer()
		#filen = '/home/puneeth/public_html/facefinder/scripts/models/modelF{}.xml'.format(i+1)
		filen = './models/modelF{}.xml'.format(i+1)
		print "loading {}".format(filen)
		recognizer.load(filen)
		recognizers.append(recognizer)

	for i in range(3):
		recognizer = cv2.createLBPHFaceRecognizer()
		#filen = '/home/puneeth/public_html/facefinder/scripts/models/modelL{}.xml'.format(i+1)
		filen = './models/modelL{}.xml'.format(i+1)
		print "loading {}".format(filen)
		recognizer.load(filen)
		recognizers.append(recognizer)

	# Local Binary Pattern/etc.
	#recognizer = cv2.createLBPHFaceRecognizer()
	#recognizer = cv2.createEigenFaceRecognizer()
	#recognizer = cv2.createFisherFaceRecognizer()
	#recognizer.load('./models/modelE.xml')

	# Create a NxM array to store predictions, where 
	# N = amount of people possible
	# M = amount of faces detected
	all_predictions = numpy.zeros((len(faces), len(names)))

 	for recognizer in recognizers:
		predictions = predict_faces(recognizer, faces, image, gray, labeledImage)
		for i in range(len(predictions)):
			all_predictions[i][predictions[i]] += 1

	print(all_predictions)

	labeledImage = label_faces(all_predictions, faces, labeledImage)


	# Show the final picture with labels
	labeledImage = cv2.resize(labeledImage, (labeledImage.shape[1]//3, labeledImage.shape[0]//3))


    #cv2.imwrite(NEWIMAGEFPATH, labeledImage)
	cv2.imwrite("images/raw/out.jpg", labeledImage)
	cv2.imshow("final", labeledImage)
	cv2.waitKey(0)
	cv2.destroyAllWindows()






