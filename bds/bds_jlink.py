import pylink
from bds.hw_base import HardWareBase


def convert_numbers_to_string(numbers, byte_size=8):
    # 使用生成器表达式和字节串拼接
    byte_seq = (number.to_bytes(byte_size, 'little', signed=False) for number in numbers)
    return ''.join(map(lambda b: ''.join(chr(x) for x in b), byte_seq))


class BDS_Jlink(HardWareBase):
    def __init__(self, err_cb, warn_cb, chip='nRF52840_xxAA', speed=4000,
                 read_size=8192, tag_detect_timeout_s=6.0, read_rtt_data_interval_s=0.002, char_format='asc', **kwargs):
        super().__init__(err_cb, warn_cb, tag_detect_timeout_s, read_rtt_data_interval_s, char_format, **kwargs)
        self.jlink = pylink.JLink()
        self.speed = speed
        self.chip = chip
        self.rx_timeout = read_rtt_data_interval_s
        self.terminal = 0
        self.buffer_idx = 0
        self.read_size = read_size
        self.rtt_is_start = False
        self.clk = 0
        self.bytes_data = b''

    def find_rtt_address(self, start_address, range_size):
        if start_address is not None:
            num_bytes = self.jlink.memory_read64(start_address,  (range_size // 8))
            mem_data = convert_numbers_to_string(num_bytes)
            # mem_data = ''.join(map(chr, self.jlink.memory_read8(start_address, range_size)))
            return mem_data.find("SEGGER RTT")
        else:
            return -1

    def hw_open(self, speed=4000, chip='nRF52840_xxAA', reset_flag=True, start_address=None, range_size=0):
        try:
            # self.rtt_data_queue.queue.clear()
            self.hw_para_init()
            self.speed = speed
            self.chip = chip
            self.jlink.open()
            self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
            self.jlink.set_speed(self.speed)
            self.jlink.connect(self.chip)
            if reset_flag:
                self.jlink.reset(ms=10, halt=False)

            offset = self.find_rtt_address(start_address, range_size)
            if offset >= 0:
                start_address += offset

            if start_address is not None:
                print('找到_SEG RTT. 起始地址:%x, 地址偏移量:%d' % (start_address, offset))

            if self.jlink.connected():
                # TODO:考虑再次阅读这个函数
                # self.jlink.rtt_control()
                self.jlink.swo_flush()
                self.jlink.rtt_start(start_address)
                self.rtt_is_start = True
                print('jlink connect success...')
        except pylink.errors.JLinkException as e:
            self.err_cb('J_Link:%s\n' % e)
            print(e)

    def hw_close(self):
        if self.jlink.opened():
            try:
                self.rtt_is_start = False
                self.jlink.rtt_stop()
            except:
                pass
            self.jlink.close()

    def get_hw_serial_number(self):
        if self.jlink.opened():
            return self.jlink.serial_number
        else:
            return 0

    def hw_is_open(self):
        return self.jlink.opened()

    def hw_write(self, data):
        self.jlink.rtt_write(0, data)

    def hw_read(self):
        try:
            if self.rtt_is_start:
                rtt_data = self.jlink.rtt_read(self.buffer_idx, self.read_size)
                if self.char_format == 'asc':
                    rtt_data_str = ''.join([chr(v) for v in rtt_data])
                    self.hw_data_handle(rtt_data_str)
                elif self.char_format == 'utf-8':
                    # utf-8
                    if len(rtt_data) > 0:
                        self.bytes_data += bytes(rtt_data)
                        self.clk = int((6 / (self.rx_timeout * 1000)))
                    else:
                        if self.clk != 0:
                            self.clk -= 1
                    if self.clk == 0:
                        decoded_str = self.bytes_data.decode('utf-8', errors='ignore')
                        decoded_str = decoded_str.replace("\\n", "\n")
                        self.hw_data_handle(decoded_str)
                        self.bytes_data = b''
                else:
                    self.err_cb('J_Link: 不支持的数据格式%s.\n' % self.char_format)
        except Exception as e:
            self.err_cb('J_Link:%s\n' % e)


if __name__ == '__main__':
    pass
