#include <Servo.h>

Servo shoulder;
Servo elbow;
Servo wrist;
Servo hand;

// Servo 1 range: // 500-2300, 500 right
// Servo 2 range: //1000-2000, 
// Servo 3 range: //500-1200, 1200 extended
// Servo 4 range: // 800-1800, closed

int shoulder_pos = 1500;
int elbow_pos = 1500;
int wrist_pos = 1500;
int hand_pos = 1500;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  shoulder.attach(2);
  elbow.attach(9);
  wrist.attach(4);
  hand.attach(5);

}

void loop() {
  // put your main code here, to run repeatedly:


 if (Serial.available() > 0) {
    char buf[9];
    int len = Serial.readBytesUntil('\n', buf, 8);
    Serial.print(buf[0]);
    Serial.print(',');
    Serial.print(buf[1]);
    Serial.print(',');
    Serial.print(buf[2]);
    Serial.print(',');
    Serial.print(buf[3]);
    Serial.print(',');
    Serial.print(buf[4]);
    Serial.print(',');
    Serial.println(len);

    if (buf[0] == 'p'){
      shoulder_pos = buf[1]*256 + buf[2];
      elbow_pos = buf[3]*256 + buf[4];
      wrist_pos = buf[5]*256 + buf[6];
      hand_pos = buf[7]*256 + buf[8];

      elbow_pos = int(buf[1]-48)*1000 + int(buf[2]-48)*100;
    }
  }

shoulder.writeMicroseconds(shoulder_pos); 
elbow.writeMicroseconds(elbow_pos); 
wrist.writeMicroseconds(wrist_pos);
hand.writeMicroseconds(hand_pos);

Serial.print(shoulder_pos);Serial.print(',');
Serial.print(elbow_pos);Serial.print(',');
Serial.print(wrist_pos);Serial.print(',');
Serial.print(hand_pos);Serial.print('\n');

}
