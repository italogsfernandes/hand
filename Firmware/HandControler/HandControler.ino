/*                   #
                    ###
                   #####
                  #######
                 #########
                ##### #####
               #####   #####
       #      #####  #  #####      #
      ###    #####  ###  #####    ###
     #####  #####  #####  #####  #####
    #####  #####  #######  #####  #####
   #####  #######  #####  #######  #####
  #####  #########  ###  #########  #####
  #####  ##### #####  #  ##### #####  #####
  ###  #####   #####   #####   #####  ###
   #  #####     ##### #####     #####  #
     #####       #########       #####
      ###         #######         ###
       #           #####           #
                    ###
                     #
********************************************
*                                          *
                Project Name
     Connected Prosthetic Hand Project
*                                          *
                Gaetan Davout
*                                          *
********************************************/

//-------------------------------------------------------------
//-------------         Initialization           --------------
//-------------------------------------------------------------
#include <Servo.h>

enum { THUMB, INDEX, MIDDLEFINGER, RINGFINGER, PINKY, WRIST};

Servo servothumb;           // Define thumb servo
Servo servoindex;           // Define index servo
Servo servomiddlefinger;    // Define majeure servo
Servo servoringfinger;      // Define ringfinger servo
Servo servopinky;           // Define pinky
Servo servowrist;           // Define wrist /!8 DONT USE THIS WITH the Black hand

// Define the inferior limit of the angle of each servo
const int LIMIT_INF_THUMB = 0;
const int LIMIT_INF_INDEX = 0;
const int LIMIT_INF_MIDDLEFINGER = 0;
const int LIMIT_INF_RINGFINGER = 0;
const int LIMIT_INF_PINKY = 0;
const int LIMIT_INF_WRIST = 0;

// Define the superior limit of the angle of each servo
const int LIMIT_SUP_THUMB = 120;         // 120
const int LIMIT_SUP_INDEX = 150;         // 150
const int LIMIT_SUP_MIDDLEFINGER = 110;  // 110
const int LIMIT_SUP_RINGFINGER = 120;    // 120
const int LIMIT_SUP_PINKY = 0;           // ?
const int LIMIT_SUP_WRIST = 0;           // ?

// Define the speed of each servo
const float SERVO_SPEED_THUMB = 0;
const float SERVO_SPEED_INDEX = 0;
const float SERVO_SPEED_MIDDLEFINGER = 0;
const float SERVO_SPEED_RINGFINGER = 0;
const float SERVO_SPEED_PINKY = 0;
const float SERVO_SPEED_WRIST = 0;

// Define the pin of the LED
const int LED_WRIST =  2;
const int LED_R =  4;
const int LED_L =  7;

// Define the pin of the LASER
const int LASER =  8;
const char LASERINSTRUCTION =  'L';

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(25); //parce que oui

  // attach servos
  servothumb.attach(11);          // Set thumb servo to digital pin 11        - Red
  servoindex.attach(10);          // Set index servo to digital pin 10        - Orange
  servomiddlefinger.attach(9);    // Set middlefinger servo to digital pin 9  - Yellow
  servoringfinger.attach(6);      // Set ringfinger servo to digital pin 6    - Green
  servopinky.attach(5);           // Set pinky servo to digital pin 5         - Blue
  //servowrist.attach(3);         // Set pinky servo to digital pin 3         - Violet

  // Set the digital pin of the LEDs and LASER as output
  pinMode(LED_WRIST, OUTPUT);
  pinMode(LED_R, OUTPUT);
  pinMode(LED_L, OUTPUT);
  pinMode(LASER, OUTPUT);

  // Initialize the LASER and the LEDs
  digitalWrite(LED_WRIST, HIGH);
  digitalWrite(LED_R, HIGH);
  digitalWrite(LED_L, HIGH);
  digitalWrite(LASER, LOW);

  servothumb.write(0);
  servoindex.write(0);
  servomiddlefinger.write(0);
  servoringfinger.write(0);
  servopinky.write(0);
  digitalWrite(LASER, LOW);
}

