import PySimpleGUI as sg
import time
import gc

def create_find_window(font=None):
    find_layout = [[sg.Text("查找内容:", font=font)],
                   [sg.Input(key='find_key', font=font, size=(50, 1)),
                    sg.Button("查找下一个", font=font, pad=((10, 10), (5, 5)), key='find',
                              button_color=('grey0', 'grey100'))],
                   [sg.Button("关闭", font=font)]]
    return sg.Window("查找", find_layout, modal=True, font=font, icon=APP_ICON, finalize=True)

def main_window():
    layout = [[sg.Text("主窗体", font=font)],
              [sg.Button("打开查找窗体", font=font, key='open_find')]]
    return sg.Window("主窗体", layout, font=font, icon=APP_ICON, finalize=True)

font = "Helvetica 12"  # 示例字体
APP_ICON = None  # 示例图标，需要替换为实际路径或变量

# 创建并显示主窗体
main_win = main_window()

# 事件循环
while True:
    window, event, values = sg.read_all_windows()

    # 当用户关闭窗口
    if event == sg.WINDOW_CLOSED and window == main_win:
        break

    # 当用户点击 "打开查找窗体" 按钮
    if event == 'open_find':
        find_win = create_find_window(font)
        continue

    # 当用户关闭查找窗体
    if window == find_win and event in (sg.WINDOW_CLOSED, '关闭'):
        find_win.close()

# 关闭主窗体
main_win.close()
gc.collect()
