import datetime


def add_timestamp(s1):
    t = '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[0:-3] + '] '
    lines = s1.splitlines(keepends=True)
    s1 = ''.join([t + line.rstrip('\r\n') + line[-2:] for line in lines])
    return s1

def add_timestamp1(s1):
    t = '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[0:-3] + '] '
    lines = s1.splitlines(keepends=True)
    #lines.append('123')
    #print(lines)
    s1 = ''.join([t + line for line in lines])
    return s1



# print(add_timestamp("afafaf\nnnsfsdjfh\nkjdkgfjk\r\n"))
print(add_timestamp1("\nafafaf\n \nnnsfsdjfh\nkjdkgfjk 123"))
