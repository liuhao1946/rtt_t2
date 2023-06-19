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
import sys
import bds.time_diff as td

global window
global hw_obj
global log_remain_str
global real_time_save_file_name

thread_lock = threading.Lock()

DB_OUT = 'db_out' + sg.WRITE_ONLY_KEY

APP_ICON = b'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'

sg.theme('DarkBlue11')

# 黑：000000
# 红：FF3030
# 蓝：00008B
# 绿：008B00
# 紫：9932CC


def hw_rx_thread():
    while True:
        try:
            thread_lock.acquire()
            hw_obj.hw_read()
            run_interval_s = hw_obj.get_read_data_time_interval_s()
        finally:
            thread_lock.release()
        time.sleep(run_interval_s)


def ser_hot_plug_detect(window_ser_sel, des_list, name_list):
    cur_com_des_list, cur_com_name_list = bds_ser.serial_find()
    if cur_com_name_list != name_list:
        default_com = ['']
        des_new, des_old = set(cur_com_des_list), set(des_list)
        # 串口增加
        def_new_len, def_old_len = len(des_new), len(des_old)
        if def_new_len > def_old_len:
            # 插入
            default_com[0] = list(des_new.difference(des_old))[0]
            log.info('serial update: add ' + default_com[0])
        elif def_new_len < def_old_len:
            # 拔出
            if window_ser_sel.get() in cur_com_des_list:
                default_com[0] = window_ser_sel.get()
            log.info('serial update: reduce ' + default_com[0])
        else:
            pass
        del name_list[:]
        del des_list[:]
        [name_list.append(v) for v in cur_com_name_list]
        [des_list.append(v) for v in cur_com_des_list]
        window_ser_sel.update(default_com[0], values=cur_com_des_list)


