//Include I2C library and declare variables
#include <Wire.h>

const int selectPins[3] = {2, 3, 4};
int FSR[11];
int temperature;
int acc_x, acc_y, acc_z;
int gyro_x, gyro_y, gyro_z;
unsigned long timer = 0;
long loopTimeMicroSec = 5000;


void setup() {
  // Start I2C and serial port
  Wire.begin();
  Serial.begin(115200);

  // Setup the registers of the MPU-6050
  setupMPU6050();

  // Set up the select pins as outputs for multiplexer
  for (int i=0; i<3; i++){
    pinMode(selectPins[i], OUTPUT);
    digitalWrite(selectPins[i], HIGH);
  }

  // Connect z on multiplexer to analog zero (A0)
  pinMode(A0, INPUT);

  // Reset the timer
  timer = micros();
}


void loop() {
  // Stabilize sampling rate
  timeSync(loopTimeMicroSec);

  // Read the raw data from MPU-6050
  readMPU6050();

  // Loop through all eight pins on multiplexer reading analog
  for (byte pin=0; pin<=7; pin++){
    selectMuxPin(pin);
    FSR[pin] = analogRead(A0);
  }

  FSR[8] = analogRead(A1);
  FSR[9] = analogRead(A2);
  FSR[10] = analogRead(A3);

  // Send raw values to Python
  writeBytes(&gyro_x, &gyro_y, &gyro_z, &acc_x, &acc_y, &acc_z,
    &FSR[0], &FSR[1], &FSR[2], &FSR[3], &FSR[4], &FSR[5], &FSR[6], &FSR[7], &FSR[8], &FSR[9], &FSR[10]);
}


void timeSync(unsigned long deltaT){
  // Calculate required delay to run at 200 Hz
  unsigned long currTime = micros();
  long timeToDelay = deltaT - (currTime - timer);

  if (timeToDelay > 5000){
    delay(timeToDelay / 1000);
    delayMicroseconds(timeToDelay % 1000);
  } else if (timeToDelay > 0){
    delayMicroseconds(timeToDelay);
  } else {}

  timer = currTime + timeToDelay;
}


void selectMuxPin(byte pin){
  // Set the S0, S1, and S2 pins to yield Y0-Y7
  for (int i=0; i<3; i++){
    if (pin & (1<<i))
      digitalWrite(selectPins[i], HIGH);
    else
      digitalWrite(selectPins[i], LOW);
  }
}


void writeBytes(int* data1, int* data2, int* data3, int* data4, int* data5, int* data6,
  int* data7, int* data8, int* data9, int* data10, int* data11, int* data12, int* data13,
  int* data14, int* data15, int* data16, int* data17){

  // Cast to a byte pointer
  byte* byteData1 = (byte*)(data1);     byte* byteData2 = (byte*)(data2);
  byte* byteData3 = (byte*)(data3);     byte* byteData4 = (byte*)(data4);
  byte* byteData5 = (byte*)(data5);     byte* byteData6 = (byte*)(data6);
  byte* byteData7 = (byte*)(data7);     byte* byteData8 = (byte*)(data8);
  byte* byteData9 = (byte*)(data9);     byte* byteData10 = (byte*)(data10);
  byte* byteData11 = (byte*)(data11);   byte* byteData12 = (byte*)(data12);
  byte* byteData13 = (byte*)(data13);   byte* byteData14 = (byte*)(data14);
  byte* byteData15 = (byte*)(data15);   byte* byteData16 = (byte*)(data16);
  byte* byteData17 = (byte*)(data17);

  // Byte array with header for transmission
  byte buf[38] = {0x9F, 0x6E,
                 byteData1[0],  byteData1[1],     byteData2[0],  byteData2[1],
                 byteData3[0],  byteData3[1],     byteData4[0],  byteData4[1],
                 byteData5[0],  byteData5[1],     byteData6[0],  byteData6[1],
                 byteData7[0],  byteData7[1],     byteData8[0],  byteData8[1],
                 byteData9[0],  byteData9[1],     byteData10[0], byteData10[1],
                 byteData11[0], byteData11[1],    byteData12[0], byteData12[1],
                 byteData13[0], byteData13[1],    byteData14[0], byteData14[1],
                 byteData15[0], byteData15[1],    byteData16[0], byteData16[1],
                 byteData17[0], byteData17[1],    0xAE, 0x72};
  Serial.write(buf, 38);
}


void readMPU6050() {
  //Subroutine for reading the raw data
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);
  Wire.endTransmission();
  Wire.requestFrom(0x68, 14);

  // Read data --> Temperature falls between acc and gyro registers
  while(Wire.available() < 14);
  acc_x = Wire.read() << 8 | Wire.read();
  acc_y = Wire.read() << 8 | Wire.read();
  acc_z = Wire.read() << 8 | Wire.read();
  temperature = Wire.read() <<8 | Wire.read();
  gyro_x = Wire.read()<<8 | Wire.read();
  gyro_y = Wire.read()<<8 | Wire.read();
  gyro_z = Wire.read()<<8 | Wire.read();
}


void setupMPU6050() {
  //Activate the MPU-6050
  Wire.beginTransmission(0x68);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();

  // Configure the accelerometer
  // 2g --> 0x00, 4g --> 0x08, 8g --> 0x10, 16g --> 0x18
  Wire.beginTransmission(0x68);
  Wire.write(0x1C);
  Wire.write(0x00);
  Wire.endTransmission();

  // Configure the gyro
  // 250 deg/s --> 0x00, 500 deg/s --> 0x08, 1000 deg/s --> 0x10, 2000 deg/s --> 0x18
  Wire.beginTransmission(0x68);
  Wire.write(0x1B);
  Wire.write(0x00);
  Wire.endTransmission();
}
