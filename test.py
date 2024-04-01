import json
import re


def extract_outside_brackets_corrected(text):
    """
    提取字符串中括号外的文本。
    """
    pattern = r'\([^)]*\)|（[^）]*）'
    return re.sub(pattern, '', text).strip()


def update_user_input_list(input_data, user_input_list):
    """
    更新用户输入列表，确保括号外的文本不重复。
    如果找到括号外文本相同的旧数据，将其删除。
    然后将新数据添加到列表前面，并保持列表长度不超过30。
    """
    input_data_outside_brackets = extract_outside_brackets_corrected(input_data)
    user_input_list = [item for item in user_input_list if item != '']  # 删除空字符串

    # 查找并删除任何括号外文本相同的旧数据
    for item in user_input_list:
        if extract_outside_brackets_corrected(item) == input_data_outside_brackets:
            user_input_list.remove(item)
            break

    if len(user_input_list) >= 2:
        user_input_list.pop(-1)
    user_input_list.insert(0, input_data)

    return user_input_list


def save_to_config(user_input_list, config_path='config.json'):
    """
    将更新后的用户输入列表保存到配置文件中。
    """
    with open(config_path, 'w') as f:
        json.dump({'user_input_data': user_input_list}, f, indent=4)


def update_gui(window, user_input_list):
    """
    更新GUI元素，显示最新的用户输入列表。
    """
    window['history_data'].update(values=user_input_list)


# 示例使用
js_cfg = {'user_input_data': ['123']}
input_data = 'example（测1冲）'  # 假设这是用户的新输入

# 更新用户输入列表
updated_list = update_user_input_list(input_data, js_cfg['user_input_data'])

print(updated_list)

js_cfg = updated_list
print(js_cfg)
# 保存到配置文件
# save_to_config(updated_list)

# 更新GUI（这里假设`window`是你的GUI窗口变量）
# update_gui(window, updated_list)
