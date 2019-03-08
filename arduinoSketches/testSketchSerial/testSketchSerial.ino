int counter = 0;
int data[8];
int datacount = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:

 if (Serial.available() > 0) {
    char buf[8];
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

    if (buf[0] == 'd'){
      datacount = (buf[1]-'0')*1000 + (buf[2]-'0')*100 + (buf[3]-'0')*10 + (buf[4]-'0');
    }
    Serial.println(datacount);
  }
  
  while (datacount > 0){
  for (int i=0;i<9;i++){
    Serial.print(i+counter);
    Serial.print(',');
  }

  Serial.println();
  counter += 1;
//  delay(500);
  datacount -= 1;
  }
}
