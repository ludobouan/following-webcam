import serial
ser = serial.Serial('/dev/tty.usbserial', 9600)
ser.write('5')