import json

# 读取JSON文件
with open('config.json', 'r') as f:
    data = json.load(f)

# 在'chip'字段中添加新的字符串
data['chip'].append('STM32XX')

# 将修改后的数据写回JSON文件
with open('config.json', 'w') as f:
    json.dump(data, f, indent=4)
