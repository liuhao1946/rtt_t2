import json


# 将修改后的数据写回JSON文件
with open('config.json', 'r') as f:
    js_cfg = json.load(f)

print(js_cfg)