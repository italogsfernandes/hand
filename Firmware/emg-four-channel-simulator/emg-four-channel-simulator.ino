/* UNIVERSIDADE FEDERAL DE UBERLANDIA
   Biomedical Engineering
   
   Autors: Ítalo G S Fernandes
           Julia Nepomuceno Mello
           
   contact: italogsfernandes@gmail.
   URLs: https://github.com/italogfernandes/

  Requisitos: Biblioteca Timer One[https://github.com/PaulStoffregen/TimerOne]
   
  Este codigo faz parte da disciplina de topicos avancados
  em instrumentacao boomedica e visa realizar a aquisicao
  de dados via o conversor AD do arduino e o envio destes
  para a interface serial.
  
  O seguinte pacote é enviado:
  Pacote: START | MSB  | LSB  | END
  Exemplo:  '$' | 0x01 | 0x42 | '\n'
*/
//Ativa e desativa o envio para o plotter serial
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
/* UNIVERSIDADE FEDERAL DE UBERLANDIA
   Biomedical Engineering Lab
   Autors: Ítalo G S Fernandes
   contact: italogsfernandes@gmail.com
   URLs: https://github.com/italogfernandes/
  Este codigo faz parte da disciplina de sistemas em tempo real
  para engenhara biomedica e visa emular um gerador de sinais
  utilizando o Arduino.
  Tal sinal tambem sera enviado para a interface Serial
  podendo ser visualizado pelo serial plotter.
  Podem ser utilizados:
    SIN_WAVE,
    SQUARE_WAVE,
    TRIANGLE_WAVE,
    RAMP_WAVE,
    CONST_WAVE,
    ECG_WAVE,
    EMG_WAVE,
    ADC_WAVE
*/
//Ativa e desativa o envio para o plotter serial
//#define PLOTTER_SERIAL

#include "SignalGenerator.h"

#define UART_BAUDRATE 115200
#define PACKET_START  '$'
#define PACKET_END    '\n'
#define PIN_ADC A0


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

//////////////////////
//Variaveis globais //
//////////////////////
SignalGenerator_t my_generator(PIN_ADC);
uint16_t generated_value;

//////////////////
//Main Function //
//////////////////
void setup() {
  Serial.begin(UART_BAUDRATE);

  my_generator.setOffset(512);
  my_generator.setAmplitude(512);
  my_generator.setWaveform(EMG_WAVE);

  SETUP_TIMER();
  START_TIMER();
}

void loop() {

}

///////////////////
//Aquire Routine //
///////////////////
void timerDataAcq() {
  //Getting the value
  generated_value = (uint16_t) my_generator.generate_value();

  //Sending the value
#ifdef PLOTTER_SERIAL
  Serial.print(generated_value);
  Serial.println();
#else
  Serial.write(PACKET_START);
  Serial.write(generated_value >> 8);
  Serial.write(generated_value);
  Serial.write(PACKET_END);
#endif
}
