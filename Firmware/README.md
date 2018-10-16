# Main

## Firmware: Arduino Sketchs
Here there are two arduino sketchs:
1. emg-four-channel-acquirer
1. emg-four-channel-simulator

Both are based in a timer for acquiring a sample of each channel in a frequency
of 1000 Hz.
The acquirer works in almost all arduino boards
(tested in some ATMEGA328p based boards and in Arduino Due (ARM)).

### Requisites
We utilize the following libraries to create a precise timer:
* Arduino Due: [DueTimer](https://github.com/ivanseidel/DueTimer). Developed by a friend of Lucas Lemos called Ivan Seidel and available in his github repository.
* Arduino Uno: [TimerOne](https://github.com/PaulStoffregen/TimerOne). I found this in the Arduino Playground website, and it has showed to be a good and accurate timer.

If you don't know how to install a Arduino Library may [this](https://www.arduino.cc/en/Guide/Libraries) can help you.

### Notes
The simulator is based in a data file called `dados_gerados.h`.
This file contains huge vectors if real EMG recordings.
