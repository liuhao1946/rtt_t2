byte_stream = b'\x01\x02\x03\x04\x05'
hex_string = byte_stream.hex()

# 每两个字符插入一个空格
hex_string = ' '.join([hex_string[i:i+2] for i in range(0, len(hex_string), 2)])

# 添加换行符
hex_string = ' ' + hex_string

print(hex_string)