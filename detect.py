import cv2
import sys
import serial
ser = serial.Serial('COM3', 115200) # Establish the connection on a specific port

def findfaces(grayframe):
    '''
    Description: Finds the faces in the frame
    -----------------------------------------
    Input: image in grayscale
    Output: List of tuples (x, y, w, h)
    -----------------------------------------
    '''
    return faceCascade.detectMultiScale(
                grayframe,
                scaleFactor=1.2, 
                minNeighbors=5,
                minSize=(60, 60),
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )


def findeyes (grayframe):
    '''
    Description: Finds the eyes in the frame
    ----------------------------------------
    Input: image in grayscale
    Output: List of tuples (x, y, w, h)
    ----------------------------------------
    '''
    return eyesCascade.detectMultiScale(
                    grayframe,
                    scaleFactor=1.3,
                    minNeighbors=5,
                    minSize=(20, 20),
                    flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                )

def disp(frame, faces, eyes):
    '''
    Description: Draws colored boxes around eyes and faces
    ----------------------------------------
    Input: image; list of tuples of faces (x, y, w, h); list of tuples of eyes (x, y, w, h)
    ----------------------------------------
    '''
    if len(faces) == 0:
        for(ex,ey,ew,eh) in eyes:
            cv2.rectangle(frame,(ex,ey),(ex+ew,ey+eh),(255,255,0),2)
    else :
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            roi_color = frame[y:y+h, x:x+w]
            for(ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(255,255,0),2)

def center(width, height):
    '''
    Description: finds center of video
    ----------------------------------------
    Input: width (int); height (int)
    Output: tuple of center (x,y)
    ----------------------------------------
    '''
    return (width/2, height/2)

def offset(centers, elements):
    '''
    Description: finds offset between center and elements
    ----------------------------------------
    Input: centers (tuple), elements (list of tulpes)
    Output: list of offsets (list of tuples)
    ----------------------------------------
    '''
    xoff = list()
    yoff = list()
    for (x, y, w, h) in elements:
        xoff = xoff + [x+(w/2)-centers[0]]
    for (x, y, w, h) in elements:
        yoff = yoff + [y+(h/2)-centers[1]]
    print(zip(xoff,yoff))
    return zip(xoff,yoff)

def face_filter():
    '''
    Analyses elements in last 10 frames
    Input: elements to add, 
    '''
    #Remove frame(-10)

    #Add frame(0)

    #For each face

def mvt_filter(offset):
    '''
    Description: returns offset if above sensibility threshold
    ----------------------------------------
    Input: offset (list of tuples)
    Output: offset (list of tuples) or None
    ----------------------------------------
    '''
    L = list()
    for i in range(len(offset)):
        if len(offset[i]) > 0:
            if abs(offset[i][0]) > 10: rt1 = offset[i][0]
            else: rt1 = 0
            if abs(offset[i][1]) > 10: rt2 = offset[i][1]
            else: rt2 = 0
            
            if rt1 != 0 or rt2 != 0: L = L + [(rt1,rt2)]

    if L != list(): return L

def send_arduino(instructions):
    ser.write(instructions+"\n")
    #Serial.print(str(angle)+"\n")

def main(a_intvl,width, height, display, angle1, angle2):
    # Create the haar cascade
    global faceCascade
    global eyesCascade
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eyesCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    w = width
    h = height
    k = 0.074794
    print(w)
    print(h)


    vid = cv2.VideoCapture(0)
    vid.set(3,w) # Defines video width
    vid.set(4,h) # Defines video height

    # Set counter
    # (Frames will only be analysed if analyse = 1)
    image = 1

    # Run code until user quits
    while True:

        # Capture frame-by-frame
        ret, frame = vid.read()

        if image = a_intvl: # If frame is to be analysed
            image = 0
            # Make grayscale
            grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Find faces in image
            faces = findfaces(grayframe)

            # If there are no faces in frame, search for eyes
            if len(faces) == 0:
                eyes = findeyes(grayframe)

            # If there are faces in frame, search for eyes on faces
            else:
                for (xf, yf, wf, hf) in faces:
                    fsection_grayframe = grayframe[yf:yf+hf, xf:xf+wf]
                    eyes = findeyes(fsection_grayframe)

            f = mvt_filter(offset(center(w, h), faces))
            if f: 
                
#                if f[0][0] > 0: angle1 -= 10
#                elif f[0][0] < 0: angle1 += 10
                
                angle1 -= int(k*(sum([f[n][0] for n in range(len(f))])/len(f)))              
                instructions = str(angle1)

#                if f[0][1] > 0: angle2 += 4
#                elif f[0][1] < 0: angle2 -= 4
                angle2 += int(k*(sum([f[n][1] for n in range(len(f))])/len(f)))
                instructions = instructions + ',' + str(angle2)

                send_arduino(instructions)
                print(instructions)
            image += l;


        # Draw a rectangle around the faces and eyes
        disp(frame, faces, eyes)

        # Display the resulting frame

        if display:
            cv2.imshow('Video', frame)

        # Quit loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    ser.close()
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try: a_intvl = (int(sys.argv[1]))
    except: a_intvl = int(raw_input("Analyse interval ? "))
    try: display = bool(int(sys.argv[2]))
    except: display = bool(int(raw_input("Display ? (Y=1 / N=0) ")))
    try: width = (int(sys.argv[3]))
    except: width = 640
    try: height = (int(sys.argv[4]))
    except: height = 480
    angle1 = 90
    angle2 = 115
    ser.write(str(angle1)+','+str(angle2)+"\n")


    main(a_intvl, width, height, display, angle1, angle2)
