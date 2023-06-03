import re
import threading
import math
from queue import Queue
from datetime import datetime

thread_lock = threading.Lock()


def find_key(s, key):
    """
    找到关键字对应的值

    :param s: 原始字符串
    :param key: 要找到的关键字
    :return: 没有找到，返回''，找到返回字符串值
    """
    key += '\([0-9]+\)'
    sub = re.search(key, s)
    if sub != None:
        x1, x2 = sub.span()
        s_data = re.sub('.+\(', '', sub.string[x1:x2], flags=re.S)
        s_data = re.sub('\)', '', s_data)

        return s_data
    else:
        return ''


def find_DT(s, key):
    """
    找到DF包含的字符串系数、字符串值

    :param s: 原始字符串
    :return: 如果找到，返回一个浮点型数值列表
    """
    sub1 = re.search('[^A-Za-z0-9]' + key + '\*{0,1}[0-9]*\(.*?\)', s)
    if sub1 is not None:
        x1, x2 = sub1.span()
        s_data = re.sub('.+\(', '', sub1.string[x1:x2])
        data = re.sub('\)', '', s_data).split(',')

        s_coe = '0'
        sub2 = re.search('[1-9]{1,2}\(', sub1.string[x1:x2])
        if sub2 is not None:
            x1, x2 = sub2.span()
            s_coe = re.sub('\(', '', sub2.string[x1:x2])

        return [float(v) / (10.0 ** int(s_coe)) for v in data]
    else:
        return []


class HardWareBase:
    def __init__(self, err_cb, tag_detect_timeout_s, read_rtt_data_interval_s, **kwargs):
        self.err_cb = err_cb

        self.raw_data_save = False

        self.timestamp_open = False
        self.rx_str = ''
        self.data_queue = Queue()
        self.thread_run_interval_s = read_rtt_data_interval_s
        self.tag_detect_timeout = self.tag_detect_timeout_init = tag_detect_timeout_s / self.thread_run_interval_s

    def hw_open(self, **kwargs):
        pass

    def hw_is_open(self):
        pass

    def hw_close(self):
        pass

    def hw_data_handle(self, s1):
        self.rx_str += s1
        if len(s1) > 0:
            if self.timestamp_open:
                t = '[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[0:-3] + '] '
                s1 = s1.replace('\n', '\n' + t)
            self.data_queue.put(s1)
            # print(int(s1[0], 16))

        s_total_len = len(self.rx_str)
        if s_total_len > 10:
            # print(s_total_len)
            tag_dlog = re.findall(r'TAG=DLOG2 .+\n{0,1}\|{0,1}.{0,3}[\n\|]', self.rx_str)

            for v in tag_dlog:
                self._dlog_pack_handle(v)

            if tag_dlog:
                tag_start_idx = 0
                # 找到最后一个完整tag，完整的tag与tag之间的内容全部删除
                for idx, v in enumerate(tag_dlog):
                    tag_idx = self.rx_str.find('TAG=DLOG2 ', tag_start_idx)
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

    def hw_write(self, data):
        pass

    def hw_para_init(self):
        self.rx_str = ''
        self.data_queue.queue.clear()

    def get_raw_data_state(self):
        return self.raw_data_save

    def _dlog_pack_handle(self, str_sub):
        pass

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
