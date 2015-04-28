#include <Servo.h> 

int octetReception=0;
long nombreReception=0;

const int posMin=500;
const int posMax=2300;

const int brocheServo1=10; 
const int brocheServo2=9;

Servo servo1;
Servo servo2;

int angleServo1=0;
int angleServo2=0;

void setup() {
  Serial.begin(115200);
  servo1.attach(brocheServo1, posMin, posMax); 
  servo2.attach(brocheServo2, posMin, posMax); 
}

void loop() {
  while (Serial.available()>0) {
    octetReception=Serial.read();
    if (octetReception==10 || octetReception==44) {
      Serial.print ("Nombre recu = ");
      Serial.println (nombreReception);
      if (octetReception==44){
        angleServo1=nombreReception;
      }
      else{
        angleServo2=nombreReception;
      }
      servo2.write(angleServo2);
      servo1.write(angleServo1);
      nombreReception=0;
      delay(10);
      break;
    }
    else {
      octetReception=octetReception-48;     
      if ((octetReception>=0)&&(octetReception<=9)) 
      nombreReception = (nombreReception*10)+octetReception;
      else Serial.println("La chaine n'est pas un nombre valide !");
      delay(1);
    }
  }
}
