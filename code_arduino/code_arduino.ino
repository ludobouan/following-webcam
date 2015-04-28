#include <Servo.h> 

int octetReception=0; // Variable qui enregistre les octets entrants 
long nombreReception=0; // Chaine de caractère reçu

const int posMin=500; // Position minimal des servomoteurs
const int posMax=2300; // Position maximal des servomoteurs

const int brocheServo1=10; // Servomoteur 1 connecté sur la broche 10
const int brocheServo2=9; // Servomoteur 2 connecté sur la broche 9

Servo servo1; // Declaration du servomoteur 1
Servo servo2; // Declaration du servomoteur 2

int angleServo1=0; // Declaration de l'angle du moteur 1
int angleServo2=0; // Declaration de l'angle du moteur 2

void setup() { // Initialisation du programme
  Serial.begin(115200); // Initialisation de la connexion par Serial
  servo1.attach(brocheServo1, posMin, posMax); // Initialisation du servomoteur 1
  servo2.attach(brocheServo2, posMin, posMax); // Initialisation du servomoteur 2
}

void loop() { // Boucle principale
  while (Serial.available()>0) { // Boucle permettant de recevoir les données du Serial octet par octet
    octetReception=Serial.read(); // Lecture de l'octet suivant
    if (octetReception==10 || octetReception==44) { // Si l'octet suivant est un retour à la ligne ou une virgule
      Serial.print ("Nombre recu = "); // Affichage du nombre reçu
      Serial.println (nombreReception);
      if (octetReception==44){ // Si une virgule est reçu
        angleServo1=nombreReception; // Le nombre reçu correspond au servomoteur 1
      }
      else{ // Sinon correspond au servomoteur 2
        angleServo2=nombreReception;
      }
      servo2.write(angleServo2); // Envoi des angles aux moteurs
      servo1.write(angleServo1);
      nombreReception=0; // Réinitialisation de la variable d'enregistrement
      delay(10);
      break;
    }
    else { // Sinon l'octet correspond à un chiffre
      octetReception=octetReception-48; // Transformer pour obtenir le chiffre de 0 à 9 
      if ((octetReception>=0)&&(octetReception<=9)) // Vérification pour éviter les erreurs
      nombreReception = (nombreReception*10)+octetReception; // Enregistrement de l'octet dans la variable nombreReception
      else Serial.println("La chaine n'est pas un nombre valide !"); // Afficher en cas d'erreur.
      delay(1);
    }
  }
}
