import serial

class ArduinoOutputController:
    """docstring for ArduinoOutputController."""
    def __init__(self):
        self.port_name = ""
        self.serialPort = serial.Serial()

    def open_port(self, p_name):
        self.port_name = p_name
        self.serialPort.port = self.port_name
        if not self.serialPort.isOpen():
            self.serialPort.open()
            self.serialPort.flushInput()
            self.serialPort.flushOutput()

    def close(self):
        """
        If the serial port is open, this method will try to close it.
        """
        if self.serialPort.isOpen():
            self.serialPort.close()

    def send_new_cmd(self, fingers=(0,0,0,0,0)):
        out_str = ""
        for f_index in range(len(fingers)):
            out_str += "%.2d " % fingers[f_index]
        out_str += "\n"
        if not self.serialPort.isOpen():
            print("Not connected, the message %s was not sent." % out_str)
        else:
            self.serialPort.write(out_str)
