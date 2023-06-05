import PySimpleGUI as sg
import json
import logging as log
import threading
import time
import re
from bds.hw_base import find_key
import datetime
import os
import bds.bds_jlink as bds_jk
import multiprocessing
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
                      sg.Checkbox('', default=js_cfg['filter_en'][0], key='fileter1_en')],
                     [sg.T('过滤2'), sg.In(js_cfg['filter'][1], key='fileter2', size=(48, 1)),
                      sg.Checkbox('', default=js_cfg['filter_en'][1], key='fileter2_en')],
                     [sg.T('过滤3'), sg.In(js_cfg['filter'][2], key='fileter3', size=(48, 1)),
                      sg.Checkbox('', default=js_cfg['filter_en'][2], key='fileter3_en')],
                     [sg.T('过滤4'), sg.In(js_cfg['filter'][3], key='fileter4', size=(48, 1)),
                      sg.Checkbox('', default=js_cfg['filter_en'][3], key='fileter4_en')],
                     [sg.T('过滤5'), sg.In(js_cfg['filter'][4], key='fileter5', size=(48, 1)),
                      sg.Checkbox('', default=js_cfg['filter_en'][4], key='fileter5_en')],
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
    """
    matches = re.findall(pat, s)
    if reverse:
        matches = [match for match in matches if s_sub in match]
    for match in matches:
        s = s.replace(match, '')
    return s


def remove_lines(patterns, text):
    """
    删除包含模式列表中的字符串的行

    :param patterns: 要匹配的模式列表
    :param text: 要处理的文本

    :return: 返回删除包含模式的行后的文本
    """
    lines = text.split('\n')
    filtered_lines = []
    for line in lines:
        if not any(pattern in line for pattern in patterns):
            filtered_lines.append(line)
    return '\n'.join(filtered_lines)


def log_fileter(log_data, filter_pat, remain_str=''):
    raw_s = remain_str + ''.join(log_data)
    log_lines = raw_s.split('\n')
    filtered_lines = []

    last_index = len(log_lines) - 1
    for idx, line in enumerate(log_lines):
        if line or (idx == last_index and not line.endswith('\n')):
            filtered_line = remove_lines(filter_pat, line + '\n')
            filtered_lines.append(filtered_line)

    new_s = ''.join(filtered_lines)
    updated_remain_str = log_lines[last_index] if not log_lines[last_index].endswith('\n') else ''

    return new_s, updated_remain_str


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


def log_print_line(win, s, auto_scroll=True):
    sv = ''
    color = 0
    pre_color = -1
    line_tag = re.findall('.+\n', s)
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
                win[DB_OUT].write('[BDS LOG]RAW string:%s,color error:%s,error code:%s\n' % (s, v, e))
                log.info('RAW string:%s,color error:%s,error code:%s\n' % (s, v, e))
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


def log_process(win, obj, js_cfg, auto_scroll=True):
    global log_remain_str

    filter_pat = [value for value, flag in zip(js_cfg['filter'], js_cfg['filter_en']) if flag]

    # read log data
    raw_log = []
    obj.read_data_queue(raw_log)
    # filter log
    new_log, log_remain_str = log_fileter(raw_log, filter_pat, log_remain_str)

    if not db_data_check_error(new_log):
        # print log to GUI
        log_print_line(win, new_log, auto_scroll)
        # save log to file
        if win['real_time_save_data'].get_text() == '关闭实时保存数据':
            try:
                with open(real_time_save_file_name, 'a', encoding='utf-8') as f:
                    f.write(new_log)
            except Exception as e:
                log.info('Write real time data to file error[%s]\n' % e)
    else:
        win[DB_OUT].write("RTT数据出错，可能需要重启设备！ + " + "error data:[" + new_log[0:20] + "]\n")
        log.info("RTT数据出错，可能需要重启设备！ + " + "error data:[" + new_log[0:20] + "]\n")


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
                win[DB_OUT].write('[J_Link LOG]过滤配置:%s\n' % ','.join(jk_cfg['filter']))
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
    multiprocessing.freeze_support()

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

    tx_data_type = ['ASC', 'HEX']
    right_click_menu = ['', ['清除窗口数据', '滚动到最底端']]

    tx_data_layout = [[sg.Button('发送数据', key='tx_data', pad=((5, 5), (5, 15)), size=(8, 1))],
                      [sg.Combo(tx_data_type, tx_data_type[0], readonly=True, key='tx_data_type', size=(8, 1))]]

    layout = [[sg.Menu(menu_def, )],
              [sg.Button('J_Link连接', key='connect', size=(10, 1), font=font, button_color=('grey0', 'grey100')),
               sg.Button('打开时间戳', font=font, button_color=('grey0', 'grey100'), key='open_timestamp'),
               sg.Button('实时保存数据', font=font, size=(14, 1), button_color=('grey0', 'grey100'),
                         key='real_time_save_data'),
               sg.Button('保存全部数据', font=font, button_color=('grey0', 'grey100'), key='save_all_data'),
               sg.Button('一键跳转', font=font, button_color=('grey0', 'grey100'), key='skip_to_file')],
              [sg.Multiline(autoscroll=True, key=DB_OUT, size=(100, 25), right_click_menu=right_click_menu,
                            font=(font + font_size + ' bold'))],

              [sg.Frame('', tx_data_layout), sg.Multiline('', font=(font + font_size + ' bold'),
                                                          key='data_input', size=(88, 4)),
               ],

              [sg.T('历史数据'), sg.Combo(js_cfg['user_input_data'], js_cfg['user_input_data'][0], pad=((35, 5), (1, 1)),
                                          readonly=True, key='history_data', size=(115, 1), enable_events=True)
               ]
              ]

    global window
    global hw_obj
    global real_time_save_file_name
    global log_remain_str

    window = sg.Window('v1.0.0', layout, finalize=True, resizable=True)
    update_connect_button_text(window, js_cfg['hw_sel'])

    jk_obj = bds_jk.BDS_Jlink(hw_error)
    hw_obj = jk_obj
    ser_obj = jk_obj

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
                '''
                if hw_obj == ser_obj:
                    window['open_timestamp'].update('打开时间戳', button_color=('grey0', 'grey100'))
                    hw_obj.close_timestamp()
                '''
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
        elif event == 'open_timestamp':
            if window['open_timestamp'].get_text() == '打开时间戳':
                hw_obj.open_timestamp()
                window['open_timestamp'].update('关闭时间戳', button_color=('grey0', 'green4'))
            else:
                hw_obj.close_timestamp()
                window['open_timestamp'].update('打开时间戳', button_color=('grey0', 'grey100'))
        elif event == 'save_all_data':
            if window[DB_OUT].get() != '':
                file_name = 'aaa_log\\' + 'log_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.txt'
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(window[DB_OUT].get())
                    os.startfile(file_name)
                    window[DB_OUT].update('')
            else:
                sg.popup('[Error]无数据!!!')
        elif event == ' 滚动到最底端 ':
            mul_scroll = True
            window[DB_OUT].update(autoscroll=True)
        elif event == '清除窗口数据':
            window[DB_OUT].update('')
        elif event == 'tx_data':
            print(window['data_input'].get())
            window['history_data'].update(window['data_input'].get(),
                                          values=[window['data_input'].get()])
        elif event == 'history_data':
            window['data_input'].write(values['history_data'])

        log_process(window, hw_obj, js_cfg, auto_scroll=mul_scroll)

    window.close()


if __name__ == '__main__':
    main()
