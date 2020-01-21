#importing modules needed
import cv2                                                                                  
import numpy as np
import time                                                                              

#Approximate test HSV values for skin color
maxHSV = (42, 255, 109)                                                                         
minHSV =(0, 0, 0)

#pixelsPerInch = (8/430.1687206)
pixelsPerInch = (7/156)
focalLengthNumerator = 582*7

#HSV values for blue on painter's tape
minHSVBlue = np.array([24, 72, 95])                                                             
maxHSVBlue = np.array([46, 181, 255])  

#HSV values for the yellow game ball
minHSVBall = np.array([28,  76,  89])
maxHSVBall = np.array([36, 255, 255])

#Font that will be used to display the text on screen
font = cv2.FONT_HERSHEY_SIMPLEX

#Boolean switch that decides whether images used are from camera or from filesystem
TestImage = False

#Use camera images
if TestImage == False:

    #Create a window with the following name                                                                          
    cv2.namedWindow("preview")

    #start the camera                                                                  
    vc = cv2.VideoCapture(0)                                                                    

    #If camera is open and taking shots
    if vc.isOpened():                                                                           
        rval, frame = vc.read() 
    else:                                                                                       
        rval = False

    saveCount = 0
    elapsedAccum = 0
    loopCount = 1
    #Do this while reading images
    while rval:
        # start timing
        startTime = time.time()

        rval, frame = vc.read()  
        endTime = time.time()
        elapsedCam = endTime-startTime

        #Convert the RGB image to HSV
        imHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #print("frame type is ", type(frame))
        #print("imHSV type is ", type(imHSV))
        #Find pixels in the blurred image that fit in range and turn them white and others black                                          
        InRange = cv2.inRange(imHSV, minHSVBall, maxHSVBall)

        #Using the black and white binary image, plot a point at every boundry pixel that is white
        contours, _ = cv2.findContours(InRange, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        #Find the biggest contour since that will be the object we are looking for
        try:
            areas = [cv2.contourArea(c) for c in contours]
            max_index = np.argmax(areas)
            cnt=contours[max_index]
        except:
            print("Could not find any contours")
            #continue??? go to top of loop

        #Using the contours approximate a rectangle to fit the shape
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        #Calculating Distance
        #(x, y), (width, height), angle = rect
        #if (width > height):
        #    angle = angle - 90
        #    width, height = height, width

        #print("Height of image based on rotated rect: " + str(height))
        #DistZ = (8.046355677641872 - (height * pixelsPerInch)) + 8.046355677641872
        #print("The object is: " + str(DistZ) + " in away from you")
        #print("The angle is: " + str(angle))
        #except:
         #   print("No contour found!")

        # Use openCV circle to estimate dist and angle
        center,radius = cv2.minEnclosingCircle(cnt)
        radiusInt = int(radius)
        tup1 = (int (center[0]), int (center[1]))
        cv2.circle(frame,tup1,radiusInt,[255,0,0])
        height = 2 * radius
        #print("Height of image based on circle: " + str(height))
        
        DistZ = focalLengthNumerator/height

        #Using moments to find the center of the image
        #try:
        M = cv2.moments(box)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        #except:
         #   print("No contours found!")

        if saveCount == 0:
            saveCount = saveCount + 1
            #cv2.drawContours(frame, contours, max_index, [0, 0, 255])
            cv2.drawContours(frame, [box], 0, [0, 128, 128])
            cv2.imwrite("InRange.jpg", InRange)
            cv2.imwrite("ImagingOutput.jpg", frame)                               

        # end timing
        endTime = time.time()
        elapsed = endTime-startTime
        elapsedAccum = elapsedAccum + elapsed
        print(elapsed, " sec loop ", elapsedCam, " sec camera read    Dist: " + str(DistZ))
        print(elapsedAccum/loopCount, "Elapsed Accum per loop")
        #Incrament the loop counter
        loopCount = loopCount + 1

#If we want to use images from the file system
if TestImage == True:

    #Read the image UNCHANGED specified in ""
    frame = cv2.imread("9.9in_camera_landscape.jpg", cv2.IMREAD_UNCHANGED)           

    #Convert that RGB image to HSV
    frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)                     
    #Create a binary image where all pixels in the HSV range are white and the rest black
    frameInRange = cv2.inRange(frameHSV, minHSVShirt, maxHSVShirt)          

    #Put a point at points that are at the periphery of the white shape
    contours, hierarchy = cv2.findContours(frameInRange, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    #find the biggest shape
    areas = [cv2.contourArea(c) for c in contours]
    max_index = np.argmax(areas)
    cnt=contours[max_index]
    #Draw contours of the biggest shape
    cv2.drawContours(frame, [cnt], -1, (0, 252, 0), 3, 8)

    #Approximate a rectangle given the contour points
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    #Calculating Distance
    (x, y), (width, height), angle = rect
    if (width > height):
        angle = angle - 90
        width, height = height, width
    print("Height of image: " + str(height))
    DistZ = (8.046355677641872 - (height * pixelsPerInch)) + 8.046355677641872
    print("The object is: " + str(DistZ) + " in away from you")
    print("The angle is: " + str(angle))

    #Draw 'em
    cv2.drawContours(frame, [box], 0, (0, 0, 255), 3, 8)

    #Find the center of the rectangle
    M = cv2.moments(box)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])

    #Draw the circle
    cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)

    #Save the following images with names specified in ""
    cv2.imwrite("InRange.jpg", frameInRange)
    cv2.imwrite("ImagingOutput.jpg", frame)                               
