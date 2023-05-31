import PySimpleGUI as sg
import json
import logging as log

DB_OUT = 'db_out' + sg.WRITE_ONLY_KEY


def dialog_config(js_cfg):
    # 从json文件中读取默认配置
    # 退出后写入json文件
    # 遍历串口

    interface_sel = js_cfg['hw_sel']
    chip_list = js_cfg['jk_chip']
    jk_speed = js_cfg['jk_speed']
    ser_list = ['COM1']
    baud_list = ['115200']

    jk_sel = False
    ser_sel = False
    if interface_sel == '1':
        jk_sel = True
    else:
        ser_sel = True

    # 接口选择
    interface_layout = [[sg.Radio('J_Link', 'radio1', key='jk_radio', default=jk_sel, enable_events=True),
                         sg.Radio('串口', 'radio2', key='ser_radio', default=ser_sel, enable_events=True)]]
    # jlink配置
    jk_layout = [[sg.Combo(chip_list, chip_list[0], readonly=True, key='chip', size=(18, 1)),
                  sg.Text('SN'), sg.Input('', readonly=True, key='jk_sn', size=(15, 1)),
                  sg.T('speed(kHz)'), sg.In(jk_speed, key='jk_sn', size=(5, 1))
                  ]
                 ]
    # 串口配置
    ser_layout = [[sg.T('串口'),
                   sg.Combo(ser_list, default_value=ser_list[0], key='ser_num', readonly=True, size=(25, 1)),
                   sg.T('波特率', pad=((45, 5), (5, 5))),
                   sg.Combo(baud_list, default_value=baud_list[0], key='baud', size=(10, 1), pad=((5, 5), (5, 5)))
                   ]
                  ]
    # 过滤配置
    filter_layout = [[sg.T('过滤1'), sg.In(js_cfg['filter'][0], key='fileter1', size=(50, 1))],
                     [sg.T('过滤2'), sg.In(js_cfg['filter'][1], key='fileter2', size=(50, 1))],
                     [sg.T('过滤3'), sg.In(js_cfg['filter'][2], key='fileter3', size=(50, 1))],
                     [sg.T('过滤4'), sg.In(js_cfg['filter'][3], key='fileter4', size=(50, 1))],
                     [sg.T('过滤5'), sg.In(js_cfg['filter'][4], key='fileter5', size=(50, 1))],
                     ]

    dialog_layout = [[sg.Frame('接口选择', interface_layout)],
                     [sg.Frame('J_Link配置', jk_layout)],
                     [sg.Frame('串口配置', ser_layout)],
                     [sg.Frame('过滤配置', filter_layout)],
                     [sg.Button('保存', key='save', pad=((250, 5), (10, 10)), size=(8, 1)),
                      sg.Button('取消', key='clean', pad=((20, 5), (10, 10)), size=(8, 1))]
                     ]

    cfg_window = sg.Window('配置项', dialog_layout, modal=True)

    while True:
        d_event, d_values = cfg_window.read()

        if d_event == sg.WINDOW_CLOSED:
            break
        elif d_event == 'save':
            js_cfg['filter'] = [cfg_window[f'fileter{i}'].get() for i in range(1, 6)]
            with open('config.json', 'w') as f:
                json.dump(js_cfg, f, indent=4)
            break
        elif d_event == 'clean':
            break
        elif d_event == 'jk_radio':
            cfg_window['jk_radio'].update(True)
            cfg_window['ser_radio'].update(False)
            js_cfg['hw_sel'] = '1'
        elif d_event == 'ser_radio':
            cfg_window['jk_radio'].update(False)
            cfg_window['ser_radio'].update(True)
            js_cfg['hw_sel'] = '2'

    cfg_window.close()


def main():
    log.basicConfig(filename='alg-tool.log', filemode='w', level=log.INFO, format='%(pastime)s %(message)s',
                    datefmt='%Y/%m/%d %I:%M:%S')

    # 读取json配置文件
    with open('config.json', 'r') as f:
        js_cfg = json.load(f)

    font = js_cfg['font'][0] + ' '
    font_size = js_cfg['font_size']

    menu_def = [['配置', ['打开配置项']],
                ['工具', ['绘制波形图']],
                ['关于']
                ]

    right_click_menu = ['', ['清除窗口数据', '滚动到最底端']]

    layout = [[sg.Menu(menu_def, )],
              [sg.Button('连接'), sg.Button('打开时间戳'), sg.Button('实时保存数据'),
               sg.Button('保存全部数据'), sg.Button('一键跳转')],
              [sg.Multiline(autoscroll=True, key=DB_OUT, size=(100, 26), right_click_menu=right_click_menu,
                            font=(font + font_size + ' bold'))]
              ]

    window = sg.Window('v1.0.0', layout, finalize=True, resizable=True)

    while True:
        event, values = window.read()
        print(event)

        if event == sg.WIN_CLOSED:
            # obj.hw_close()
            break
        elif event == '打开配置项':
            dialog_config(js_cfg)
            # 获得json配置
            # 如果处于连接状态，需要让部分选择框禁用

    window.close()


if __name__ == '__main__':
    main()
