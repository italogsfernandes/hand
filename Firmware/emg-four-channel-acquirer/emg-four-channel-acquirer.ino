/* UNIVERSIDADE FEDERAL DE UBERLANDIA
   Biomedical Engineering

   Autors: Ítalo G S Fernandes

   contact: italogsfernandes@gmail.
   URLs: https://github.com/italogfernandes/

  Requisites: Library Timer One[https://github.com/PaulStoffregen/TimerOne]

  This code aims to acquire data from the arduino analog to digital converter
  (ADC) and send this to the serial interface as ASCII text or as binary data.

  When selected the binary data mode this is the format of the packet
  For 1 channel:
  Packet:  START | MSB  | LSB  | END
  Exemple:  '$' | 0x01 | 0x42 | '\n'
  For n channels:
  Packet:  START | MSB1  | LSB1  | MSB...  | LSB...  | MSB_n  | LSB_n  | END
  Exemple:  '$' |  0x01 |  0x42 |  0x01   |  0x33   |  0x02   |  0xB4  | '\n'
*/
//Uncomment the next line to activate the sending of data as text
//This is usefull when you are using the serial plotter tool (Ctrl+shift+L)
//#define PLOTTER_SERIAL

//Libraries
///////////
//Timers //
///////////
#define FREQ_AQUIRE          1000                   //Frequency in Hz
#define INTERVAL_MS_AQUIRE   1000 / FREQ_AQUIRE     //Interval in milliseconds
#define INTERVAL_US_AQUIRE   1000000 / FREQ_AQUIRE  //Interval in microseconds

// Arduino DUE
#if defined(__arm__) && defined(__SAM3X8E__)
#include<DueTimer.h>
#define SETUP_TIMER()   Timer3.attachInterrupt(timerDataAcq).setFrequency(FREQ_AQUIRE)
#define START_TIMER()   Timer3.start()
#define STOP_TIMER()    Timer3.stop()
#endif

// Arduino UNO, NANO (and others 328P based boards), MEGA e ATtiny85
#if defined(__AVR_ATmega328P__) || defined(__AVR_ATmega2560__) || defined(__AVR_ATtiny85__)
#include<TimerOne.h>
#define SETUP_TIMER()   Timer1.initialize()
#define START_TIMER()   Timer1.attachInterrupt(timerDataAcq,INTERVAL_US_AQUIRE)
#define STOP_TIMER()    Timer1.stop()
#endif

////////////
//Defines //
////////////
#define PACKET_START  '$'
#define PACKET_END    '\n'
#define QNT_CH        4
const uint8_t adc_channels_pins[QNT_CH] PROGMEM = { A0, A1, A2, A3};

//Global data
uint16_t adc_read_values[QNT_CH];

//Setup
void setup() {
  Serial.begin(115200);
  SETUP_TIMER();
  START_TIMER();
}

void loop() {

}

//Aquire Routine
void timerDataAcq() {
  for(int i=0; i<QNT_CH; i++){
    adc_read_values[i] = analogRead(adc_channels_pins[i]);
  }//Sending the value
#ifndef PLOTTER_SERIAL
  sendData();
#else
  showData();
#endif
}

void sendData() {
  Serial.write(PACKET_START);
  for(int i=0; i<QNT_CH; i++){
    Serial.write(adc_read_values[i] >> 8);
    Serial.write(adc_read_values[i]);
  }
  Serial.write(PACKET_END);
}

void showData() {
  for(int i=0; i<QNT_CH; i++){
    Serial.print(adc_read_values[i]+1024*i);
    Serial.print("\t");
  }
  Serial.println();
}
