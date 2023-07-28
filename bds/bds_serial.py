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


def ser_hot_plug_detect(last_default_des, last_des_list, last_name_list):
    """
    Detecting Serial Port Hot Unplugging, Recommended to be called at 1s intervals.

    :param last_default_des: Current serial port description in the final combo box.
    :param last_des_list: Last serial port description ([''USB-SERIAL CH340 (COM12)', ‘通信端口 (COM1)'...]) list.
    :param last_name_list: Last serial port name (['COM1,COM2'...]) list.
    :return: Serial port description displayed by default in the combo box. Returns an 'empty string' indicating no
    change to the serial port
    """
    cur_com_des_list, cur_com_name_list = serial_find()
    default_des = ''
    if cur_com_des_list and cur_com_name_list != last_name_list:
        des_new, des_old = set(cur_com_des_list), set(last_des_list)
        # 串口增加
        def_new_len, def_old_len = len(des_new), len(des_old)
        if def_new_len > def_old_len:
            # 插入
            default_des = list(des_new.difference(des_old))[0]
        elif def_new_len < def_old_len:
            # 拔出，但不是目标串口
            if last_default_des in cur_com_des_list:
                default_des = last_default_des
            else:
                default_des = cur_com_des_list[0]
        else:
            pass
        del last_des_list[:]
        del last_name_list[:]
        [last_name_list.append(v) for v in cur_com_name_list]
        [last_des_list.append(v) for v in cur_com_des_list]

    return default_des


def ser_buad_list_adjust(cur_baud, bauds):
    """
    Adjust the baud rate list to place the desired baud rate in the first position of the list.
    This baud rate will be the default baud rate the next time you open the software.
    :param cur_baud: The baud rate you need.
    :param bauds: Baud rate list.
    :return: Adjusted Baud Rate List.
    """
    # 删除重复波特率
    bauds = [x for x in bauds if x != cur_baud]
    # 将需要的波特率插入第一行
    bauds.insert(0, cur_baud)
    return bauds


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
                    elif self.char_format == 'utf-8':
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
                    elif self.char_format == 'hex':
                        self.hw_data_hex_handle(bytes_data)
                except Exception as e:
                    self.err_cb('Serial:%s\n' % e)
        except Exception as e:
            self.err_cb('Serial:%s\n' % e)


if __name__ == '__main__':
    pass
