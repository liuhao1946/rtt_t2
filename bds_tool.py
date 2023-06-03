import PySimpleGUI as sg
import json
import logging as log
import threading
import time
import re
from bds.hw_base import find_key
import datetime
import bds.bds_jlink as bds_jk
import bds.bds_serial as bds_ser
import bds.bds_waveform as wv

global window
global hw_obj
global log_remain_str
global real_time_save_file_name


thread_lock = threading.Lock()

DB_OUT = 'db_out' + sg.WRITE_ONLY_KEY


def hw_rx_thread():
    # global last_time1
    # last_time1 = 0
    while True:
        try:
            thread_lock.acquire()
            hw_obj.hw_read()
            run_interval_s = hw_obj.get_read_data_time_interval_s()
        finally:
            thread_lock.release()
        time.sleep(run_interval_s)


def hw_interface_config_dialog(js_cfg):
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
                  sg.T('speed(kHz)'), sg.In(jk_speed, key='jk_sn', size=(5, 1))],
                 [sg.Checkbox('连接时复位', default=True, key='jk_reset', font=js_cfg['font'][0])]
                 ]
    # 串口配置
    ser_layout = [[sg.T('串口'),
                   sg.Combo(ser_list, default_value=ser_list[0], key='ser_num', readonly=True, size=(25, 1)),
                   sg.T('波特率', pad=((45, 5), (5, 5))),
                   sg.Combo(baud_list, default_value=baud_list[0], key='baud', size=(10, 1), pad=((5, 5), (5, 5)))
                   ]
                  ]

    dialog_layout = [[sg.Frame('接口选择', interface_layout)],
                     [sg.Frame('J_Link配置', jk_layout)],
                     [sg.Frame('串口配置', ser_layout)],
                     [sg.Button('保存', key='save', pad=((250, 5), (10, 10)), size=(8, 1)),
                      sg.Button('取消', key='clean', pad=((20, 5), (10, 10)), size=(8, 1))]
                     ]

    cfg_window = sg.Window('硬件接口配置', dialog_layout, modal=True)

    while True:
        d_event, d_values = cfg_window.read()

        if d_event == sg.WINDOW_CLOSED or d_event == 'clean':
            break
        elif d_event == 'save':
            # 将芯片信号写入第一个位置
            chip_name = cfg_window['chip'].get()
            if chip_name in js_cfg['jk_chip']:
                js_cfg['jk_chip'].remove(chip_name)
            js_cfg['jk_chip'].insert(0, chip_name)

            with open('config.json', 'w') as f:
                json.dump(js_cfg, f, indent=4)
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


def filter_config_dialog(js_cfg):
    # 过滤配置
    filter_layout = [[sg.T('过滤1'), sg.In(js_cfg['filter'][0], key='fileter1', size=(48, 1)),
                      sg.Checkbox('', default=False, key='fileter1_en')],
                     [sg.T('过滤2'), sg.In(js_cfg['filter'][1], key='fileter2', size=(48, 1)),
                      sg.Checkbox('', default=False, key='fileter2_en')],
                     [sg.T('过滤3'), sg.In(js_cfg['filter'][2], key='fileter3', size=(48, 1)),
                      sg.Checkbox('', default=False, key='fileter3_en')],
                     [sg.T('过滤4'), sg.In(js_cfg['filter'][3], key='fileter4', size=(48, 1)),
                      sg.Checkbox('', default=False, key='fileter4_en')],
                     [sg.T('过滤5'), sg.In(js_cfg['filter'][4], key='fileter5', size=(48, 1)),
                      sg.Checkbox('', default=False, key='fileter5_en')],
                     ]

    dialog_layout = [[sg.Frame('过滤配置', filter_layout)],
                     [sg.Button('保存', key='f_save', pad=((250, 5), (10, 10)), size=(8, 1)),
                      sg.Button('取消', key='f_clean', pad=((20, 5), (10, 10)), size=(8, 1))]
                     ]

    cfg_window = sg.Window('过滤配置', dialog_layout, modal=True)

    while True:
        d_event, d_values = cfg_window.read()
        if d_event == sg.WINDOW_CLOSED or d_event == 'f_clean':
            break
        elif d_event == 'f_save':
            js_cfg['filter'] = [cfg_window[f'fileter{i}'].get() for i in range(1, 6)]
            js_cfg['filter_en'] = [cfg_window[f'fileter{i}_en'].get() for i in range(1, 6)]
            with open('config.json', 'w') as f:
                json.dump(js_cfg, f, indent=4)
            break

    cfg_window.close()


def hw_error(err):
    window.write_event_value('hw_error', err)


def update_connect_button_text(win, hw_sel):
    if hw_sel == '1':
        win['connect'].update('J_Link连接')
    elif hw_sel == '2':
        win['connect'].update('串口连接')


