import cv2

imagePath = 'testimg.jpg'

# Create the haar cascade
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eyesCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

analyse = 1
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    if analyse == 1:

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #equalizeHist(gray,gray)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        if len(faces) == 0:
            eyes = eyesCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=8,
                minSize=(20, 20),
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )

        else:
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                eyes = eyesCascade.detectMultiScale(roi_gray)

        for (x, y, w, h) in faces:
            print(x, y, w, h)
        analyse += 1

    elif analyse <= 10: analyse += 1; #print(analyse)
    else: analyse -= 10; #print(analyse)

        # Draw a rectangle around the faces
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
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()