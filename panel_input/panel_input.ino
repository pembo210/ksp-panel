/*
 * This program drives the input controls of a control panel for the
 * space simulation game Kerbal Space Program (KSP). The inputs consist
 * of lighted pushbuttons, a slide potentiometer, and toggle switches.
 * This code runs on a Teensy acting as a USB joystick, which plugs into
 * the machine running the game and acts as a controller.
 */

// Pin variables
// Potentiometers
int throttlePot = A0;

//Pushbutton
int AG1 = 10;
int AG2 = 9;
int AG3 = 8;
int AG4 = 7;
int AG5 = 6;
int AG6 = 5;
int AG7 = 4;
int AG8 = 3;
int AG9 = 2;
int AG10 = 1;
int abortPush = 11;
int stagePush = 15;

//Toggle switches
int sasToggle = 16;
int rcsToggle = 17;
int gearToggle = 18;
int brakeToggle = 19;
int lightToggle = 20;

// State variables
int sasCurrent = HIGH;
int rcsCurrent = HIGH;
int lightCurrent = HIGH;
int gearCurrent = HIGH;
int brakeCurrent = HIGH;

int sasLast = HIGH;
int rcsLast = HIGH;
int lightLast = HIGH;
int gearLast = HIGH;
int brakeLast = HIGH;

void setup() {  
  pinMode(AG1, INPUT_PULLUP);
  pinMode(AG2, INPUT_PULLUP);
  pinMode(AG3, INPUT_PULLUP);
  pinMode(AG4, INPUT_PULLUP);
  pinMode(AG5, INPUT_PULLUP);
  pinMode(AG6, INPUT_PULLUP);
  pinMode(AG7, INPUT_PULLUP);
  pinMode(AG8, INPUT_PULLUP);
  pinMode(AG9, INPUT_PULLUP);
  pinMode(AG10, INPUT_PULLUP);
  pinMode(abortPush, INPUT_PULLUP);
  pinMode(stagePush, INPUT_PULLUP);
  
  pinMode(sasToggle, INPUT_PULLUP);
  pinMode(rcsToggle, INPUT_PULLUP);
  pinMode(gearToggle, INPUT_PULLUP);
  pinMode(lightToggle, INPUT_PULLUP);
  pinMode(brakeToggle, INPUT_PULLUP);


  pinMode(13, OUTPUT);
  digitalWrite(13, HIGH);
}

void loop() {  
  //Update states of toggles for comparison
  sasCurrent = digitalRead(sasToggle);
  rcsCurrent = digitalRead(rcsToggle);
  lightCurrent = digitalRead(lightToggle);
  gearCurrent = digitalRead(gearToggle);
  brakeCurrent = digitalRead(brakeToggle);

  updatePushbutton(AG1, 1);
  updatePushbutton(AG2, 2);
  updatePushbutton(AG3, 3);
  updatePushbutton(AG4, 4);
  updatePushbutton(AG5, 5);
  updatePushbutton(AG6, 6);
  updatePushbutton(AG7, 7);
  updatePushbutton(AG8, 8);
  updatePushbutton(AG9, 9);
  updatePushbutton(AG10,10);
  updatePushbutton(abortPush, 11);
  updatePushbutton(stagePush, 12);
  
  updateToggle(sasCurrent, sasLast, 13);
  updateToggle(rcsCurrent, rcsLast, 14);
  updateToggle(lightCurrent, lightLast, 15);
  updateToggle(gearCurrent, gearLast, 16); 
  updateToggle(brakeCurrent, brakeLast, 17);
  
  updateSlider(throttlePot);

  //Shift current values to last for comparison
  sasLast = sasCurrent;
  rcsLast = rcsCurrent;
  lightLast = lightCurrent;
  gearLast = gearCurrent;
  brakeLast = brakeCurrent;

  delay(50);
}

void updatePushbutton(int pin, int joystickButton) {
  if (digitalRead(pin) == LOW) {Joystick.button(joystickButton, 1);}
  if (digitalRead(pin) == HIGH) {Joystick.button(joystickButton, 0);}
}

void updateToggle(int current, int last, int joystickButton) {
  if (current != last) {
    Joystick.button(joystickButton, 1);
    delay(10);
    Joystick.button(joystickButton, 0);
  }
}

void updateSlider(int pin) {
  int throttle = analogRead(pin);
  if (throttle < 50) {throttle = 0;}
  Joystick.sliderLeft(throttle);
}

