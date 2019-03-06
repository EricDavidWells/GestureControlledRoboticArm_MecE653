// http://robojax.com/learn/arduino/?vid=robojax_16ch_relay_multiplexer
// https://www.youtube.com/watch?v=lQL6dfL_rsg&feature=youtu.be

/*
 * using CD74HC4067 chip to control 16 channel relay
 * with any Arduino board. This code will control 1 relay at a time
 *
 * watch video instruction for this video:https://youtu.be/lQL6dfL_rsg
 *
 * Watch main video explaining the 16 channel relay module:
 * https://youtu.be/Q9aBI4ELKC4
 *
 * Written by Ahmad Shamshiri for Robojax.com on Sunday September 30th, 2018
 * at 13:56 in Ajax, Ontario, Canada
 * Video Tutorial recorded Nov 30, 2018
 *
  * This code is "AS IS" without warranty or liability. Free to be used as long as you keep this note intact.*
 * This code has been download from Robojax.com
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

const int SIG = 2;// SIG pin
const int EN = 7;// Enable pin
const int controlPin[4] = {3, 4, 5, 6}; // 4 pins used for binary output

int loopDelay = 1000;// delay in loop

const int muxTable[16][4] = {
  // s0, s1, s2, s3     channel
    {0,  0,  0,  0}, // 0
    {1,  0,  0,  0}, // 1
    {0,  1,  0,  0}, // 2
    {1,  1,  0,  0}, // 3
    {0,  0,  1,  0}, // 4
    {1,  0,  1,  0}, // 5
    {0,  1,  1,  0}, // 6
    {1,  1,  1,  0}, // 7
    {0,  0,  0,  1}, // 8
    {1,  0,  0,  1}, // 9
    {0,  1,  0,  1}, // 10
    {1,  1,  0,  1}, // 11
    {0,  0,  1,  1}, // 12
    {1,  0,  1,  1}, // 13
    {0,  1,  1,  1}, // 14
    {1,  1,  1,  1}  // 15
};



void setup() {
  // Robojax 16ch relay with multiplexer 20181201
  for(int i=0; i<4; i++)
  {
    pinMode(controlPin[i], OUTPUT);// set pin as output
    digitalWrite(controlPin[i], HIGH); // set initial state as HIGH

  }


    pinMode(SIG, OUTPUT);// set SIG pin as output
    digitalWrite(SIG, LOW); // set SIG sends what should be the output
                            // for low trigger relay it should be LOW
                            // for HIGH trigger high it should be HIGH

    pinMode(EN, OUTPUT);// set EN pin as output
    digitalWrite(EN, LOW); // set EN in (enable pin) Low to activate the chip
  Serial.begin(9600);

   // Robojax 16ch relay with multiplexer 20181201
}

void loop() {
// Robojax 16ch relay with multiplexer 20181201
  for(int i=0; i<16; i++)
  {

  channelControl(i);

  delay(loopDelay);// wait for loopDelay ms
  }

  //channelControl(7);// this will turn on only relay 12
 Serial.println("===============");

  // Robojax 16ch relay with multiplexer 20181201
}

/*
 *
 * @brief controls each relay ON or OFF
 * @param relayChannel (integer)
 * @return no return value
 */

void channelControl(int relayChannel)
{
    // Robojax 16ch relay with multiplexer 20181201
    digitalWrite(controlPin[0], muxTable[relayChannel][0]);
    digitalWrite(controlPin[1], muxTable[relayChannel][1]);
    digitalWrite(controlPin[2], muxTable[relayChannel][2]);
    digitalWrite(controlPin[3], muxTable[relayChannel][3]);

       Serial.print(relayChannel);
       Serial.print (": ");
       Serial.print(muxTable[relayChannel][3]);
       Serial.print(muxTable[relayChannel][2]);
       Serial.print(muxTable[relayChannel][1]);
       Serial.println(muxTable[relayChannel][0]);
   // Robojax 16ch relay with multiplexer 20181201
}//channelControl end
