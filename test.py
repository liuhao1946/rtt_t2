import datetime


def add_timestamp1(s1):
    s1 = s1.replace('\r\n', '\n').replace('\r', '')  # 将所有的\r\n 和 \r 转换为 ''
    t = '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[0:-3] + '] '
    lines = s1.splitlines(keepends=True)
    s1 = ''.join([t + line for line in lines])
    return s1

print(add_timestamp1("qw123afafaf\r\n\r\r\r\nnnsfsdjfh"))

