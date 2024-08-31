import PySimpleGUI as sg
import tkinter as tk
from tkinter import ttk
import json
import os

# 模拟配置文件
CONFIG_FILE = 'test_config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {'user_input_data': ['测试数据1', '测试数据2', '测试数据3']}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def create_custom_combo(window, key, values, default_value, size):
    combo = ttk.Combobox(window[key].Widget.master, values=values, width=size[0])
    combo.set(default_value)
    
    # 创建右键菜单
    context_menu = tk.Menu(window[key].Widget.master, tearoff=0)
    context_menu.add_command(label="删除当前项")
    
    def show_menu(event):
        context_menu.post(event.x_root, event.y_root)
    
    combo.bind("<Button-3>", show_menu)
    
    # 替换PySimpleGUI的Combo为自定义的ttk.Combobox
    parent = window[key].Widget.master
    window[key].Widget.destroy()
    window[key].Widget = combo
    
    # 使用pack布局管理器
    combo.pack(expand=True, fill='x')
    
    return combo, context_menu

def main():
    sg.theme('DefaultNoMoreNagging')
    
    # 加载配置
    js_cfg = load_config()

    layout = [
        [sg.Text('输入数据:'), sg.Input(key='data_input', size=(30, 1))],
        [sg.Button('添加到历史', key='add_to_history')],
        [sg.Text('历史数据:'),
         sg.Combo(js_cfg['user_input_data'], default_value=js_cfg['user_input_data'][0] if js_cfg['user_input_data'] else '',
                  key='history_data', size=(30, 1), enable_events=True)],
        [sg.Multiline(size=(50, 10), key='output', disabled=True)],
        [sg.Button('退出')]
    ]

    window = sg.Window('历史数据测试', layout, finalize=True)

    # 创建自定义的Combobox和右键菜单
    combo, context_menu = create_custom_combo(window, 'history_data', js_cfg['user_input_data'],
                                              js_cfg['user_input_data'][0] if js_cfg['user_input_data'] else '',
                                              (30, 1))

    def delete_current_item():
        current_value = combo.get()
        if current_value in js_cfg['user_input_data']:
            js_cfg['user_input_data'].remove(current_value)
            combo['values'] = js_cfg['user_input_data']
            combo.set(js_cfg['user_input_data'][0] if js_cfg['user_input_data'] else '')
            save_config(js_cfg)
            window['output'].print(f'已删除: {current_value}')

    context_menu.entryconfigure("删除当前项", command=delete_current_item)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, '退出'):
            break

        if event == 'add_to_history':
            new_data = values['data_input'].strip()
            if new_data and new_data not in js_cfg['user_input_data']:
                js_cfg['user_input_data'].insert(0, new_data)  # 添加到列表开头
                combo['values'] = js_cfg['user_input_data']
                combo.set(new_data)
                save_config(js_cfg)
                window['output'].print(f'已添加新数据: {new_data}')
            window['data_input'].update('')  # 清空输入框

        if event == 'history_data':
            window['data_input'].update(combo.get())

    window.close()

if __name__ == '__main__':
    main()