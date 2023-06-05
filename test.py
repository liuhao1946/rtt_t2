import PySimpleGUI as sg

# 定义布局
layout = [
    [sg.Column([
        [sg.Text('Combo', size=(10, 1)), sg.Combo(['Option 1', 'Option 2'], size=(10, 1))],
        [sg.Text('Button', size=(10, 1)), sg.Button('Click', size=(10, 1))]
    ])],
    [sg.Multiline(size=(20, 5))],
    [sg.Button('Exit')]
]

# 创建窗口
window = sg.Window('GUI Layout', layout)

# 事件循环
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break

# 关闭窗口
window.close()
