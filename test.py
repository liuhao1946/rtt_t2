import PySimpleGUI as sg

# 定义窗口的布局
layout = [[sg.Button("OK")]]

# 创建窗口
window = sg.Window("Demo", layout, finalize=True)

# # 创建事件循环
# while True:
#     event, values = window.read()
#     # 如果用户关闭窗口或点击“OK”按钮，则结束循环
#     if event == "OK" or event == sg.WIN_CLOSED:
#         break

# 关闭窗口
window.close()