//-------------------------------------------------------------
//-------------          Main function           --------------
//-------------------------------------------------------------

void loop() {
  if (Serial.available()) {

    /*for(int i = 0; i < 15; i++){ //Clignotement des LED
      if(i%2 == 0){
        digitalWrite(LED_WRIST, HIGH);
        digitalWrite(LED_R, HIGH);
        digitalWrite(LED_L, HIGH);
      } else {
        digitalWrite(LED_WRIST, LOW);
        digitalWrite(LED_R, LOW);
        digitalWrite(LED_L, LOW);
      }
      delay(50);
      }*/

    String servopositions = Serial.readString();
    Serial.println(servopositions);

    if (servopositions.charAt(0) == LASERINSTRUCTION) {
      Serial.println(digitalRead(LASER));
      if (digitalRead(LASER) == 0) {
        digitalWrite(LASER, HIGH);
        Serial.println("Laser on");
      } else {
        digitalWrite(LASER, LOW);
        Serial.println("Laser off");
      }
    } else {// if(servopositions.length() == 14 + 1) { // 14 caracètre + 1 caractère de fin
      serialFlush();
      int servothumbposition = servopositions.substring(0, 2).toInt();
      int servoindexposition = servopositions.substring(3, 5).toInt();
      int servomiddlefingerposition = servopositions.substring(6, 8).toInt();
      int servoringfingerposition = servopositions.substring(9, 11).toInt();
      int servopinkyposition = servopositions.substring(12, 14).toInt();

      Serial.println(servothumbposition);
      Serial.println(servoindexposition);
      Serial.println(servomiddlefingerposition);
      Serial.println(servoringfingerposition);
      Serial.println(servopinkyposition);

      if (servothumbposition >= 0 && servothumbposition <= 90) {
        servothumb.write(servothumbposition);
      } else {
        servothumb.write(0);
      }

      if (servoindexposition >= 0 && servoindexposition <= 90) {
        servoindex.write(servoindexposition);
      } else {
        servoindex.write(0);
      }

      if (servomiddlefingerposition >= 0 && servomiddlefingerposition <= 90) {
        servomiddlefinger.write(servomiddlefingerposition);
      } else {
        servomiddlefinger.write(0);
      }

      if (servoringfingerposition >= 0 && servoringfingerposition <= 90) {
        servoringfinger.write(servoringfingerposition);
      } else {
        servoringfinger.write(0);
      }

      if (servopinkyposition >= 0 && servopinkyposition <= 90) {
        servopinky.write(servopinkyposition);
      } else {
        servopinky.write(0);
      }
    }
    //else {
    // Serial.println("Error Input");
    //}
  }



  /*
    sensorValue = map(analogRead(sensorPin),0,1023,0,120);
    Serial.print("angle = ");
    Serial.print(sensorValue);
    Serial.print("\n");
    if(sensorValue>0 && sensorValue<179) {
    servothumb.write(0);
    servoindex.write(sensorValue);
    servomiddlefinger.write(0);
    servoringfinger.write(0);
    servopinky.write(0);
    }



    sensorValue = map(analogRead(sensorPin),0,1023,0,6);
    Serial.print(sensorValue);
    Serial.print(" => ");
    switch(sensorValue) {
    case 0:
      Serial.print("alltorest\n");
      alltorest();
      delay(1000);
      break;
    case 1:
      Serial.print("point\n");
      point();
      delay(1000);
      break;
    case 2:
      Serial.print("honor\n");
      honor();
      delay(1000);
      break;
    case 3:
      Serial.print("fist\n");
      fist();
      delay(1000);
      break;
    case 4:
      Serial.print("come\n");
      come();
      break;
    case 5:
      Serial.print("moveleft\n");
      moveleft();
      break;
    case 6:
      Serial.print("moveright\n");
      moveright();
      break;
    default:
      alltorest();
      break;
    }

    //*/
}

