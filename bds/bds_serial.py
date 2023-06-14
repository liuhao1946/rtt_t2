import serial
from serial.tools import list_ports_windows
from .bds_utils import *
from queue import Queue
# import re
from bds.hw_base import HardWareBase


# from datetime import datetime


def serial_find():
    """
    返回计算机上的COM名称

    :return: [serial description, serial name]
    """
    com_des_list = []
    com_name_list = []
    com_information = list_ports_windows.comports()
    for i in range(len(com_information)):
        com_des_list.append(com_information[i].description)
        com_name_list.append(com_information[i].name)

    return [com_des_list, com_name_list]


class BDS_Serial(HardWareBase):
    def __init__(self, err_cb, warn_cb, com_name='', baud=115200,
                 read_size=10240, tag_detect_timeout_s=6.0, read_rtt_data_interval_s=0.002, char_format='asc',
                 **kwargs):
        super().__init__(err_cb, warn_cb, tag_detect_timeout_s, read_rtt_data_interval_s, char_format, **kwargs)
        self.bytes_data = b''
        self.ser = serial.Serial()
        self.com_name = com_name
        self.baudrate = baud
        self.rx_timeout = read_rtt_data_interval_s
        self.read_size = read_size
        self.clk = 0
        self.ser_is_start = False
        self.ser_data_queue = Queue()

    def hw_open(self, port='', baud=115200, rx_buffer_size=10240):
        try:
            # print(port,baud)
            self.hw_para_init()
            self.ser.port = port
            self.ser.baudrate = baud
            self.ser.set_buffer_size(rx_buffer_size)
            self.ser.open()
            self.ser.reset_input_buffer()
            self.ser_is_start = True
        except Exception as e:
            self.err_cb('%s\n' % e)
            print(e)

    def hw_close(self):
        self.ser_is_start = False
        if self.ser.is_open:
            self.ser.close()

    def get_hw_serial_number(self):
        pass

    def hw_is_open(self):
        return self.ser.is_open

    def hw_write(self, data):
        self.ser.write(list_to_bytes(data))

    def hw_read(self):
        try:
            if self.ser_is_start:
                bytes_data = self.ser.read_all()
                try:
                    if self.char_format == 'asc':
                        raw_ser_data_str = ''.join(map(lambda x: chr(x), bytes_data))
                        self.hw_data_handle(raw_ser_data_str)
                    else:
                        # utf-8
                        if len(bytes_data) > 0:
                            self.bytes_data += bytes_data
                            self.clk = int((6 / (self.rx_timeout * 1000)))
                        else:
                            if self.clk != 0:
                                self.clk -= 1
                        if self.clk == 0:
                            decoded_str = self.bytes_data.decode('utf-8', errors='ignore')
                            decoded_str = decoded_str.replace("\\n", "\n")
                            self.hw_data_handle(decoded_str)
                            self.bytes_data = b''
                except Exception as e:
                    self.err_cb('Serial:%s\n' % e)
        except Exception as e:
            self.err_cb('Serial:%s\n' % e)


if __name__ == '__main__':
    pass