def delete_str(pat, s, reverse=False, s_sub=''):
    """
    删除字符串s中符合模式串的子串

    :param pat: 模式串
    :param s: 要处理的字符串
    :param reverse: reverse=True，提取符合模式串的子串后，保留有s_sub的子串，删除没有s_sub的子串
                    reverse=False，删除符合模式串的子串
    :param s_sub: 如果reverse=False，这个参数没有意义。如果reverse=True，参考reverse

    :return: 返回删除后的字符串

    example：

    s = 'SN(666)SN(555)TABTEST\nSN(123)SN(456)TABTEST\nSN(666)SN(555)TABTEST\nSN(123)SN(555)TABTEST\n123'

    delete_str('SN.+\n', s)

    结果: '123'

    delete_str('SN.+\n',s,reverse=True,s_sub='123')

    结果: 'SN(123)SN(456)TABTEST\nSN(123)SN(555)TABTEST\n123'
    """
    x = 0
    while True:
        sub = re.search(pat, s[x:])
        if sub is not None:
            x1, x2 = sub.span()
            if not reverse:
                s = s.replace(s[x1:x2], '')
            else:
                if s[x1 + x:x2 + x].find(s_sub) < 0:
                    s = s.replace(s[x1 + x:x2 + x], '')
                else:
                    x += x2
        else:
            break

    return s


def db_data_check_error(s):
    err_cnt = 0
    err_chr = chr(0)
    for v in s:
        # ~-127
        if v > '~' or v == err_chr:
            err_cnt += 1
            if err_cnt > 100:
                return True

    return False


def log_filter(win, s):
    return s


def log_data_display(win, obj, auto_scroll=True, color=True):
    global log_remain_str

    log_data = []
    obj.read_data_queue(log_data)

    raw_s = ''
    s = log_remain_str
    log_remain_str = ''
    for v in log_data:
        s += v
        raw_s += v

    log_split = s.split('\n')
    data_len = len(log_split)
    s1 = ''
    for idx, v in enumerate(log_split):
        if data_len > 1:
            if v != '':
                if idx != data_len - 1:
                    v += '\n'
                    v = log_filter(win, v)
                    s1 += v
                else:
                    # 最后一个要么是空，要么是没有换行符的字符串，此时都连接到rtt_data_str
                    log_remain_str = v
            else:
                # 如果中间存在连续多个换行符，就存在连续多个空字符串，因此，除最后一个以外都要附带换行
                if idx != data_len - 1:
                    v += '\n'
        else:
            log_remain_str = v

    # 数据错误检查
    if not db_data_check_error(s1):
        # a = time.time()
        if color:
            sv = ''
            color = 0
            pre_color = -1
            line_tag = re.findall('.+\n', s1)
            for idx, v in enumerate(line_tag):
                v_idx = v.find('BDSCOL(')
                if v_idx < 0:
                    if pre_color >= 0:
                        sg.cprint(sv, text_color='#%06X' % pre_color, end='', autoscroll=auto_scroll)
                        sv = ''
                        pre_color = -1
                    sv += v
                    color = -1
                else:
                    if sv != '' and color == -1:
                        # 按照默认色打印
                        sg.cprint(sv, text_color='#%06X' % 0, end='', autoscroll=auto_scroll)
                        sv = ''
                    try:
                        color = int(find_key(v, 'BDSCOL'))
                    except Exception as e:
                        win[DB_OUT].write('[BDS LOG]RAW string:%s,color error:%s,error code:%s\n' % (raw_s, v, e))
                        log.info('RAW string:%s,color error:%s,error code:%s\n' % (raw_s, v, e))
                        color = 0
                    if pre_color < 0:
                        pre_color = color
                    if color == pre_color:
                        sv += delete_str('BDSCOL\([0-9]{1,8}\)', v)
                    else:
                        # 输出上一个颜色的字符串
                        sg.cprint(sv, text_color='#%06X' % pre_color, end='', autoscroll=auto_scroll)
                        sv = delete_str('BDSCOL\([0-9]{1,8}\)', v)
                    pre_color = color
            if color < 0:
                color = 0
            if sv != '':
                sg.cprint(sv, text_color='#%06X' % color, end='', autoscroll=auto_scroll)
        else:
            win[DB_OUT].write(s1)
        # b = time.time()
        # delta = '%03d' % ((b - a) * 1000)
        # print(delta)
        if win['real_time_save_data'].get_text() == '关闭实时保存数据':
            try:
                with open(real_time_save_file_name, 'a', encoding='utf-8') as f:
                    f.write(raw_s)
            except Exception as e:
                log.info('Write real time data to file error[%s]\n' % e)
    else:
        win[DB_OUT].write("RTT数据出错，可能需要重启设备！ + " + "error data:[" + s1[0:20] + "]\n")
        log.info("RTT数据出错，可能需要重启设备！ + " + "error data:[" + s1[0:20] + "]\n")


