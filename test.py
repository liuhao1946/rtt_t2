import datetime
import time


def add_timestamp1_v1(s1):
    s1 = s1.replace('\r\n', '\n').replace('\r', '')  # 标准化换行符
    timestamp = '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + '] '
    lines = s1.splitlines(keepends=True)  # 保留行分隔符
    result = []
    buffer = ""

    for line in lines:
        if line.endswith('\n'):
            if buffer:
                line = buffer + line  # 合并前一部分不完整的行
                buffer = ""
            result.append(timestamp + line)
        else:
            buffer += line  # 将不完整的行暂时存放在缓冲区
            result.append(buffer)  # 直接将不完整行加入结果

    return ''.join(result)


def add_timestamp1_v2(s1):
    s1 = s1.replace('\r\n', '\n').replace('\r', '')  # 标准化换行符
    timestamp = '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + '] '
    lines = s1.splitlines(keepends=True)  # 保留行分隔符
    timestamped_lines = []
    buffer = []

    for line in lines:
        if line.endswith('\n'):
            if buffer:
                buffer.append(line)  # 合并前一部分不完整的行
                timestamped_lines.append(timestamp + ''.join(buffer))
                buffer = []
            else:
                timestamped_lines.append(timestamp + line)
        else:
            buffer.append(line)  # 将不完整的行暂时存放在缓冲区

    remainder = ''.join(buffer)

    return ''.join(timestamped_lines), remainder


# 测试数据
s1 = "这是第一行完整的字符串\n这是第二行不完整的字符串" * 1000000

# 测试第一个方案
start_time = time.time()
add_timestamp1_v1(s1)
end_time = time.time()
print("First version time:", end_time - start_time)

# 测试第二个方案
start_time = time.time()
add_timestamp1_v2(s1)
end_time = time.time()
print("Second version time:", end_time - start_time)
