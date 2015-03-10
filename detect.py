import cv2
import sys

def findfaces(grayframe):
    return faceCascade.detectMultiScale(
                grayframe,
                scaleFactor=1.1, 
                minNeighbors=5,
                minSize=(60, 60),
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )


def findeyes (grayframe):
    return eyesCascade.detectMultiScale(
                    grayframe,
                    scaleFactor=1.3,
                    minNeighbors=5,
                    minSize=(20, 20),
                    flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                )

def disp(frame, faces, eyes):
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
    return (width/2, height/2)

def offset(centers, elements):
    xoff = list()
    yoff = list()
    for (x, y, w, h) in elements:
        xoff = xoff + [x+(w/2)-centers[0]]
    for (x, y, w, h) in elements:
        yoff = yoff + [y+(h/2)-centers[1]]
    return zip(yoff,xoff)

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
    Only instruct motor to turn if offset > x
    '''
    L = list()
    for i in range(len(offset)):
        if len(offset[i]) > 0:
            if abs(offset[i][0]) > 30 or abs(offset[i][1]) > 30:
                L = L + [offset[i]]
    if L != list (): return L

def main(a_intvl,width, height, display):
    # Create the haar cascade
    global faceCascade
    global eyesCascade
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eyesCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    print(width)
    print(height)
    w = width
    h = height

    vid = cv2.VideoCapture(0)
    vid.set(3,w) # Defines video width
    vid.set(4,h) # Defines video height

    # Set counter
    # (Frames will only be analysed if analyse = 1)
    analyse = 1

    # Run code until user quits
    while True:

        # Capture frame-by-frame
        ret, frame = vid.read()

        if analyse == 1: # If frame is to be analysed

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
            if f: print f

            analyse += 1

        # Increase / Reset counter
        elif analyse <= a_intvl: analyse += 1; 
        else: analyse -= a_intvl;


        # Draw a rectangle around the faces and eyes
        disp(frame, faces, eyes)

        # Display the resulting frame

        if display:
            cv2.imshow('Video', frame)

        # Quit loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    try: a_intvl = (int(sys.argv[1]))
    except: a_intvl = int(raw_input("Analyse interval ? "))
    try: display = bool(int(sys.argv[2]))
    except: display = bool(int(raw_input("Display ? (Y=1 / N=0) ")))
    try: width = (int(sys.argv[3]))
    except: width = 600
    try: height = (int(sys.argv[4]))
    except: height = 480

    main(a_intvl, width, height, display)

