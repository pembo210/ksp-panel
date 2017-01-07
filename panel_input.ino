/*
 * Maybe make polling switches be a function
 */

// Pin variables
int throttlePot = A0;

int abortPush = 1;
int stagePush = 2;
int timewarpUpPush = 3;
int timewarpDownPush = 4;

int sasToggle = 5;
int rcsToggle = 6;

// State variables
int sasCurrent = HIGH;
int rcsCurrent = HIGH;

int sasLast = HIGH;
int rcsLast = HIGH;

int throttle = 0;

void setup() {  
  pinMode(abortPush, INPUT_PULLUP);
  pinMode(stagePush, INPUT_PULLUP);
  pinMode(timewarpUpPush, INPUT_PULLUP);
  pinMode(timewarpDownPush, INPUT_PULLUP);
  pinMode(sasToggle, INPUT_PULLUP);
  pinMode(rcsToggle, INPUT_PULLUP);

  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);
}

void loop() {  
  if (digitalRead(abortPush) == LOW) {Joystick.button(1, 1);}
  if (digitalRead(abortPush) == HIGH) {Joystick.button(1, 0);}

  if (digitalRead(stagePush) == LOW) {Joystick.button(2, 1);}
  if (digitalRead(stagePush) == HIGH) {Joystick.button(2, 0);}

  if (digitalRead(timewarpUpPush) == LOW) {Joystick.button(3, 1);}
  if (digitalRead(timewarpUpPush) == HIGH) {Joystick.button(3, 0);}

  if (digitalRead(timewarpDownPush) == LOW) {Joystick.button(4, 1);}
  if (digitalRead(timewarpDownPush) == HIGH) {Joystick.button(4, 0);}

  sasCurrent = digitalRead(sasToggle);
  rcsCurrent = digitalRead(rcsToggle);

  if (sasCurrent != sasLast) {
    Joystick.button(5, 1);
    delay(10);
    Joystick.button(5, 0);
  }

  if (rcsCurrent != rcsLast) {
    Joystick.button(6, 1);
    delay(10);
    Joystick.button(6, 0);
  }

  //throttle = analogRead(throttlePot);
  //Joystick.sliderLeft(throttle);
  
  sasLast = sasCurrent;
  rcsLast = rcsCurrent;

  delay(50);
}
