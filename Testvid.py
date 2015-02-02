import cv2
import sys

def get_faces(rtnfaces, rtneyes, display):
    # Create the haar cascade
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eyesCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    vid = cv2.VideoCapture(0)
    vid.set(3,640) # Defines video width
    vid.set(4,480) # Defines video height

    # Set counter
    # (Frames will only be analysed if analyse = 1)
    analyse = 1

    # Run code until user quits
    while True:

        # Capture frame-by-frame
        ret, frame = vid.read()

        if analyse == 1: # If frame is to be analysed

            # Make greyscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Find faces in image
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1, 
                minNeighbors=5,
                minSize=(60, 60),
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )

            # If there are no faces in frame, search for eyes
            if len(faces) == 0:
                eyes = eyesCascade.detectMultiScale(
                    gray,
                    scaleFactor=1.3,
                    minNeighbors=5,
                    minSize=(20, 20),
                    flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                )

            # If there are faces in frame, search for eyes on faces
            else:
                for (xf, yf, wf, hf) in faces:
                    roi_gray = gray[yf:yf+hf, xf:xf+wf]
                    eyes = eyesCascade.detectMultiScale(
                        roi_gray,
                        scaleFactor=1.3,
                        minNeighbors=8,
                        minSize=(20, 20),
                        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
                    )

            # Print the coordinates of the faces
            if rtnfaces == True:
                for (xf, yf, wf, hf) in faces:
                    print(xf, yf, wf, hf)
            if rtneyes == True:
                for (xe,ye,we,he) in eyes:
                    print(xe, ye, we, he)

            analyse += 1

        # Increase / Reset counter
        elif analyse <= 10: analyse += 1; 
        else: analyse -= 10; 


        # Draw a rectangle around the faces and eyes
        if len(faces) == 0:
            for(ex,ey,ew,eh) in eyes:
                cv2.rectangle(frame,(ex,ey),(ex+ew,ey+eh),(255,255,0),2)
        else :
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                roi_color = frame[y:y+h, x:x+w]
                for(ex,ey,ew,eh) in eyes:
                    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(255,255,0),2)

        # Display the resulting frame
        if display == True:
            cv2.imshow('Video', frame)

        # Quit loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    rtnfaces = bool(sys.argv[1])
    rtneyes = bool(sys.argv[2])
    display = bool(sys.argv[3])

    get_faces(rtnfaces, rtneyes, display)