def jk_connect(win, obj, jk_cfg):
    if win['connect'].get_text() == 'J_Link连接':
        try:
            jk_con_reset = True if jk_cfg['jk_con_reset'] == '1' else False
            try:
                jk_speed = int(jk_cfg['jk_speed'])
            except:
                jk_speed = 4000
            obj.hw_open(speed=jk_speed, chip=jk_cfg['jk_chip'][0], reset_flag=jk_con_reset)
            if obj.hw_is_open():
                win['connect'].update('J_Link断开', button_color=('grey0', 'green4'))
                win[DB_OUT].write('[J_Link LOG]sn:%d\n' % obj.get_hw_serial_number())
                if jk_con_reset:
                    win[DB_OUT].write('[J_Link LOG]J_Link复位MCU.\n')
                log.info('J_Link连接成功')
                # 每次连接后复位波形.波形是否立即复位取决于波形进程是否已经再运行
                # wv.wave_pro_acc_cmd('wave reset')
            else:
                win[DB_OUT].write('[J_Link LOG]J_Link打开失败\n')
        except Exception as e:
            obj.hw_close()
            log.info('J_Link打开失败' + str(e))
            win[DB_OUT].write('[J_Link LOG]Error:%s\n' % e)
            win['connect'].update('J_Link连接')
    else:
        obj.hw_close()
        win['connect'].update('J_Link连接', button_color=('grey0', 'grey100'))
        log.info('J_Link断开连接')
        time.sleep(0.1)


def main():
    log.basicConfig(filename='alg-tool.log', filemode='w', level=log.INFO, format='%(asctime)s %(message)s',
                    datefmt='%Y/%m/%d %I:%M:%S')

    # 读取json配置文件
    with open('config.json', 'r') as f:
        js_cfg = json.load(f)

    font = js_cfg['font'][0] + ' '
    font_size = js_cfg['font_size']

    menu_def = [['配置', ['接口选择', '过滤配置']],
                ['工具', ['绘制波形图']],
                ['关于']
                ]

    right_click_menu = ['', ['清除窗口数据', '滚动到最底端']]

    layout = [[sg.Menu(menu_def, )],
              [sg.Button('J_Link连接', key='connect', size=(10, 1), font=font, button_color=('grey0', 'grey100')),
               sg.Button('打开时间戳', font=font, button_color=('grey0', 'grey100'), key='open_timestamp'),
               sg.Button('实时保存数据', font=font, size=(14, 1), button_color=('grey0', 'grey100'),
                         key='real_time_save_data'),
               sg.Button('保存全部数据', font=font, button_color=('grey0', 'grey100'), key='save_all_data'),
               sg.Button('一键跳转', font=font, button_color=('grey0', 'grey100'), key='skip_to_file')],
              [sg.Multiline(autoscroll=True, key=DB_OUT, size=(100, 26), right_click_menu=right_click_menu,
                            font=(font + font_size + ' bold'))]
              ]

    global window
    global hw_obj
    global real_time_save_file_name
    global log_remain_str

    window = sg.Window('v1.0.0', layout, finalize=True, resizable=True)
    update_connect_button_text(window, js_cfg['hw_sel'])

    jk_obj = bds_jk.BDS_Jlink(hw_error)
    hw_obj = jk_obj
    threading.Thread(target=hw_rx_thread, daemon=True).start()

    mul_scroll = False
    real_time_save_file_name = ''
    log_remain_str = ''

    sg.cprint_set_output_destination(window, DB_OUT)

    while True:
        event, values = window.read(timeout=150)
        print(event)

        if event == sg.WIN_CLOSED:
            hw_obj.hw_close()
            break

        # Sliding control of log window
        y1, y2 = window[DB_OUT].get_vscroll_position()
        if mul_scroll and bool(1 - y2):
            mul_scroll = False
            window[DB_OUT].update(autoscroll=False)
        elif not mul_scroll and y2 == 1:
            mul_scroll = True
            window[DB_OUT].update(autoscroll=True)

        # GUI event response
        if event == '接口选择':
            hw_interface_config_dialog(js_cfg)
            update_connect_button_text(window, js_cfg['hw_sel'])

            # 获得json配置
            # 如果处于连接状态，需要让部分选择框禁用
        elif event == '过滤配置':
            filter_config_dialog(js_cfg)
        elif event == 'hw_error':
            sg.popup(values['hw_error'])
        elif event == 'connect':
            if window['connect'].get_text().find('J_Link') >= 0:
                thread_lock.acquire()
                hw_obj = jk_obj
                thread_lock.release()
                jk_connect(window, hw_obj, js_cfg)
            elif window['connect'].get_text().find('串口') >= 0:
                pass
            elif event == 'real_time_save_data':
                if window['real_time_save_data'].get_text() == '实时保存数据':
                    window['real_time_save_data'].update('关闭实时保存数据', button_color=('grey0', 'green4'))
                    real_time_save_file_name = 'aaa_log\\' + 'real_time_log_' + datetime.datetime.now().strftime(
                        '%Y-%m-%d-%H-%M-%S') + '.txt'
                else:
                    window['real_time_save_data'].update('实时保存数据', button_color=('grey0', 'grey100'))

        log_data_display(window, hw_obj, auto_scroll=mul_scroll)

    window.close()


if __name__ == '__main__':
    main()
