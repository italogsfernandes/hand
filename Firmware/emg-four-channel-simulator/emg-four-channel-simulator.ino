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
#define PLOTTER_SERIAL

//Libraries
#include "SignalGenerator.h"

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

////////////
//Defines //
////////////
#define UART_BAUDRATE 115200
#define PACKET_START  '$'
#define PACKET_END    '\n'
#define QNT_CH        4

////////////////
//Global data //
////////////////
SignalGenerator_t my_generator;
uint16_t generated_value;
float emg_read_values[QNT_CH];
uint16_t adc_read_values[QNT_CH];

void timerDataAcq();
void sendData();
void showData();
//////////////////
//Main Function //
//////////////////
void setup() {
  Serial.begin(UART_BAUDRATE);
  
  my_generator.setOffset(512);
  my_generator.setAmplitude(512);
  my_generator.setWaveform(REPOUSO_WAVE);
  
  SETUP_TIMER();
  START_TIMER();
}

void loop() {

}

///////////////////
//Aquire Routine //
///////////////////
void timerDataAcq() {
  my_generator.generate_value(emg_read_values);
  for(int i=0; i<QNT_CH; i++){
    adc_read_values[i] = (uint16_t) emg_read_values[i];
  }
  //Sending the value
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
