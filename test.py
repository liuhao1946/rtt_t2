import PySimpleGUI as sg

# 定义布局
layout = [[sg.Text('请使用上下箭头键。')],
          [sg.Text(size=(15, 1), key='-OUTPUT-')],
          [sg.Button('退出')]]

# 创建窗口
window = sg.Window('键盘事件示例', layout)

# 事件循环
while True:
    event, values = window.read()
    print(event)
    if event == sg.WIN_CLOSED or event == '退出':
        break
    elif event == 'Up':
        window['-OUTPUT-'].update('按下了上键')
    elif event == 'Down':
        window['-OUTPUT-'].update('按下了下键')

# 关闭窗口
window.close()
