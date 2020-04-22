unsigned long timer = 0;
long loopTime = 5000;   // microseconds
 
void setup() {
  Serial.begin(38400);
  timer = micros();
}

void loop() {
  timeSync(loopTime);
  int val0 = analogRead(0); // - 512;
  int val1 = analogRead(1); // - 512;
  int val2 = analogRead(2); // - 512;
  int val3 = analogRead(3); // - 512;
  int val4 = analogRead(4); // - 512;
//  double val0 = (analogRead(0) - 512) / 512.0;
//  double val1 = (analogRead(1) - 512) / 512.0;
//  double val2 = (analogRead(2) - 512) / 512.0;
//  double val3 = (analogRead(3) - 512) / 512.0;
//  double val4 = (analogRead(4) - 512) / 512.0;
  sendToPC(&val0, &val1, &val2, &val3, &val4);
}

void timeSync(unsigned long deltaT)
{
  unsigned long currTime = micros();
  long timeToDelay = deltaT - (currTime - timer);
  if (timeToDelay > 5000)
  {
    delay(timeToDelay / 1000);
    delayMicroseconds(timeToDelay % 1000);
  }
  else if (timeToDelay > 0)
  {
    delayMicroseconds(timeToDelay);
  }
  else
  {
      // timeToDelay is negative so we start immediately
  }
  timer = currTime + timeToDelay;
}
 
void sendToPC(int* data0, int* data1, int* data2, int* data3, int* data4)
{
  byte* byteData0 = (byte*)(data0);
  byte* byteData1 = (byte*)(data1);
  byte* byteData2 = (byte*)(data2);
  byte* byteData3 = (byte*)(data3);
  byte* byteData4 = (byte*)(data4);
  byte buf[10] = {byteData0[0], byteData0[1],
                  byteData1[0], byteData1[1],
                  byteData2[0], byteData2[1],
                  byteData3[0], byteData3[1],
                  byteData4[0], byteData4[1]};
  Serial.write(buf, 10);
}
 
void sendToPC(double* data0, double* data1, double* data2, double* data3, double* data4)
{
  byte* byteData0 = (byte*)(data0);
  byte* byteData1 = (byte*)(data1);
  byte* byteData2 = (byte*)(data2);
  byte* byteData3 = (byte*)(data3);
  byte* byteData4 = (byte*)(data4);
  byte buf[20] = {byteData0[0], byteData0[1], byteData0[2], byteData0[3],
                  byteData1[0], byteData1[1], byteData1[2], byteData1[3],
                  byteData2[0], byteData2[1], byteData2[2], byteData2[3],
                  byteData3[0], byteData3[1], byteData3[2], byteData3[3],
                  byteData4[0], byteData4[1], byteData4[2], byteData4[3]};
  Serial.write(buf, 20);
}


//int sensorPin = A1;  // The photodiode on A1
//int sensorValue = 0;  // variable to store data 
//
//void setup(void) {
//   pinMode(sensorPin, INPUT);
//   
//   Serial.begin(9600);  // initialise serial communication
//}
// 
//void loop(void) {
//   sensorValue = analogRead(sensorPin);
//   Serial.println(sensorValue);
//   delay(100);
//}
