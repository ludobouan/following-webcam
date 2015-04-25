####################
# Localistion d'objet par analyse d'image
# Ludovic Bouan et Thomas Lefort
# TIPE 2015 - ECAM Lyon
####################


# Importer les modules et bibliotèques nécessaires
import sys
import serial
import cv2

# Paramêtres de connexion avec le port serial
ser = serial.Serial('COM3', 115200)



########### FONCTIONS ##########

def findfaces(grayframe):
    '''
    Description: Trouve les visages dans l'image
    -----------------------------------------
    Entrée: Image en nuances de gris
    Sortie: Liste des visages (liste de tuples: (x, y, largeur, hauteur))
    -----------------------------------------
    '''
    return faceCascade.detectMultiScale(
                grayframe,                          # Image à analyser
                scaleFactor=1.2,                    # Facteur d'agrandissement
                minNeighbors=5,                     # Nombre minimale de voisins
                minSize=(60, 60),                   # Taille minimum d'un visage
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE    # Fichier cascade
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
                grayframe,                          # Image à analyser
                scaleFactor=1.3,                    # Facteur d'agrandissement
                minNeighbors=5,                     # Nombre minimale de voisins
                minSize=(20, 20),                   # Taille minimum d'un visage
                flags=cv2.cv.CV_HAAR_SCALE_IMAGE    # Fichier cascade
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
    # Si il n'y a pas de visages
    if len(faces) == 0:
        # Encadrer en jaune tout les yeux detectés (le cadre fait 2 pixels d'épaisseur)
        for(ex,ey,ew,eh) in eyes:
            cv2.rectangle(frame,(ex,ey),(ex+ew,ey+eh),(255,255,0),2)

    #Si il y a des visages
    else :
        # Encadrer en vert tout les yeux detectés
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            roi_color = frame[y:y+h, x:x+w]

        # Encadrer en jaune tout les yeux detectés
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
    # Creer des listes vides
    xoff = list()
    yoff = list()

    # Pour chaque element, calculer la difference entre son centre et le centre de la video en x puis en y
    for (x, y, w, h) in elements:
        xoff = xoff + [x+(w/2)-centers[0]]
        yoff = yoff + [y+(h/2)-centers[1]]

    # Renvoyer une liste de tuple dans lequel le ieme tuple contient le ieme element de xoff et le ieme element de yoff
    return zip(xoff,yoff)

def mvt_filter(offset):
    '''
    Description: Renvoi le decalage seulement si il est assez important
    ----------------------------------------
    Entrée: Décalage (liste de tuples)
    Sortie: Décalage (liste de tuples) ou rien
    ----------------------------------------
    '''
    # Creer une liste vide
    L = list()
    
    # Pour chaque élément dans la list offset
    for i in range(len(offset)):
        if len(offset[i]) > 0:
            # Si le décalage en x de cet element est superieur à 10, rt1 prend la valeur de ce décalage, sinon 0
            if abs(offset[i][0]) > 10: rt1 = offset[i][0]
            else: rt1 = 0
            # Si le décalage en y de cet element est superieur à 10, rt2 prend la valeur de ce décalage, sinon 0
            if abs(offset[i][1]) > 10: rt2 = offset[i][1]
            else: rt2 = 0
            
            # Si rt1 ou rt2 different de 0, ajouter ce couple à la liste L
            if rt1 != 0 or rt2 != 0: L = L + [(rt1,rt2)]

    if L != list(): return L

def send_arduino(instructions):
    '''
    Description: Etablie la connection avec le port serial et envoi le string fourni
    ----------------------------------------
    Input: Instructions (string)
    Output: Serial
    ----------------------------------------
    '''
    ser.write(instructions+"\n")
    


########## BOUCLE PRINCIPALE ##########

def main(a_intvl,width, height, display, angle1, angle2):

    # Faire des cascades des variables globales
    global faceCascade
    global eyesCascade

    # Importer les haarcascades
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    eyesCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    # Définir la constante de proportionalité k
    # Cette valeur est obtenu expérimentalement
    k = 0.0432

    # Capturer la vidéo
    vid = cv2.VideoCapture(0)

    # Définir les dimensions de la vidéo
    vid.set(3,width)
    vid.set(4,height)

    # Défini le compteur
    analyse = 1

    # Boucle infini (interrompu par l'utilisateur par la touche 'Q')
    while True:

        # Lire la video image par image
        ret, frame = vid.read()

        # Si l'image est à analyser
        if analyse == 1:

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

            # Definir f comme la liste des décalages seulement si le décalage est assez important
            f = mvt_filter(offset(center(width, height), faces))

            # Si f existe
            if f: 

                ##### Methode 2 #####
                #Selon le signe du decalage, diminuer ou augmenter l'angle
#                if f[0][0] > 0: angle1 -= 10
#                elif f[0][0] < 0: angle1 += 10

                ##### Methode 1 #####
                # Calculer de la moyenne des décalages horizontaux
                # Multiplier cette moyenne par k
                # Arrondir ce resultat et la soustraire a l'angle du moteur 
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

        # Encadrer les éléments détectés
        disp(frame, faces, eyes)

        # Afficher l'image analysée
        if display:
            cv2.imshow('Video', frame)

        # Quitter la boucle quand la touche 'Q' est enfoncée
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Quand tout est fini, fermer l'affichage et libérer la mémoire
    ser.close()
    video_capture.release()
    cv2.destroyAllWindows()


########## INITIALISATION ##########

if __name__ == "__main__":
    
    # Prendre ou demander les variables d'initialisation
    try: a_intvl = (int(sys.argv[1]))
    except: a_intvl = int(raw_input("Analyse interval ? "))
    try: display = bool(int(sys.argv[2]))
    except: display = bool(int(raw_input("Display ? (Y=1 / N=0) ")))
    # Prendre par defaut 480x640 comme dimension de la video
    try: width = (int(sys.argv[3]))
    except: width = 640
    try: height = (int(sys.argv[4]))
    except: height = 480
    angle1 = 90
    angle2 = 115
    ser.write(str(angle1)+','+str(angle2)+"\n")


    main(a_intvl, width, height, display, angle1, angle2)