def hw_config_dialog(js_cfg):
    # 遍历串口
    interface_sel = js_cfg['hw_sel']
    chip_list = js_cfg['jk_chip']
    jk_speed = js_cfg['jk_speed']
    baud_list = js_cfg['ser_baud']
    com_des_list, com_name_list = bds_ser.serial_find()
    if not com_des_list:
        com_des_list.append('')
    if not baud_list:
        baud_list.append('')

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
                 [sg.Checkbox('连接时复位', default=js_cfg['jk_con_reset'], key='jk_reset', font=js_cfg['font'][0])]
                 ]
    # 串口配置
    ser_layout = [[sg.T('串口'),
                   sg.Combo(com_des_list, default_value=com_des_list[0], key='com_des_list', readonly=True,
                            size=(30, 1)),
                   sg.T('波特率', pad=((45, 5), (5, 5))),
                   sg.Combo(baud_list, default_value=baud_list[0], key='baud_list', size=(10, 1), pad=((5, 5), (5, 5)))
                   ]
                  ]

    # 波形配置
    wave_layout = [[sg.T('y轴下边界'),
                    sg.In(js_cfg['y_range'][0], key='y_min', pad=((10, 1), (1, 1)), size=(10, 1)),
                    sg.T('y轴上边界', pad=((10, 1), (1, 1))),
                    sg.In(js_cfg['y_range'][1], key='y_max', size=(10, 1))],
                   [sg.T('y轴名称', pad=((5, 1), (1, 1))),
                    sg.In(js_cfg['y_label_text'], key='y_label_text', pad=((25, 1), (1, 1)), size=(10, 1)),
                    sg.T('曲线名称', pad=((12, 1), (1, 1))),
                    sg.In(js_cfg['curves_name'], key='curves_name', pad=((10, 1), (5, 5)), size=(50, 1)),
                    ]
                   ]

    # 字符编码
    c_format = js_cfg['char_format']
    c_utf_8 = False
    c_asc = False
    if c_format == 'utf-8':
        c_utf_8 = True
    else:
        c_asc = True

    char_format_layout = [[sg.Checkbox('utf-8', default=c_utf_8, key='utf_8', enable_events=True),
                           sg.Checkbox('asc', default=c_asc, key='asc', enable_events=True)],
                          ]

    dialog_layout = [[sg.Frame('接口选择', interface_layout)],
                     [sg.Frame('J_Link配置', jk_layout)],
                     [sg.Frame('串口配置', ser_layout)],
                     [sg.Frame('波形图配置', wave_layout)],
                     [sg.Frame('字符编码格式', char_format_layout)],
                     [sg.Button('保存', key='save', pad=((430, 5), (10, 10)), size=(8, 1)),
                      sg.Button('取消', key='clean', pad=((30, 5), (10, 10)), size=(8, 1))]
                     ]

    cfg_window = sg.Window('硬件接口配置', dialog_layout, modal=True)

    ser_lost_detect_interval = 0
    while True:
        d_event, d_values = cfg_window.read(timeout=100)
        print(d_event)

        ser_lost_detect_interval += 1
        if ser_lost_detect_interval >= 10:
            ser_lost_detect_interval = 0
            ser_hot_plug_detect(cfg_window['com_des_list'], com_des_list, com_name_list)

        if d_event == sg.WINDOW_CLOSED or d_event == 'clean':
            break
        elif d_event == 'save':
            # 将芯片信号写入第一个位置
            chip_name = cfg_window['chip'].get()
            try:
                js_cfg['y_range'][0] = int(cfg_window['y_min'].get())
                js_cfg['y_range'][1] = int(cfg_window['y_max'].get())
                js_cfg['y_label_text'] = cfg_window['y_label_text'].get()
                js_cfg['curves_name'] = cfg_window['curves_name'].get()

                baud = int(cfg_window['baud_list'].get())
                # 删除重复baud
                if baud in js_cfg['ser_baud']:
                    js_cfg['ser_baud'] = [x for x in js_cfg['ser_baud'] if x != baud]
                js_cfg['ser_baud'].insert(0, baud)
                if len(js_cfg['ser_baud']) >= 10:
                    js_cfg['ser_baud'].pop()
                js_cfg['ser_des'] = cfg_window['com_des_list'].get()
                js_cfg['ser_com'] = com_name_list[com_des_list.index(cfg_window['com_des_list'].get())]

                if cfg_window['asc'].get():
                    c_format = 'asc'
                elif cfg_window['utf_8'].get():
                    c_format = 'utf-8'
                js_cfg['char_format'] = c_format
                if chip_name in js_cfg['jk_chip']:
                    js_cfg['jk_chip'].remove(chip_name)
                js_cfg['jk_chip'].insert(0, chip_name)
                js_cfg['jk_con_reset'] = cfg_window['jk_reset'].get()

                with open('config.json', 'w') as f:
                    json.dump(js_cfg, f, indent=4)
                break
            except:
                sg.Popup('y轴范围设置错误')
        elif d_event == 'jk_radio':
            cfg_window['jk_radio'].update(True)
            cfg_window['ser_radio'].update(False)
            js_cfg['hw_sel'] = '1'
        elif d_event == 'ser_radio':
            cfg_window['jk_radio'].update(False)
            cfg_window['ser_radio'].update(True)
            js_cfg['hw_sel'] = '2'
        elif d_event == 'utf_8':
            cfg_window['asc'].update(False)
            cfg_window['utf_8'].update(True)
        elif d_event == 'asc':
            cfg_window['asc'].update(True)
            cfg_window['utf_8'].update(False)

    cfg_window.close()


def hw_error(err):
    window.write_event_value('hw_error', err)


def hw_warn(err):
    window.write_event_value('hw_warn', err)


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
    if not patterns:
        return text

    lines = text.split('\n')
    filtered_lines = (line for line in lines if not any(pattern in line for pattern in patterns))
    return '\n'.join(filtered_lines)


