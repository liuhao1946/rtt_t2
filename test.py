
def convert_numbers_to_string(numbers, byte_size=4):
    # 使用生成器表达式和字节串拼接
    byte_seq = (number.to_bytes(byte_size, 'little', signed=False) for number in numbers)
    return ''.join(map(lambda b: ''.join(chr(x) for x in b), byte_seq))

a = [0x31313132]


print(convert_numbers_to_string(a))

