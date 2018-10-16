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
#define FREQ_AQUIRE          500                   //Frequency in Hz
#define INTERVAL_MS_AQUIRE   500 / FREQ_AQUIRE     //Interval in milliseconds
#define INTERVAL_US_AQUIRE   500000 / FREQ_AQUIRE  //Interval in microseconds

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

//Arduino Pins
#define SUPINAR_WAVE_PIN    8
#define PRONAR_WAVE_PIN     9
#define PINCAR_WAVE_PIN     10
#define FECHAR_WAVE_PIN     11
#define ESTENDER_WAVE_PIN   12
#define FLEXIONAR_WAVE_PIN  13

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

  pinMode(SUPINAR_WAVE_PIN, INPUT_PULLUP);
  pinMode(PRONAR_WAVE_PIN, INPUT_PULLUP);
  pinMode(PINCAR_WAVE_PIN, INPUT_PULLUP);
  pinMode(FECHAR_WAVE_PIN, INPUT_PULLUP);
  pinMode(ESTENDER_WAVE_PIN, INPUT_PULLUP);
  pinMode(FLEXIONAR_WAVE_PIN, INPUT_PULLUP);

  my_generator.setOffset(512);
  my_generator.setAmplitude(512);
  my_generator.setWaveform(SUPINAR_WAVE);

  SETUP_TIMER();
  START_TIMER();
}

void loop() {
    // Movement Selection
    if(!digitalRead(SUPINAR_WAVE_PIN)){
        my_generator.setWaveform(SUPINAR_WAVE);
    }
    else if(!digitalRead(PRONAR_WAVE_PIN)){
        my_generator.setWaveform(PRONAR_WAVE);
    }
    else if(!digitalRead(PINCAR_WAVE_PIN)){
        my_generator.setWaveform(PINCAR_WAVE);
    }
    else if(!digitalRead(FECHAR_WAVE_PIN)){
        my_generator.setWaveform(FECHAR_WAVE);
    }
    else if(!digitalRead(ESTENDER_WAVE_PIN)){
        my_generator.setWaveform(ESTENDER_WAVE);
    }
    else if(!digitalRead(FLEXIONAR_WAVE_PIN)){
        my_generator.setWaveform(FLEXIONAR_WAVE);
    } else{
        my_generator.setWaveform(REPOUSO_WAVE);
    }
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
