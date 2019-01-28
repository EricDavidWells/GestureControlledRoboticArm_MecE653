#include <Servo.h>
#include <Wire.h>

Servo Shoulder;
Servo Elbow;
Servo Hand;

double accelPitch, accelRoll;
long acc_x, acc_y, acc_z;
long scaleFactor = 8192; // 2g --> 16384 , 4g --> 8192 , 8g --> 4096, 16g --> 2048
double accel_x, accel_y, accel_z;

int Shoulderpos = 1200;
int Elbowpos = 1200;
int Handpos = 3000;

// Declare some variables
const int FSR_PIN[] = {0, 1, 2, 3, 4, 5, 6, 7};

const float VCC = 4.98;
const float R_DIV = 5100.0;

int fsrADC;
float force[8];
float fsrV;
float fsrR;
float fsrG;

String label = "foo\n";
String incomingString;
int dataCount = 0;

int y;

void setup(){
  // Set up serial and pin mode
  Serial.begin(115200);
  Serial.setTimeout(3);
  for (int i=0;i<8;i++){
  pinMode(FSR_PIN[i], INPUT);
  }

  Shoulder.attach(5);
  Elbow.attach(4);
  Hand.attach(11);

  Shoulder.writeMicroseconds(Shoulderpos);
  Elbow.writeMicroseconds(Elbowpos);
  Hand.writeMicroseconds(Handpos);

  setup_mpu_6050_registers();
//
//  pinMode(14, OUTPUT);
//  pinMode(15, OUTPUT);
//  digitalWrite(14, LOW);
//  digitalWrite(15, HIGH);
}


void loop(){
  // Read the raw acc data from MPU-6050
  read_mpu_6050_data();

  // Convert acceleration to g force
  accel_x = (double)acc_x / (double)scaleFactor;
  accel_y = (double)acc_y / (double)scaleFactor;
  accel_z = (double)acc_z / (double)scaleFactor;

  // Find pitch and roll from accelerometer
  accelPitch = atan2(accel_y, accel_z) * RAD_TO_DEG;
  accelRoll = atan2(accel_x, accel_z) * RAD_TO_DEG;
//Serial.println(accelPitch);

  // Map servo value
//  Elbowpos = map(accelPitch,0,-180,500,3000);

  if (accelPitch >= -80){
    Elbowpos = 1150;
  }
  else{
    Elbowpos = 2650;
  }

if (Serial.available() > 0) {
                // read the incoming byte:
  incomingString = Serial.readString();
    if (incomingString.toInt() > 20){
      dataCount = incomingString.toInt();
    }
    else if (incomingString == "a\n") {
      dataCount = 1;
    }
    else if (incomingString.startsWith("s") == true){
      incomingString.remove(0,1);
      y = incomingString.toInt();
    }
    else {
       label = incomingString;
    }
  }

   if (y == 1){
     Shoulderpos += 1;
   }
   else if (y == 2){
     Shoulderpos -= 1;
   }
  if(y == 3){
    Handpos += 1;
  }
  else if(y == 0){
    Handpos -= 1;
//    Elbowpos = 1200;
//    Shoulderpos = 1200;
  }
//  else if(y == 1){
//    Elbowpos += 1;
//  }
//  else if (y == 2){
//    Elbowpos -= 1;
//  }

//  Serial.print(Shoulderpos);
//  Serial.print('\t');
//  Serial.print(Elbowpos);
//  Serial.print('\t');
//  Serial.print(Handpos);
//  Serial.print('\n');

  Shoulderpos = constrain(Shoulderpos, 500, 2000);
  Elbowpos = constrain(Elbowpos, 500, 2000);
  Handpos = constrain(Handpos, 1000, 3000);

  Shoulder.writeMicroseconds(Shoulderpos);
  Elbow.writeMicroseconds(Elbowpos);
  Hand.writeMicroseconds(Handpos);

while (dataCount > 0){
  for (int i=0; i<8;i++){
      // Read pin
    fsrADC = analogRead(FSR_PIN[i]);

    // Use ADC reading to calculate voltage:
    fsrV = fsrADC * VCC / 1023.0;

    // Use voltage and static resistor value to calculate FSR resistance:
    fsrR = ((VCC - fsrV) * R_DIV) / fsrV;

    // Guesstimate force based on slopes in figure 3 of FSR datasheet (conductance):
    fsrG = 1.0 / fsrR;

    // Break parabolic curve down into two linear slopes:
    if (fsrR <= 600)
      force[i] = (fsrG - 0.00075) / 0.00000032639;
    else
      force[i] =  fsrG / 0.000000642857;
    }

float aveforce = 0;
  // Display data [in grams] and add small pause
    for (int i=0; i<8; i++){
        Serial.print(force[i],1);
        Serial.print(',');
        aveforce += force[i];
    }
    aveforce = aveforce/8;
    Serial.print(aveforce,1);
    Serial.print(',');
    Serial.print(label);
//    Serial.println();

    dataCount -= 1;
}
}


void read_mpu_6050_data() {
  //Subroutine for reading the raw accelerometer data
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);
  Wire.endTransmission();
  Wire.requestFrom(0x68, 6);

  // Read data
  while (Wire.available() < 6);
  acc_x = Wire.read() << 8 | Wire.read();
  acc_y = Wire.read() << 8 | Wire.read();
  acc_z = Wire.read() << 8 | Wire.read();
}


void setup_mpu_6050_registers() {
  //Activate the MPU-6050
  Wire.beginTransmission(0x68);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();

  //Configure the accelerometer
  Wire.beginTransmission(0x68);
  Wire.write(0x1C);
  Wire.write(0x08); // 2g --> 0x00, 4g --> 0x08, 8g --> 0x10, 16g --> 0x18
  Wire.endTransmission();
}