def log_fileter(log_data, filter_pat, remain_str=''):
    raw_s = remain_str + ''.join(log_data)
    log_lines = raw_s.split('\n')
    filtered_lines = []
    updated_remain_str = ''

    last_index = len(log_lines) - 1
    for idx, line in enumerate(log_lines):
        if idx < last_index:
            filtered_line = remove_lines(filter_pat, line + '\n')
            filtered_lines.append(filtered_line)
        else:
            if line.endswith('\n'):
                filtered_line = remove_lines(filter_pat, line + '\n')
                filtered_lines.append(filtered_line)
            else:
                updated_remain_str = line

    new_s = ''.join(filtered_lines)

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
                color = find_key(v, 'BDSCOL')
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

    filter_pat = []
    if win['filter_en'].get():
        filter_pat = win['filter'].get().split('&&')

    # read log data
    raw_log = []
    obj.read_data_queue(raw_log)
    # filter log
    new_log, log_remain_str = log_fileter(raw_log, filter_pat, log_remain_str)
    # Check only asc characters
    if js_cfg['char_format'] != 'asc' or not db_data_check_error(new_log):
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
            jk_con_reset = jk_cfg['jk_con_reset']
            try:
                jk_speed = int(jk_cfg['jk_speed'])
            except:
                jk_speed = 4000
            obj.hw_open(speed=jk_speed, chip=jk_cfg['jk_chip'][0], reset_flag=jk_con_reset)
            if obj.hw_is_open():
                win['connect'].update('J_Link断开', button_color=('grey0', 'green4'))
                win[DB_OUT].write('[J_Link LOG]sn:%d\n' % obj.get_hw_serial_number())
                win[DB_OUT].write('[J_Link LOG]过滤配置:%s\n' % ','.join(jk_cfg['filter'].split('&&')))
                win[DB_OUT].write('[J_Link LOG]芯片型号:%s\n' % jk_cfg['jk_chip'][0])
                if jk_con_reset:
                    win[DB_OUT].write('[J_Link LOG]J_Link复位MCU.\n')
                else:
                    win[DB_OUT].write('[J_Link LOG]J_Link没有复位MCU.\n')
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


def ser_connect(win, obj, jk_cfg):
    if win['connect'].get_text() == '串口连接':
        try:
            cur_com_name = jk_cfg['ser_com']
            cur_baud = int(jk_cfg['ser_baud'][0])
            win[DB_OUT].write('[Serial LOG]com description: %s\n' % jk_cfg['ser_des'])
            win[DB_OUT].write('[Serial LOG]baudrare: %d\n' % cur_baud)

            obj.hw_open(port=cur_com_name, baud=cur_baud, rx_buffer_size=10240)

            if obj.hw_is_open():
                win[DB_OUT].write('[Serial LOG]串口已打开\n')
                win['connect'].update('关闭串口', button_color=('grey0', 'green4'))
            else:
                win[DB_OUT].write('[Serial LOG]串口打开失败\n')
        except Exception as e:
            print(e)
            obj.hw_close()
            log.info('串口打开失败' + str(e))
            win[DB_OUT].write('[Serial LOG]Error:%s\n' % e)
            win['connect'].update('串口连接', button_color=('grey0', 'grey100'))
    else:
        obj.hw_close()
        win[DB_OUT].write('[Serial LOG]串口关闭！\n')
        win['connect'].update('串口连接', button_color=('grey0', 'grey100'))
        log.info('串口关闭！')
        time.sleep(0.1)


def Collapsible(layout, key, title='', arrows=(sg.SYMBOL_DOWN, sg.SYMBOL_UP), collapsed=False):
    """
    User Defined Element
    A "collapsable section" element. Like a container element that can be collapsed and brought back
    :param layout:Tuple[List[sg.Element]]: The layout for the section
    :param key:Any: Key used to make this section visible / invisible
    :param title:str: Title to show next to arrow
    :param arrows:Tuple[str, str]: The strings to use to show the section is (Open, Closed).
    :param collapsed:bool: If True, then the section begins in a collapsed state
    :return:sg.Column: Column including the arrows, title and the layout that is pinned
    """
    return sg.Column([[sg.T((arrows[1] if collapsed else arrows[0]), enable_events=True, k=key + '-BUTTON-'),
                       sg.T(title, enable_events=True, key=key + '-TITLE-')],
                      [sg.pin(sg.Column(layout, key=key, visible=not collapsed, metadata=arrows))]], pad=(0, 0))