//-------------------------------------------------------------
//-------------         6 mouvements functions        --------------
//-------------------------------------------------------------


//-------------------------------------------------------------
//-------------         package functions        --------------
//-------------------------------------------------------------

//-------------------------------------------------------------
// Set all functions to rest: stopactivity
void stopactivity() {
  alltorest();
}

//-------------------------------------------------------------
// Motion to set the servo into "rest" position: alltorest
void alltorest() {
  servothumb.write(LIMIT_INF_THUMB);
  servoindex.write(LIMIT_INF_INDEX);
  servomiddlefinger.write(LIMIT_INF_MIDDLEFINGER);
  servoringfinger.write(LIMIT_INF_RINGFINGER);
  servopinky.write(LIMIT_INF_PINKY);
}

//-------------------------------------------------------------
// Motion to set the servo into "max" position: alltomax
void alltomax() {
  servothumb.write(LIMIT_SUP_THUMB);
  servoindex.write(LIMIT_SUP_INDEX);
  servomiddlefinger.write(LIMIT_SUP_MIDDLEFINGER);
  servoringfinger.write(LIMIT_SUP_RINGFINGER);
  servopinky.write(LIMIT_SUP_PINKY);
}


//-------------------------------------------------------------
//-------------        USB mode functions        --------------
//-------------------------------------------------------------


//-------------------------------------------------------------
// Make the forearm move to the right: moveright
void moveright() {
  servoindex.write(120);
  servomiddlefinger.write(120);
  servoringfinger.write(120);
  servopinky.write(120);
  delay(300);
  servothumb.write(LIMIT_SUP_THUMB);
  delay(300);
  servoindex.write(LIMIT_INF_INDEX);
  servomiddlefinger.write(LIMIT_INF_MIDDLEFINGER);
  servoringfinger.write(LIMIT_INF_RINGFINGER);
  servopinky.write(LIMIT_INF_PINKY);
  delay(300);
  servothumb.write(LIMIT_INF_THUMB);
  delay(300);
}

//-------------------------------------------------------------
// Make the forearm move to the left: moveleft
void moveleft() {
  servoindex.write(LIMIT_INF_INDEX);
  servomiddlefinger.write(LIMIT_INF_INDEX);
  servoringfinger.write(LIMIT_INF_INDEX);
  servopinky.write(LIMIT_INF_INDEX);
  delay(300);
  servothumb.write(LIMIT_SUP_THUMB);
  delay(300);
  servoindex.write(120);
  servomiddlefinger.write(120);
  servoringfinger.write(120);
  servopinky.write(120);
  delay(300);
  servothumb.write(LIMIT_INF_THUMB);
  delay(300);
}

//-------------------------------------------------------------
// Make the forearm at the pointer position: point
void point() {
  servothumb.write(LIMIT_SUP_THUMB);
  servoindex.write(LIMIT_INF_INDEX);
  servomiddlefinger.write(LIMIT_SUP_MIDDLEFINGER);
  servoringfinger.write(LIMIT_SUP_RINGFINGER);
  servopinky.write(LIMIT_SUP_PINKY);
  delay(600);
  digitalWrite(LASER, HIGH);
}

//-------------------------------------------------------------
// Close all finger: fist
void fist() {
  alltomax();
}

//-------------------------------------------------------------
// Make the sign to come: come
void come() {
  for (int i = 0; i < 2; i++)
  {
    servoindex.write(LIMIT_SUP_INDEX);
    delay(200);
    servoindex.write(LIMIT_INF_INDEX);
    delay(400);
  }
}

//-------------------------------------------------------------
// Close all finger exept the middle: honor
void honor() {
  servothumb.write(LIMIT_SUP_THUMB);
  servoindex.write(LIMIT_SUP_INDEX);
  servomiddlefinger.write(LIMIT_INF_MIDDLEFINGER);
  servoringfinger.write(LIMIT_SUP_RINGFINGER);
  servopinky.write(LIMIT_SUP_PINKY);
}

void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
} 
