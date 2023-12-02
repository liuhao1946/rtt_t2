import re
import threading
from queue import Queue
from datetime import datetime
import binascii

thread_lock = threading.Lock()


def find_key(text, key):
    pattern = fr"{key}\((\d+)\)"
    match = re.search(pattern, text)
    if match:
        sn_value = int(match.group(1))
        return sn_value
    return None


def find_group(text, key):
    pattern = fr"{key}\*(\d+)\((-?\d+\.?\d*),(-?\d+\.?\d*),(-?\d+\.?\d*)\)"
    match = re.search(pattern, text)
    if match:
        n = int(match.group(1))
        x = int(match.group(2))/(10**n) if n != 0 else int(match.group(2))
        y = int(match.group(3))/(10**n) if n != 0 else int(match.group(3))
        z = int(match.group(4))/(10**n) if n != 0 else int(match.group(4))
        return [x, y, z]
    return []


class HardWareBase:
    def __init__(self, err_cb, warn_cb, tag_detect_timeout_s, read_rtt_data_interval_s, char_format, **kwargs):
        self.err_cb = err_cb
        self.warn_cb = warn_cb
        self.raw_data_save = False
        self.timestamp_open = False
        self.rx_str = ''
        self.char_format = char_format
        self.data_queue = Queue()
        self.M_cb = []
        self.thread_run_interval_s = read_rtt_data_interval_s
        self.tag_detect_timeout = self.tag_detect_timeout_init = tag_detect_timeout_s / self.thread_run_interval_s

    def hw_open(self, **kwargs):
        pass

    def hw_is_open(self):
        pass

    def hw_close(self):
        pass

    def hw_set_char_format(self, c_format):
        self.char_format = c_format

    def hw_data_handle(self, s1):
        self.rx_str += s1
        if len(s1) > 0:
            if self.timestamp_open:
                t = '[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[0:-3] + '] '
                lines = s1.splitlines(keepends=True)
                s1 = ''.join([t + line for line in lines])
            self.data_queue.put(s1)

        s_total_len = len(self.rx_str)
        if s_total_len > 10:
            tag_dlog = re.findall(r"(TAG=DLOG.+?\n)", self.rx_str)

            for v in tag_dlog:
                self.dlog_pack_handle(v)

            if tag_dlog:
                tag_start_idx = 0
                # 找到最后一个完整tag，完整的tag与tag之间的内容全部删除
                for idx, v in enumerate(tag_dlog):
                    tag_idx = self.rx_str.find('TAG=DLOG', tag_start_idx)
                    tag_start_idx = tag_idx + len(v)
                if tag_start_idx < s_total_len:
                    self.rx_str = self.rx_str[tag_start_idx:]
                else:
                    self.rx_str = ''

            if tag_dlog:
                self.tag_detect_timeout = self.tag_detect_timeout_init
            if self.tag_detect_timeout:
                self.tag_detect_timeout = self.tag_detect_timeout - 1
            else:
                self.rx_str = ''

    def hw_data_hex_handle(self, byte_stream):
        if byte_stream != b'':
            hex_string = binascii.hexlify(byte_stream).decode()
            hex_string = ' '.join([hex_string[i:i + 2] for i in range(0, len(hex_string), 2)])
            self.data_queue.put(' ' + hex_string + '\n')

    def hw_write(self, data):
        pass

    def hw_para_init(self):
        self.rx_str = ''
        self.data_queue.queue.clear()

    def get_raw_data_state(self):
        return self.raw_data_save

    def reg_dlog_M_callback(self, cb):
        self.M_cb.append(cb)

    def dlog_pack_handle(self, sub):
        try:
            thread_lock.acquire()
            raw_data = find_group(sub, 'M')

            if len(raw_data) >= 3:
                for _, cb in enumerate(self.M_cb):
                    # print(raw_data, len(self.M_cb))
                    cb(raw_data)
        except Exception as e:
            self.warn_cb('re data error:[%s]\n' % e)
        finally:
            thread_lock.release()

    def get_hw_serial_number(self):
        pass

    def open_timestamp(self):
        self.timestamp_open = True

    def close_timestamp(self):
        self.timestamp_open = False

    def get_read_data_time_interval_s(self):
        return self.thread_run_interval_s

    def read_data_queue(self, data):
        q_size = self.data_queue.qsize()
        for _ in range(0, q_size):
            data.append(self.data_queue.get())


if __name__ == '__main__':
    pass
