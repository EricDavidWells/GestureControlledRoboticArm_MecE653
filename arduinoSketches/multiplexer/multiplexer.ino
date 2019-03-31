// Declare variables
const int selectPins[3] = {2, 3, 4};
unsigned long timer = 0;
long loopTimeMicroSec = 5000;
int FSR[11];
double avgFSR = 0;


void setup(){
  // Start serial
  Serial.begin(115200);

  // Set up the select pins as outputs
  for (int i=0; i<3; i++){
    pinMode(selectPins[i], OUTPUT);
    digitalWrite(selectPins[i], HIGH);
  }

  // Connect z to analog zero
  pinMode(A0, INPUT);

  // Reset the timer
  timer = micros();
}



void loop(){
  // Stabilize sampling rate
  timeSync(loopTimeMicroSec);

  // Loop through all eight pins.
  for (byte pin=0; pin<=7; pin++){
    selectMuxPin(pin);
    FSR[pin] = analogRead(A0);
  }

  FSR[8] = analogRead(A1);
  FSR[9] = analogRead(A2);
  FSR[10] = analogRead(A3);

//  // Send raw values to Python
//  writeBytes(&FSR[0], &FSR[1], &FSR[2], &FSR[3], &FSR[4], &FSR[5], &FSR[6], &FSR[7]);

  // Send raw values to serial port
  for (int i=0; i<11; i++){
    Serial.print(FSR[i]); Serial.print(",");
    avgFSR += FSR[i];
  }
  Serial.println(avgFSR/11);
  avgFSR = 0;

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



void writeBytes(int* data1, int* data2, int* data3, int* data4, int* data5, int* data6, int* data7, int* data8){
  // Cast to a byte pointer
  byte* byteData1 = (byte*)(data1);
  byte* byteData2 = (byte*)(data2);
  byte* byteData3 = (byte*)(data3);
  byte* byteData4 = (byte*)(data4);
  byte* byteData5 = (byte*)(data5);
  byte* byteData6 = (byte*)(data6);
  byte* byteData7 = (byte*)(data7);
  byte* byteData8 = (byte*)(data8);

  // Byte array with header for transmission
  byte buf[18] = {0x9F, 0x6E,
                 byteData1[0], byteData1[1],
                 byteData2[0], byteData2[1],
                 byteData3[0], byteData3[1],
                 byteData4[0], byteData4[1],
                 byteData5[0], byteData5[1],
                 byteData6[0], byteData6[1],
                 byteData7[0], byteData7[1],
                 byteData8[0], byteData8[1]};
  Serial.write(buf, 18);
}
