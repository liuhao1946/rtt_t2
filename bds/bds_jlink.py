import pylink
from bds.hw_base import HardWareBase


def convert_numbers_to_string(numbers, byte_size=4):
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
        self.last_successful_sn = None  # 存储上一次成功连接的序列号

    def find_rtt_address(self, start_address, range_size):
        if start_address is not None:
            num_bytes = self.jlink.memory_read32(start_address,  (range_size // 4))
            mem_data = convert_numbers_to_string(num_bytes)
            return mem_data.find("SEGGER RTT")
        else:
            return -1

    def hw_open(self, speed=4000, chip='nRF52840_xxAA', reset_flag=True, start_address=None, range_size=0, sn_no=None):
        try:
            self.hw_para_init()
            self.speed = speed
            self.chip = chip

            # 如果没有提供 sn_no，先尝试使用上一次成功的序列号
            if sn_no is None and self.last_successful_sn is not None:
                try:
                    self.jlink.open(serial_no=self.last_successful_sn)
                except pylink.errors.JLinkException:
                    # 如果使用上一次的序列号失败，则使用默认参数重试
                    self.jlink.open()
            else:
                self.jlink.open(serial_no=sn_no)

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
                self.jlink.swo_flush()
                self.jlink.rtt_start(start_address)
                self.rtt_is_start = True
                print('jlink connect success...')
                # 保存成功连接的序列号
                self.last_successful_sn = self.jlink.serial_number
                return True  # 返回连接成功的标志
        except pylink.errors.JLinkException as e:
            self.err_cb('J_Link:%s\n' % e)
            print(e)
        return False  # 返回连接失败的标志

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
                elif self.char_format == 'gb2312':
                    # gb2312
                    if len(rtt_data) > 0:
                        self.bytes_data += bytes(rtt_data)
                        self.clk = int((6 / (self.rx_timeout * 1000)))
                    else:
                        if self.clk != 0:
                            self.clk -= 1
                    if self.clk == 0:
                        decoded_str = self.bytes_data.decode('gb2312', errors='ignore')
                        decoded_str = decoded_str.replace("\\n", "\n")
                        self.hw_data_handle(decoded_str)
                        self.bytes_data = b''
                else:
                    self.err_cb('J_Link: 不支持的数据格式%s.\n' % self.char_format)
        except Exception as e:
            self.err_cb('J_Link:%s\n' % e)


if __name__ == '__main__':
    pass
