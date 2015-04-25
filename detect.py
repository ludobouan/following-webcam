import cv2
import sys
import serial
ser = serial.Serial('COM3', 115200) # Parametres de connexion avec le port serial

def findfaces(grayframe):
    '''
    Description: Trouve les visages dans l'image
    -----------------------------------------
    Entrée: Image en nuances de gris
    Sortie: Liste des visages (liste de tuples: (x, y, largeur, hauteur))
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
    Description: Trouve les yeux dans l'image
    ----------------------------------------
    Entrée: Image en nuance de gris
    Sortie: Liste des yeux (liste de tuples: (x, y, largeur, hauteur))
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
    Description: Encadre les élements détectés
    ----------------------------------------
    Entrée: Image
            Liste des visages (liste de tuples: (x, y, largeur, hauteur))
            Liste des yeux (liste de tuples: (x, y, l, h))
    Sortie: Image avec visages encadrés en vert
            et les yeux encadrés en jaune
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
    Description: Trouve le centre de la video
    ----------------------------------------
    Entrée: largeur (int); hauteur (int)
    Sortie: tuple du center (x,y)
    ----------------------------------------
    '''
    return (width/2, height/2)

def offset(centers, elements):
    '''
    Description: Trouve le decalage etre le centre et les elements
    ----------------------------------------
    Entrée: Centres (tuple); Elements (liste de tulpes)
    Sortie: Liste de decalages (liste de tuples)
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

def mvt_filter(offset):
    '''
    Description: Renvoi le decalage seulement si il est assez important
    ----------------------------------------
    Entrée: Decalage (liste de tuples)
    Sortie: Decalage (liste de tuples) ou rien
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
    '''
    Description: Etabli la connection avec le port serial et envoi le string fourni
    ----------------------------------------
    Input: Instructions (string)
    Output: Serial
    ----------------------------------------
    '''
    ser.write(instructions+"\n")

def main(a_intvl,width, height, display, angle1, angle2):
    # Importer les haar-cascades
    global faceCascade
    global eyesCascade
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eyesCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    k = 0.074794 #
    print(width)
    print(height)


    vid = cv2.VideoCapture(0)
    vid.set(3,w) # Defini la largeur de la video
    vid.set(4,h) # Defini la hauteur de la video

    # Defini le compteur
    # (Les images sont analysé seulement si analyse = 1)
    analyse = 1

    # Boucle infini (interrompu par l'utilisateur par la touche 'q')
    while True:

        # Capturer la video image par image
        ret, frame = vid.read()

        if analyse == 1: # Si l'image est à analysé
            
            # Faire une copie de l'image en nuances de gris
            grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Trouver les visages
            faces = findfaces(grayframe)

            # Si il n'y a pas de visages, chercher les yeux dans toute l'image
            if len(faces) == 0:
                eyes = findeyes(grayframe)

            # Si il y a des visages, chercher les yeux dans le cadre des visages
            else:
                for (xf, yf, wf, hf) in faces:
                    fsection_grayframe = grayframe[yf:yf+hf, xf:xf+wf]
                    eyes = findeyes(fsection_grayframe)

            f = mvt_filter(offset(center(w, h), faces))
            if f: 
                # Methode 2
#                if f[0][0] > 0: angle1 -= 10
#                elif f[0][0] < 0: angle1 += 10
                
                # Methode 1
                angle1 -= int(k*(sum([f[n][0] for n in range(len(f))])/len(f)))              
                instructions = str(angle1)

                # Methode 2
#                if f[0][1] > 0: angle2 += 4
#                elif f[0][1] < 0: angle2 -= 4

                # Methode 1
                angle2 += int(k*(sum([f[n][1] for n in range(len(f))])/len(f)))
                instructions = instructions + ',' + str(angle2)

                send_arduino(instructions)
                print(instructions)
        
            analyse += 1
        
        # Augmenter / Remettre à 0 la variable compteur
        elif analyse <= a_intvl: analyse += 1; 
        else: analyse -= a_intvl;

        # Encadrer les elements detectés
        disp(frame, faces, eyes)

        # Afficher l'image analysée
        if display:
            cv2.imshow('Video', frame)

        # Quitter la boucle quand la touche 'q' est enfoncée
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Quand tout est finie, fermer l'affichage et detruire les variables
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
