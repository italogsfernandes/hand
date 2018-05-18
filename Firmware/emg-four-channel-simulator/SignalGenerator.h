#ifndef __SignalGenerator__
#define __SignalGenerator__

#include <avr/pgmspace.h> //for IDE versions below 1.0 (2011)
#include <dados_gerados.h>

//Tipos de ondas possiveis de se selecionar
typedef enum {
  REPOUSO,
  SUPINAR,
  PRONAR,
  PINCAR,
  FECHAR,
  ESTENDER,
  FLEXIONAR
} waveforms_t;

/////////////////////////////////////////
//Classe para gerar as formas de onda //
////////////////////////////////////////
class SignalGenerator_t {
  private:
    waveforms_t _waveform; //Acessible by getter and setter

    uint16_t _actual_index; //Index de leitura do vetor de dados
    float _actual_value; //Valor atual
    float _offset;
    float _amplitude;

    uint16_t _qnt_points;
    uint8_t _freq_divider;

    double get_next() {
      switch (_waveform) {
        case REPOUSO:
          _actual_value[0] = 0;
          _actual_value[1] = 0;
          _actual_value[2] = 0;
          _actual_value[3] = 0;
        case SUPINAR:
          _actual_value[0] = pgm_read_float_near(emg_supinar_wave + _actual_index * _freq_divider);
          _actual_value[1] = pgm_read_float_near(emg_supinar_wave + 1 + _actual_index * _freq_divider);
          _actual_value[2] = pgm_read_float_near(emg_supinar_wave + 2 + _actual_index * _freq_divider);
          _actual_value[3] = pgm_read_float_near(emg_supinar_wave + 3 + _actual_index * _freq_divider);
          break;
        case PRONAR:
          _actual_value[0] = pgm_read_float_near(emg_supinar_wave + _actual_index * _freq_divider);
          _actual_value[1] = pgm_read_float_near(emg_supinar_wave + 1 + _actual_index * _freq_divider);
          _actual_value[2] = pgm_read_float_near(emg_supinar_wave + 2 + _actual_index * _freq_divider);
          _actual_value[3] = pgm_read_float_near(emg_supinar_wave + 3 + _actual_index * _freq_divider);
          break;
        case PINCAR:
          _actual_value[0] = pgm_read_float_near(emg_supinar_wave + _actual_index * _freq_divider);
          _actual_value[1] = pgm_read_float_near(emg_supinar_wave + 1 + _actual_index * _freq_divider);
          _actual_value[2] = pgm_read_float_near(emg_supinar_wave + 2 + _actual_index * _freq_divider);
          _actual_value[3] = pgm_read_float_near(emg_supinar_wave + 3 + _actual_index * _freq_divider);
          break;
        case FECHAR:
          _actual_value[0] = pgm_read_float_near(emg_supinar_wave + _actual_index * _freq_divider);
          _actual_value[1] = pgm_read_float_near(emg_supinar_wave + 1 + _actual_index * _freq_divider);
          _actual_value[2] = pgm_read_float_near(emg_supinar_wave + 2 + _actual_index * _freq_divider);
          _actual_value[3] = pgm_read_float_near(emg_supinar_wave + 3 + _actual_index * _freq_divider);
          break;
        case ESTENDER:
          _actual_value[0] = pgm_read_float_near(emg_supinar_wave + _actual_index * _freq_divider);
          _actual_value[1] = pgm_read_float_near(emg_supinar_wave + 1 + _actual_index * _freq_divider);
          _actual_value[2] = pgm_read_float_near(emg_supinar_wave + 2 + _actual_index * _freq_divider);
          _actual_value[3] = pgm_read_float_near(emg_supinar_wave + 3 + _actual_index * _freq_divider);
          break;
        case FLEXIONAR:
          _actual_value[0] = pgm_read_float_near(emg_supinar_wave + _actual_index * _freq_divider);
          _actual_value[1] = pgm_read_float_near(emg_supinar_wave + 1 + _actual_index * _freq_divider);
          _actual_value[2] = pgm_read_float_near(emg_supinar_wave + 2 + _actual_index * _freq_divider);
          _actual_value[3] = pgm_read_float_near(emg_supinar_wave + 3 + _actual_index * _freq_divider);
          break;
        case SUPINAR:
          _actual_value[0] = pgm_read_float_near(emg_supinar_wave + _actual_index * _freq_divider);
          _actual_value[1] = pgm_read_float_near(emg_supinar_wave + 1 + _actual_index * _freq_divider);
          _actual_value[2] = pgm_read_float_near(emg_supinar_wave + 2 + _actual_index * _freq_divider);
          _actual_value[3] = pgm_read_float_near(emg_supinar_wave + 3 + _actual_index * _freq_divider);
          break;
      }
      _actual_value[0] = _actual_value[0] * _amplitude + _offset;
      _actual_value[1] = _actual_value[1] * _amplitude + _offset;
      _actual_value[2] = _actual_value[2] * _amplitude + _offset;
      _actual_value[3] = _actual_value[3] * _amplitude + _offset;
      ++_actual_index %= (_qnt_points / _freq_divider); //Incremento circular
      return _actual_value;
    }

  public:
    SignalGenerator_t () {
      _waveform = REPOUSO;
      _actual_index = 0;
      _offset = 0;
      _amplitude = 100;
      _freq_divider = 1;
    }

    void generate_value(float *value_holder) {
      get_next();
      value_holder[0] = _actual_value[0];
      value_holder[1] = _actual_value[1];
      value_holder[2] = _actual_value[2];
      value_holder[3] = _actual_value[3];
    }

    ////////////////////////
    //Getters and Setters //
    ////////////////////////

    waveforms_t getWaveform() {
      return _waveform;
    }

    void setWaveform(waveforms_t waveform) {
      _waveform = waveform;
      switch (_waveform) {
        case REPOUSO:
          break;
        case SUPINAR:
          _qnt_points = size(emg_supinar_wave) / size(float);
          break;
        case PRONAR:
          _qnt_points = size(emg_pronar_wave) / size(float);
          break;
        case PINCAR:
          _qnt_points = size(emg_pincar_wave) / size(float);
          break;
        case FECHAR:
          _qnt_points = size(emg_fechar_wave) / size(float);
          break;
        case ESTENDER:
          _qnt_points = size(emg_estender_wave) / size(float);
          break;
        case FLEXIONAR:
          _qnt_points = size(emg_flexionar_wave) / size(float);
          break;
      }
    }

    void setAmplitude(float amplitude) {
      _amplitude = amplitude;
    }

    void setOffset(float offset) {
      _offset = offset;
    }

    void setQntPointsPerInterval(uint16_t qnt_points) {
      _qnt_points = qnt_points;
    }

    void setFreqDivider(uint16_t freq_divider) {
      _freq_divider = freq_divider;
    }
};

#endif
