// Adapted from https://www.thepoorengineer.com/en/arduino-python-plot/
unsigned long timer = 0;
long loopTime = 5000;   // microseconds


void setup() {
  Serial.begin(115200);
  timer = micros();
}


void loop() {
  timeSync(loopTime);

  // Double data type
  // double val0 = analogRead(A0)/ 1.0;
  // double val1 = analogRead(A1)/ 1.0;
  // double val2 = analogRead(A2)/ 1.0;
  // double val3 = analogRead(A3)/ 1.0;
  // double val4 = analogRead(A4)/ 1.0;
  // double val5 = analogRead(A5)/ 1.0;
  // double val6 = analogRead(A6)/ 1.0;
  // double val7 = analogRead(A7)/ 1.0;

  // // Int data type
  int val0 = analogRead(A0);
  int val1 = analogRead(A1);
  int val2 = analogRead(A2);
  int val3 = analogRead(A3);
  int val4 = analogRead(A4);
  int val5 = analogRead(A5);
  int val6 = analogRead(A6);
  int val7 = analogRead(A7);

  writeBytes(&val0, &val1, &val2, &val3, &val4, &val5, &val6, &val7);
}


void timeSync(unsigned long deltaT){
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


void writeBytes(int* data1, int* data2, int* data3, int* data4, int* data5, int* data6, int* data7, int* data8){
  byte* byteData1 = (byte*)(data1);
  byte* byteData2 = (byte*)(data2);
  byte* byteData3 = (byte*)(data3);
  byte* byteData4 = (byte*)(data4);
  byte* byteData5 = (byte*)(data5);
  byte* byteData6 = (byte*)(data6);
  byte* byteData7 = (byte*)(data7);
  byte* byteData8 = (byte*)(data8);

  byte buf[16] = {byteData1[0], byteData1[1],
                 byteData2[0], byteData2[1],
                 byteData3[0], byteData3[1],
                 byteData4[0], byteData4[1],
                 byteData5[0], byteData5[1],
                 byteData6[0], byteData6[1],
                 byteData7[0], byteData7[1],
                 byteData8[0], byteData8[1]};
  Serial.write(buf, 16);
}


void writeBytes(double* data1, double* data2, double* data3, double* data4, double* data5, double* data6, double* data7, double* data8){
  byte* byteData1 = (byte*)(data1);
  byte* byteData2 = (byte*)(data2);
  byte* byteData3 = (byte*)(data3);
  byte* byteData4 = (byte*)(data4);
  byte* byteData5 = (byte*)(data5);
  byte* byteData6 = (byte*)(data6);
  byte* byteData7 = (byte*)(data7);
  byte* byteData8 = (byte*)(data8);

  byte buf[32] = {byteData1[0], byteData1[1], byteData1[2], byteData1[3],
                 byteData2[0], byteData2[1], byteData2[2], byteData2[3],
                 byteData3[0], byteData3[1], byteData3[2], byteData3[3],
                 byteData4[0], byteData4[1], byteData4[2], byteData4[3],
                 byteData5[0], byteData5[1], byteData5[2], byteData5[3],
                 byteData6[0], byteData6[1], byteData6[2], byteData6[3],
                 byteData7[0], byteData7[1], byteData7[2], byteData7[3],
                 byteData8[0], byteData8[1], byteData8[2], byteData8[3]};
  Serial.write(buf, 32);
}
