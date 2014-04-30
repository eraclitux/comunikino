/*############     Comunikino's firmware ver. 0.1 ###########

  Copyright(c) 2011 Andrea Masi - www.eraclitux.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <LiquidCrystal.h>
#include <Servo.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);            // LCD 4bit mode
Servo myservo;
                                                  // Custom chars
byte heart[8] = {
  0x0,
  0xa,
  0x1f,
  0x1f,
  0xe,
  0x4,
  0x0,
  0x0
};
boolean newMessage=0;                             // New message flag

void setup() {
                                                  // set up Servo
      myservo.attach(10);
      myservo.write(10);                          // Flag up
      delay(500);
                                                  // set up Buttons
      pinMode(A0,INPUT);                          // YES button
      digitalWrite(A0, HIGH);
      pinMode(A1,INPUT);                          // NO button
      digitalWrite(A1, HIGH);
      pinMode(A2,INPUT);                          // HEARTHBEAT button
      digitalWrite(A2, HIGH);
                                                  // set up Serial
      Serial.begin(9600);
                                                  // set up LCD
      pinMode(A5,OUTPUT);                         // LCD backligth
      digitalWrite(A5, LOW);
      lcd.begin(16, 2);
      lcd.createChar(0, heart);
      splashScreen();
      myservo.write(95);                          // Flag down
}

void loop () {
      checkNewmessage();
      checkButton();
}
void splashScreen() {
      digitalWrite(A5, HIGH);
      delay(1500);
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print("Comunikino");
      lcd.setCursor(0,1);
      lcd.print("by Eraclitux");
      delay(3000);
      lcd.clear();
      digitalWrite(A5, LOW);
}
void checkButton() {                              // Why not using interrupts? Mah!...
      if (digitalRead(A0)==LOW && newMessage==1) {
        sendYes();
        delay(2000);                              // Debounce
        digitalWrite(A5,LOW);
        lcd.clear();
        newMessage=0;
        myservo.write(95);                        // Flag down. Avoiding endpoints (0 and 180) eliminates servo' flickering.
        return;
      }
      if (digitalRead(A1)==LOW && newMessage==1) {
        sendNo();
        delay(2000);                              // Debounce
        digitalWrite(A5,LOW);
        lcd.clear();
        newMessage=0;
        myservo.write(95);                        // Flag down. Avoiding endpoints (0 and 180) eliminates servo' flickering.
        return;
      }
      if (digitalRead(A2)==LOW) {
        sendHeartbeat();
        delay(2500);                              // Debounce
        digitalWrite(A5,LOW);
        lcd.clear();
        newMessage=0;
        myservo.write(95);                        // Flag down. Avoiding endpoints (0 and 180) eliminates servo' flickering.
        return;
      }
}
void printMessage() {
       char l;
       lcd.clear();
       lcd.setCursor(0,0);
       for (char i = 0; i < 16; i++) {
           l=Serial.read();
           if (l != -1 ) {
             if (l =='#') {                       // we have received the whole mail's subject
               newMessage=1;
               return;
             }
             lcd.print (l);
             delay(150);
          }
      }
      lcd.setCursor(0,1);
      for (char i = 0; i < 16; i++) {
          l=Serial.read();
          if (l != -1 ) {
             if (l =='#') {                       // we have received the whole mail's subject
               newMessage=1;
               return;
             }
             lcd.print (l);
             delay(150);
          }
       }
}
void checkNewmessage() {
      if (Serial.available() > 0) {
          lcd.clear();
          myservo.write(10);                      // Flag up. Avoiding endpoints (0 and 180) eliminates servo' flickering.
          blinkBacklight();
          delay(2000);                            // let's create suspance!
          printMessage();
          delay(500);                             // debugg
          blinkLcd(1);
          delay(50);                              // debugg
          Serial.flush();                         // debugg
          newMessage=1;
      }
}

void blinkLcd (char times) {
      for (char i = 0; i < times; i++) {
          lcd.noDisplay();
          delay(500);
          lcd.display();
          delay(500);
      }
}
void blinkBacklight() {
      digitalWrite(A5,HIGH);
      delay(400);
      digitalWrite(A5,LOW);
      delay(400);
      digitalWrite(A5,HIGH);
      delay(400);
      digitalWrite(A5,LOW);
      delay(400);
      digitalWrite(A5,HIGH);
      delay(400);
}
void sendYes() {
      Serial.print("Y\n");
      delay(5);
      lcd.clear();
      delay(5);
      lcd.setCursor(0,0);
      lcd.print("Sending --> YES ");
}
void sendNo() {
      Serial.print("N\n");
      delay(5);
      lcd.clear();
      delay(5);
      lcd.setCursor(0,0);
      lcd.print("Sending --> NO ");
}
void sendHeartbeat() {
      Serial.print("B\n");
      delay(5);
      lcd.clear();
      digitalWrite(A5,HIGH);
      delay(10);
      lcd.setCursor(0,0);
      lcd.print("Sending --> ");
      lcd.write(0);
}
