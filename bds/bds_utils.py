
import struct

def check_sum(src,sum_size = 8):
    s = 0
    for v in src:
        s += v
    if sum_size == 8:
        s = s % 256
    elif sum_size == 16:
        s = s % 65536
    return s

def list_to_bytes(lst):
    return b''.join(map(lambda x:int.to_bytes(x,1,'little'),lst))

def bytes_to_list(lst):
    return [v for v in lst]

def db_list_to_str(src):
    return ''.join(map(lambda x: hex(x)+',',src))

def list_to_str(src):
    return ''.join(map(lambda x: str(x),src))

def bytes_unpack_to_s16_litte(src):
    """
    将字节流转换为short int(2字节)
    :type src:  bytes
    :return: short int型的列表
    """
    return [struct.unpack('<h', src[i:i+2])[0] for i in range(0,len(src),2)]

def bytes_unpack_to_u32_litte(src):
    """
    将字节流转换为unsigned int(4字节)
    :type src:  bytes
    :return: short int型的列表
    """
    return [struct.unpack('<I', src[i:i+4])[0] for i in range(0,len(src),4)]

def bytes_unpack_to_float_litte(src):
    """
    将字节流转换为float(4字节)
    :type src:  bytes
    :return: float型的列表
    """
    return [struct.unpack('<f', src[i:i + 4])[0] for i in range(0, len(src), 4)]

def batch_enqueue(q,data):
    for v in data:
        q.put(v)

def batch_dequeue(q):
    return [q.get() for i in range(0,q.qsize())]

def bytes_to_str(b):
    """
    将bytes转换为字符串
    :param b: bytes
    :return: 字符串
    """
    return ''.join(map(lambda x: chr(x),b))
    #return str(b,'utf-8')

def str_to_bytes(s):
    return s.encode('utf-8')