def main():
    multiprocessing.freeze_support()

    log.basicConfig(filename='rtt.log', filemode='w', level=log.INFO, format='%(asctime)s %(message)s',
                    datefmt='%Y/%m/%d %I:%M:%S')

    # 读取json配置文件
    with open('config.json', 'r') as f:
        js_cfg = json.load(f)

    font = js_cfg['font'][0] + ' '
    font_size = js_cfg['font_size']

    sec1_layout = [[sg.T('过滤'), sg.In(js_cfg['filter'], key='filter', size=(50, 1)),
                    sg.Checkbox('', default=False, key='filter_en', enable_events=True),
                    ]
                   ]
    tx_data_type = ['ASC', 'HEX']
    right_click_menu = ['', ['清除窗口数据', '滚动到最底端']]

    tx_data_layout = [[sg.Button('发送数据', key='tx_data', pad=((5, 5), (5, 15)), size=(8, 1))],
                      [sg.Combo(tx_data_type, tx_data_type[0], readonly=True, key='tx_data_type', size=(8, 1))]]

    layout = [[sg.Button('J_Link连接', key='connect', size=(10, 1), font=font, button_color=('grey0', 'grey100')),
               sg.Button('打开时间戳', font=font, button_color=('grey0', 'grey100'), key='open_timestamp'),
               sg.Button('实时保存数据', font=font, size=(14, 1), button_color=('grey0', 'grey100'),
                         key='real_time_save_data'),
               sg.Button('保存全部数据', font=font, button_color=('grey0', 'grey100'), key='save_all_data'),
               sg.Button('一键跳转', font=font, button_color=('grey0', 'grey100'), key='skip_to_file'),
               sg.Button('配置', button_color=('grey0', 'grey100'), pad=((200, 1), (1, 1)), key='config', size=(9, 1)),
               sg.Button('波形绘制', button_color=('grey0', 'grey100'), key='wave', size=(9, 1))],

              [Collapsible(sec1_layout, 'sec1_key', '过滤设置', collapsed=True)],

              [sg.Multiline(autoscroll=True, key=DB_OUT, size=(100, 25), right_click_menu=right_click_menu,
                            font=(font + font_size + ' bold'))],

              [sg.Frame('', tx_data_layout, key='tx_button'), sg.Multiline('', font=(font + font_size + ' bold'),
                                                                           key='data_input', size=(89, 4)),
               ],
              [sg.T('历史数据'),
               sg.Combo(js_cfg['user_input_data'], js_cfg['user_input_data'][0], pad=((35, 5), (1, 1)),
                        readonly=True, key='history_data', size=(115, 1), enable_events=True)
               ]
              ]

    global window
    global hw_obj
    global real_time_save_file_name
    global log_remain_str

    window = sg.Window('v1.0.1', layout, finalize=True, resizable=True, icon=APP_ICON)
    window.set_min_size(window.size)
    window[DB_OUT].expand(True, True, True)
    window['data_input'].expand(True, True, True)
    window['history_data'].expand(True, False, False)

    update_connect_button_text(window, js_cfg['hw_sel'])
    jk_obj = bds_jk.BDS_Jlink(hw_error, hw_warn, char_format=js_cfg['char_format'])
    ser_obj = bds_ser.BDS_Serial(hw_error, hw_warn, char_format=js_cfg['char_format'])

    hw_obj = jk_obj

    threading.Thread(target=hw_rx_thread, daemon=True).start()

    mul_scroll = False
    real_time_save_file_name = ''
    log_remain_str = ''

    wv.wave_init()
    hw_obj.reg_dlog_M_callback(wv.wave_data)
    ser_obj.reg_dlog_M_callback(wv.wave_data)

    sg.cprint_set_output_destination(window, DB_OUT)

    time_diff = td.TimeDifference()

    while True:
        event, values = window.read(timeout=150)

        if event == sg.WIN_CLOSED:
            hw_obj.hw_close()
            break

        # Sliding control of log window
        y1, y2 = window[DB_OUT].get_vscroll_position()
        if mul_scroll and bool(1 - y2):
            print('autoscroll=False')
            mul_scroll = False
            window[DB_OUT].update(autoscroll=False)
        elif not mul_scroll and y2 == 1:
            mul_scroll = True
            print('autoscroll=True')
            window[DB_OUT].update(autoscroll=True)

        # GUI event response
        if event == 'hw_error':
            hw_obj.hw_close()
            if js_cfg['hw_sel'] == '2':
                window[DB_OUT].write('[Serial LOG]串口错误:' + values['hw_error'] + '\n')
                window['connect'].update('串口连接', button_color=('grey0', 'grey100'))
            else:
                window[DB_OUT].write('[J_Link LOG]J_Link错误:' + values['hw_error'] + '\n')
                window['connect'].update('J_Link连接', button_color=('grey0', 'grey100'))
            sg.popup(values['hw_error'])
            print('error:' + values['hw_error'])
        elif event == 'hw_warn':
            window[DB_OUT].write('[BDS LOG] ' + values['hw_warn'])
            print('warn:' + values['hw_warn'])
        elif event == 'connect':
            wv.wave_cmd('wave reset')
            if window['connect'].get_text().find('J_Link') >= 0:
                if hw_obj == ser_obj:
                    window['open_timestamp'].update('打开时间戳', button_color=('grey0', 'grey100'))
                    hw_obj.close_timestamp()
                thread_lock.acquire()
                hw_obj = jk_obj
                thread_lock.release()
                jk_connect(window, hw_obj, js_cfg)
            elif window['connect'].get_text().find('串口') >= 0:
                if hw_obj == jk_obj:
                    window['open_timestamp'].update('打开时间戳', button_color=('grey0', 'grey100'))
                    hw_obj.close_timestamp()
                thread_lock.acquire()
                hw_obj = ser_obj
                thread_lock.release()
                ser_connect(window, hw_obj, js_cfg)
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
        elif event == '滚动到最底端':
            mul_scroll = True
            window[DB_OUT].update(autoscroll=True)
        elif event == '清除窗口数据':
            window[DB_OUT].update('')
        elif event == 'tx_data':
            if hw_obj.hw_is_open():
                input_data = window['data_input'].get()
                if input_data not in js_cfg['user_input_data']:
                    if len(js_cfg['user_input_data']) >= 10:
                        js_cfg['user_input_data'].pop(0)
                    js_cfg['user_input_data'].append(input_data)
                    with open('config.json', 'w') as f:
                        json.dump(js_cfg, f, indent=4)
                window['history_data'].update(input_data, values=js_cfg['user_input_data'])
                if window['tx_data_type'].get() == 'HEX':
                    try:
                        print([int(i, 16) for i in input_data.split(' ')])
                        hw_obj.hw_write([int(i, 16) for i in input_data.split(' ')])
                    except:
                        sg.popup_no_wait('数据格式错误。数据类型请选择HEX，数据之间用空格隔开。')
                else:
                    try:
                        hw_obj.hw_write([ord(i) for i in input_data])
                    except Exception as e:
                        sg.popup_no_wait("%s" % e)
            else:
                sg.popup('请先连接硬件')
        elif event == 'history_data':
            window['data_input'].update(window['history_data'].get())
        elif event.startswith('sec1_key'):
            window['sec1_key'].update(visible=not window['sec1_key'].visible)
            window['sec1_key' + '-BUTTON-'].update(
                window['sec1_key'].metadata[0] if window['sec1_key'].visible else window['sec1_key'].metadata[1])
        elif event.startswith('sec2_key'):
            window['sec2_key'].update(visible=not window['sec2_key'].visible)
            window['sec2_key' + '-BUTTON-'].update(
                window['sec2_key'].metadata[0] if window['sec2_key'].visible else window['sec2_key'].metadata[1])
        elif event == 'filter_en':
            if window['filter_en'].get():
                js_cfg['filter'] = window['filter'].get()
                js_cfg['filter_en'] = True
            else:
                js_cfg['filter'] = window['filter'].get()
                js_cfg['filter_en'] = False
            with open('config.json', 'w') as f:
                json.dump(js_cfg, f, indent=4)
        elif event == 'config':
            if not hw_obj.hw_is_open():
                hw_config_dialog(js_cfg)
                update_connect_button_text(window, js_cfg['hw_sel'])
                hw_obj.hw_set_char_format(js_cfg['char_format'])
            else:
                sg.popup_no_wait('请先断开硬件连接！')
        elif event == 'wave':
            if hw_obj.hw_is_open():
                if len(js_cfg['curves_name']) > 0:
                    wv.wave_cmd('wave reset')
                    wv.startup_wave(js_cfg['y_range'], js_cfg['y_label_text'],
                                    [v for v in js_cfg['curves_name'].split('&&') if v != ''])
                else:
                    sg.popup_no_wait('没有设置任何轴名称，请至少设置一个轴名称')
            else:
                sg.popup_no_wait('请先连接硬件')
        elif event == 'skip_to_file':
            try:
                os.startfile(os.path.dirname(os.path.realpath(sys.argv[0])) + '\\aaa_log')
            except Exception as e:
                sg.popup_no_wait("%s" % e)

        log_process(window, hw_obj, js_cfg, auto_scroll=mul_scroll)
        time_diff.print_time_difference()

    window.close()


if __name__ == '__main__':
    main()
