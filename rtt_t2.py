import PySimpleGUI as sg
import json
import logging as log
import threading
import time
import re
import datetime
import os
import bds.bds_jlink as bds_jk
import multiprocessing
import bds.bds_serial as bds_ser
import bds.bds_waveform as wv
import sys
import bds.time_diff as td
import requests
import webbrowser
import keyboard
import tkinter as tk

global window
global download_window
global hw_obj
global log_remain_str
global real_time_save_file_name

thread_lock = threading.Lock()
download_thread_lock = threading.Lock()
download_thread_lock.acquire()

DB_OUT = 'db_out' + sg.WRITE_ONLY_KEY

APP_ICON = b'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'

color_pat = re.compile(r'BDSCOL\((\d{1,8})\)', re.I)

sg.theme('DefaultNoMoreNagging')


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


def version_detect_thread(win, rtt_cur_version):
    try:
        try:
            print('Download from gitee')
            latest_release = requests.get("https://gitee.com/api/v5/repos/bds123/rtt_t2/releases",
                                          timeout=5).json()[-1]
            log.info('download source: gitee')
        except:
            print('Download from github')
            latest_release = requests.get("https://api.github.com/repos/liuhao1946/rtt_t2/releases",
                                          timeout=5).json()[0]
            log.info('download source: github')

        if rtt_cur_version != latest_release['tag_name']:
            win.write_event_value('latest_release', latest_release)
    except Exception as e:
        log.info('download error: ' + str(e))
        print('download error:' + str(e))


def download_thread(latest_release):
    download_thread_lock.acquire()
    try:
        # 获取下载路径
        home_dir = os.path.expanduser('~')
        download_dir = os.path.join(home_dir, 'Downloads')
        # 获取版本号

        rtt_latest_version = latest_release['tag_name']
        print('rtt latest version %s' % rtt_latest_version)
        log.info('rtt latest version %s' % rtt_latest_version)

        download_url = latest_release['assets'][0]['browser_download_url']
        tag_name = latest_release['assets'][0]['name']
        filename = os.path.join(download_dir, tag_name)

        print('Download url: %s' % download_url)
        print('Download path : %s' % filename)

        log.info('Download url: %s' % download_url)

        # 请求文件
        response = requests.get(download_url, timeout=5, stream=True)
        # 获取文件大小
        total_size_in_bytes = int(response.headers.get('Content-Length', 0))
        block_size = 1024  # 1 Kibibyte
        download_len = 0
        print('file total size: %d' % total_size_in_bytes)
        percent_latest = 0
        with open(filename, 'wb') as file:
            for data in response.iter_content(block_size):
                file.write(data)
                download_len += len(data)
                percent = download_len * 100 // total_size_in_bytes
                if percent_latest != percent:
                    download_window.write_event_value('downloading', percent)
                    percent_latest = percent

        download_window.write_event_value('download_done', filename)
        log.info('download_done')
    except Exception as e:
        print(e)
        try:
            download_window.write_event_value('download_err', str(e))
        except:
            pass


def extract_and_convert_hex(string):
    # 正则表达式匹配规则
    pattern = r"(0x[0-9A-Fa-f]+)\s+(0x[0-9A-Fa-f]+)"

    # 使用正则表达式查找匹配项
    match = re.search(pattern, string)
    if match:
        # 提取匹配的十六进制数
        hex1, hex2 = match.groups()
        if int(hex1, 16) % 4 != 0:
            return None

        return hex1, hex2
    else:
        return None


def hw_config_dialog(js_cfg):
    global cfg_window

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
    if js_cfg['ser_des'] in com_des_list:
        def_select_com = js_cfg['ser_des']
    else:
        def_select_com = com_des_list[0]

    jk_sel = False
    ser_sel = False
    if interface_sel == '1':
        jk_sel = True
    else:
        ser_sel = True

    if js_cfg['rtt_block_address'][0] == '' or js_cfg['rtt_block_address'][1] == '':
        rtt_search_address = ''
    else:
        rtt_search_address = js_cfg['rtt_block_address'][0] + ' ' + js_cfg['rtt_block_address'][1]

    # 接口选择
    # https://github.com/liuhao1946/rtt_t2
    interface_layout = [[sg.Radio('J_Link', 'radio1', key='jk_radio', default=jk_sel, enable_events=True),
                         sg.Radio('串口', 'radio2', key='ser_radio', default=ser_sel, enable_events=True),
                         ]]

    # jlink配置
    jk_layout = [[sg.Combo(chip_list, chip_list[0], readonly=True, key='chip', size=(18, 1)),
                  sg.Text('SN'), sg.Input('', readonly=True, key='jk_sn', size=(15, 1)),
                  sg.T('speed(kHz)'), sg.In(jk_speed, key='jk_speed', size=(5, 1)),
                  sg.Checkbox('连接时复位', default=js_cfg['jk_con_reset'], key='jk_reset', pad=((40, 10), (1, 1)),
                              font=js_cfg['font'][0])],
                 [sg.T('_SEGGER_RTT地址搜索范围(格式:起始地址 范围大小，比如:0x20000000 0x4000)：')],
                 [sg.In(rtt_search_address, key='rtt_block_address', size=(50, 1))]
                 ]
    # 串口配置
    ser_layout = [[sg.T('串口'),
                   sg.Combo(com_des_list, default_value=def_select_com, key='com_des_list', readonly=True,
                            size=(47, 1)),
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
    c_hex = False
    c_gb2312 = False
    if c_format == 'utf-8':
        c_utf_8 = True
    elif c_format == 'asc':
        c_asc = True
    elif c_format == 'hex':
        c_hex = True
    elif c_format == 'gb2312':
        c_gb2312 = True

    lb_rn = False
    lb_n = False
    lb_none = False
    if js_cfg['line_break'] == '\r\n':
        lb_rn = True
    elif js_cfg['line_break'] == '\n':
        lb_n = True
    else:
        lb_none = True

    char_format_layout = [[sg.Checkbox('utf-8', default=c_utf_8, key='utf_8', enable_events=True),
                           sg.Checkbox('asc', default=c_asc, key='asc', enable_events=True),
                           sg.Checkbox('hex', default=c_hex, key='hex', enable_events=True),
                           sg.Checkbox('gb2312', default=c_gb2312, key='gb2312', enable_events=True)],
                          ]

    line_break_layout = [[sg.Checkbox(r'\r\n', default=lb_rn, key='lb_rn', enable_events=True),
                          sg.Checkbox(r'\n', default=lb_n, key='lb_n', enable_events=True),
                          sg.Checkbox(r'none', default=lb_none, key='lb_none', enable_events=True)
                          ],
                         ]

    dialog_layout = [[sg.Frame('接口选择', interface_layout)],
                     [sg.Frame('J_Link配置', jk_layout)],
                     [sg.Frame('串口配置', ser_layout)],
                     [sg.Frame('波形图配置', wave_layout)],
                     [sg.Frame('字符编码格式', char_format_layout), sg.Frame('发送asc追加换行符', line_break_layout)],
                     [[sg.Text('gitee仓库地址:'),
                       sg.Text('https://gitee.com/bds123/rtt_t2', key='gitee_adr', enable_events=True)],
                      [sg.Text('github仓库地址:'),
                       sg.Text('https://github.com/liuhao1946/rtt_t2', key='github_adr', enable_events=True)]],
                     [sg.Button('保存', key='save', pad=((430, 5), (10, 10)), size=(8, 1),
                                button_color=('grey0', 'grey100')),
                      sg.Button('取消', key='clean', pad=((30, 5), (10, 10)), size=(8, 1),
                                button_color=('grey0', 'grey100'))]
                     ]

    cfg_window = sg.Window('硬件接口配置', dialog_layout, modal=True, icon=APP_ICON, finalize=True)

    cfg_window['gitee_adr'].set_cursor('hand2')
    cfg_window['github_adr'].set_cursor('hand2')

    ser_lost_detect_interval = 0
    err_code = 0

    while True:
        d_event, d_values = cfg_window.read(timeout=100)

        ser_lost_detect_interval += 1
        if ser_lost_detect_interval >= 10:
            ser_lost_detect_interval = 0
            default_des = bds_ser.ser_hot_plug_detect(cfg_window['com_des_list'].get(), com_des_list, com_name_list)
            try:
                if default_des != '':
                    cfg_window['com_des_list'].update(default_des, values=com_des_list)
            except ValueError as e:
                print(e)

        if d_event == sg.WINDOW_CLOSED or d_event == 'clean':
            break
        elif d_event == 'save':
            # 将芯片信号写入第一个位置
            chip_name = cfg_window['chip'].get()
            try:
                if cfg_window['rtt_block_address'].get() != '':
                    rtt_block_address = extract_and_convert_hex(cfg_window['rtt_block_address'].get())
                    if rtt_block_address is None:
                        sg.popup("请输入正确的起始搜索地址以及范围。十六进制字符串必须以 '0x'或者'0X' 开头，两个值之间用空格隔开,"
                                 "起始地址必须4字节对齐，比如:\"0x20000000\" \"0x1000\"")
                        continue
                    else:
                        js_cfg['rtt_block_address'] = rtt_block_address
                        print(rtt_block_address[0], rtt_block_address[1])
                else:
                    js_cfg['rtt_block_address'] = ['', '']

                js_cfg['jk_speed'] = int(cfg_window['jk_speed'].get())
                js_cfg['y_range'][0] = int(cfg_window['y_min'].get())
                js_cfg['y_range'][1] = int(cfg_window['y_max'].get())
                js_cfg['y_label_text'] = cfg_window['y_label_text'].get()
                js_cfg['curves_name'] = cfg_window['curves_name'].get()

                baud = int(cfg_window['baud_list'].get())
                js_cfg['ser_baud'] = bds_ser.ser_buad_list_adjust(baud, js_cfg['ser_baud'])
                if len(js_cfg['ser_baud']) >= 10:
                    js_cfg['ser_baud'].pop()

                js_cfg['ser_des'] = cfg_window['com_des_list'].get()

                try:
                    js_cfg['ser_com'] = com_name_list[com_des_list.index(cfg_window['com_des_list'].get())]
                except Exception as e:
                    js_cfg['ser_com'] = ''

                if cfg_window['asc'].get():
                    c_format = 'asc'
                elif cfg_window['utf_8'].get():
                    c_format = 'utf-8'
                elif cfg_window['hex'].get():
                    c_format = 'hex'
                elif cfg_window['gb2312'].get():
                    c_format = 'gb2312'
                js_cfg['char_format'] = c_format

                if cfg_window['lb_rn'].get():
                    lb_type = "\r\n"
                elif cfg_window['lb_n'].get():
                    lb_type = "\n"
                else:
                    lb_type = ""
                js_cfg['line_break'] = lb_type

                if chip_name in js_cfg['jk_chip']:
                    js_cfg['jk_chip'].remove(chip_name)
                js_cfg['jk_chip'].insert(0, chip_name)
                js_cfg['jk_con_reset'] = cfg_window['jk_reset'].get()

                with open('config.json', 'w') as f:
                    json.dump(js_cfg, f, indent=4)
                break
            except Exception as e:
                sg.Popup(str(e), icon=APP_ICON)
        elif d_event == 'jk_radio':
            cfg_window['jk_radio'].update(True)
            cfg_window['ser_radio'].update(False)
            js_cfg['hw_sel'] = '1'
        elif d_event == 'ser_radio':
            cfg_window['jk_radio'].update(False)
            cfg_window['ser_radio'].update(True)
            js_cfg['hw_sel'] = '2'
        elif d_event == 'utf_8':
            cfg_window['hex'].update(False)
            cfg_window['asc'].update(False)
            cfg_window['utf_8'].update(True)
            cfg_window['gb2312'].update(False)
        elif d_event == 'asc':
            cfg_window['asc'].update(True)
            cfg_window['utf_8'].update(False)
            cfg_window['hex'].update(False)
            cfg_window['gb2312'].update(False)
        elif d_event == 'hex':
            cfg_window['asc'].update(False)
            cfg_window['utf_8'].update(False)
            cfg_window['hex'].update(True)
            cfg_window['gb2312'].update(False)
        elif d_event == 'gb2312':
            cfg_window['asc'].update(False)
            cfg_window['utf_8'].update(False)
            cfg_window['hex'].update(False)
            cfg_window['gb2312'].update(True)

        elif d_event == 'gitee_adr' or d_event == 'github_adr':
            webbrowser.open(cfg_window[d_event].get())
        elif d_event == 'lb_rn':
            cfg_window['lb_rn'].update(True)
            cfg_window['lb_n'].update(False)
            cfg_window['lb_none'].update(False)
        elif d_event == 'lb_n':
            cfg_window['lb_rn'].update(False)
            cfg_window['lb_n'].update(True)
            cfg_window['lb_none'].update(False)
        elif d_event == 'lb_none':
            cfg_window['lb_rn'].update(False)
            cfg_window['lb_n'].update(False)
            cfg_window['lb_none'].update(True)

    cfg_window.close()

    return err_code


def update_reminder_dialog(font, latest_release):
    global download_window

    threading.Thread(target=download_thread, args=(latest_release,), daemon=True).start()

    progress_layout = [
        [sg.ProgressBar(100, orientation='h', size=(60, 20), key='progressbar')]
    ]

    ver_info = '软件更新:' + latest_release['tag_name'] + '\n'
    ver_info += latest_release['body']

    ver_info = ver_info.replace('\r\n', '\n')
    update_layout = [
        [sg.Text(ver_info, key='update_text', font=font)],
        [sg.Text('gitee下载地址:'),
         sg.Text('https://gitee.com/bds123/rtt_t2/releases', key='gitee_adr', enable_events=True)],
        [sg.Text('github下载地址:'),
         sg.Text('https://github.com/liuhao1946/rtt_t2/releases', key='github_adr', enable_events=True)],
        [sg.Frame('下载进度', progress_layout, key='progress', font=font)],
        [sg.Button('立刻更新', key='download', font=font),
         sg.Button('下次更新', key='next_download', font=font),
         ]
    ]

    s = ''
    download_window = sg.Window('更新提醒', update_layout, modal=True, icon=APP_ICON, font=font, finalize=True)

    download_window['gitee_adr'].set_cursor('hand2')
    download_window['github_adr'].set_cursor('hand2')

    download_button = download_window['download']
    progress_bar = download_window['progressbar']
    progress_display = download_window['progress']

    while True:
        event, values = download_window.read(timeout=100)

        if event == sg.WINDOW_CLOSED or event == 'next_download':
            break
        elif event == 'gitee_adr' or event == 'github_adr':
            webbrowser.open(download_window[event].get())
        elif event == 'download':
            if download_button.get_text() == '立刻更新':
                download_button.update('下载中...')
                download_thread_lock.release()
                log.info('start download...')
                print('start download...')
                time.sleep(0.2)
        elif event == 'download_err':
            log.info('download error: ' + values['download_err'])
            progress_display.update('下载异常!重启软件或者下次更新')
            download_button.update('立刻更新')
        elif event == 'downloading':
            progress_bar.update(values['downloading'])
            progress_display.update('%d' % values['downloading'] + '%')
        elif event == 'download_done':
            s = values['download_done']
            time.sleep(0.3)
            break

    download_window.close()

    return s


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


def remove_line(patterns, line, only_exclude):
    """
    根据选项删除包含或不包含模式列表中的字符串的行

    :param patterns: 要匹配的模式列表
    :param line: 要处理的行
    :param only_exclude: 是否只删除包含模式的行

    :return: 返回处理后的行，如果被过滤则返回空字符串
    """
    if not patterns:
        return line

    if any(pattern in line for pattern in patterns) != only_exclude:
        return line
    else:
        return ''


def log_fileter(log_data, filter_pat, remain_str='', only_exclude=True):
    raw_s = remain_str + ''.join(log_data)
    log_lines = raw_s.split('\n')
    filtered_lines = []
    updated_remain_str = ''

    last_index = len(log_lines) - 1
    for idx, line in enumerate(log_lines):
        if idx < last_index:
            filtered_line = remove_line(filter_pat, line + '\n', only_exclude)
            filtered_lines.append(filtered_line)
        else:
            if line.endswith('\n'):
                filtered_line = remove_line(filter_pat, line + '\n', only_exclude)
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
    need_s = ''
    color = 0
    pre_color = -1
    line_tag = re.findall('.+\n', s)
    for idx, v in enumerate(line_tag):
        match = color_pat.search(v)
        if match is None:
            if pre_color >= 0:
                sg.cprint(sv, text_color='#%06X' % pre_color, end='', autoscroll=auto_scroll)
                sv = ''
                pre_color = -1
            sv += v
            need_s += v
            color = -1
        else:
            # 打印上一次v_idx < 0时的颜色(默认颜色)
            if sv != '' and color == -1:
                sg.cprint(sv, text_color='#%06X' % 0, end='', autoscroll=auto_scroll)
                sv = ''
            try:
                color = int(match.group(1))  # 提取匹配的数字并转换为整数
            except Exception as e:
                win[DB_OUT].write('[BDS LOG]RAW string:%s,color error:%s,error code:%s\n' % (s, v, e))
                log.info('RAW string:%s,color error:%s,error code:%s\n' % (s, v, e))
                color = 0
            if pre_color < 0:
                pre_color = color
            if color == pre_color:
                temp_s = delete_str('BDSCOL\([0-9]{1,8}\)', v)
                need_s += temp_s
                sv += temp_s
            else:
                # 输出上一个颜色的字符串
                sg.cprint(sv, text_color='#%06X' % pre_color, end='', autoscroll=auto_scroll)
                sv = delete_str('BDSCOL\([0-9]{1,8}\)', v)
                need_s += sv
            pre_color = color
    if color < 0:
        color = 0
    if sv != '':
        sg.cprint(sv, text_color='#%06X' % color, end='', autoscroll=auto_scroll)

    return need_s


def save_log_to_file(win, log_s):
    if win['real_time_save_data'].get_text() == '关闭实时保存数据':
        try:
            with open(real_time_save_file_name, 'a', encoding='utf-8') as f:
                f.write(log_s)
        except Exception as e:
            log.info('Write real time data to file error[%s]\n' % e)


def log_process(win, obj, js_cfg, auto_scroll=True):
    global log_remain_str

    # read log data
    raw_log = []
    obj.read_data_queue(raw_log)

    if js_cfg['char_format'] == 'hex':
        if raw_log:
            win[DB_OUT].write(''.join(raw_log))
        return

    filter_pat = []
    only_exclude = True
    if win['filter_en'].get():
        filter_pat = win['filter'].get().split('&&')
        if win['filter_inverse'].get():
            only_exclude = False

    # filter log
    new_log, log_remain_str = log_fileter(raw_log, filter_pat, log_remain_str, only_exclude)
    # Check only asc characters
    if js_cfg['char_format'] != 'asc' or not db_data_check_error(new_log):
        # print log
        need_log = log_print_line(win, new_log, auto_scroll)
        save_log_to_file(win, need_log)
    else:
        win[DB_OUT].write("RTT数据出错，可能需要重启设备！ + " + "error data:[" + new_log[0:20] + "]\n")
        log.info("RTT数据出错，可能需要重启设备！ + " + "error data:[" + new_log[0:20] + "]\n")


def jk_connect(win, obj, jk_cfg):
    if win['connect'].get_text() == 'J_Link连接':
        try:
            jk_con_reset = jk_cfg['jk_con_reset']
            try:
                jk_speed = jk_cfg['jk_speed']
            except:
                jk_speed = 4000
            start_address = None
            range_size = 0
            if jk_cfg['rtt_block_address'][0] != '' and jk_cfg['rtt_block_address'][1] != '':
                start_address = int(jk_cfg['rtt_block_address'][0], 16)
                range_size = int(jk_cfg['rtt_block_address'][1], 16)
                print(hex(start_address), hex(range_size))
            obj.hw_open(speed=jk_speed, chip=jk_cfg['jk_chip'][0], reset_flag=jk_con_reset,
                        start_address=start_address, range_size=range_size)
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


def Collapsible(layout, key, title='', font=None, arrows=(sg.SYMBOL_DOWN, sg.SYMBOL_UP), collapsed=False):
    """
    User Defined Element
    A "collapsable section" element. Like a container element that can be collapsed and brought back
    :param font: font
    :param layout:Tuple[List[sg.Element]]: The layout for the section
    :param key:Any: Key used to make this section visible / invisible
    :param title:str: Title to show next to arrow
    :param arrows:Tuple[str, str]: The strings to use to show the section is (Open, Closed).
    :param collapsed:bool: If True, then the section begins in a collapsed state
    :return:sg.Column: Column including the arrows, title and the layout that is pinned
    """
    sg.Text()
    return sg.Column([[sg.T((arrows[1] if collapsed else arrows[0]), enable_events=True, k=key + '-BUTTON-'),
                       sg.T(title, enable_events=True, key=key + '-TITLE-', font=font)],
                      [sg.pin(sg.Column(layout, key=key, visible=not collapsed, metadata=arrows))]], pad=(0, 0))


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
    if not isinstance(input_data, str) or input_data.strip() == '':  # 空字符串或非字符串输入
        return user_input_list  # 直接返回原列表，不做更改

    input_data_outside_brackets = extract_outside_brackets_corrected(input_data)
    if input_data_outside_brackets == '':  # 如果括号外文本为空，则不添加
        return user_input_list

    # 清理列表中的空字符串
    user_input_list = [item for item in user_input_list if item.strip() != '']

    # 移除任何括号外文本相同的旧数据
    user_input_list = [item for item in user_input_list if
                       extract_outside_brackets_corrected(item) != input_data_outside_brackets]

    # 维持列表长度不超过30
    if len(user_input_list) >= 29:  # 因为下一步就要添加新元素，所以这里是29
        user_input_list.pop(-1)

    user_input_list.insert(0, input_data)

    return user_input_list


# 监听键盘事件
def listen_for_arrow_keys():
    last_pressed = None
    debounce_time = 0.2  # 设置去抖时间，例如0.2秒

    while True:
        try:
            if keyboard.is_pressed('up') and last_pressed != 'up':
                window.write_event_value('KEY_UP', '')
                last_pressed = 'up'
                time.sleep(debounce_time)  # 等待去抖时间后再继续
            elif keyboard.is_pressed('down') and last_pressed != 'down':
                window.write_event_value('KEY_DOWN', '')
                last_pressed = 'down'
                time.sleep(debounce_time)  # 等待去抖时间后再继续
            elif keyboard.is_pressed('ctrl+f') and last_pressed != 'ctrl+f':
                window.write_event_value('CTRL_F', '')
                last_pressed = 'ctrl+f'
                time.sleep(debounce_time)
            else:
                last_pressed = None  # 如果没有按键被按下，重置last_pressed
        except:
            pass

        time.sleep(0.05)


def get_next_item(lst, current_index, direction):
    if not lst:  # 检查列表是否为空
        return None

    if direction == 'KEY_UP':
        # 上一个元素的索引，如果当前是第一个元素，则跳转到列表的最后一个元素
        new_index = (current_index - 1) % len(lst)
    elif direction == 'KEY_DOWN':
        # 下一个元素的索引，如果当前是最后一个元素，则跳转到列表的第一个元素
        new_index = (current_index + 1) % len(lst)
    else:
        # 如果方向不是'Up'或'Down'，则返回None
        return None

    return lst[new_index], new_index


# 定义搜索窗口的创建函数
def create_find_window(font=None):
    find_layout = [[sg.Input(key='find_key', font=font, size=(50, 1)),
                    sg.Button("查找下一个", font=font, pad=((10, 10), (5, 5)), key='find_next',
                              button_color=('grey0', 'grey100'))],
                   [sg.Button("查找上一个", font=font, pad=((473, 10), (5, 5)), key='find_pre',
                              button_color=('grey0', 'grey100'))]]
    return sg.Window("查找内容", find_layout, modal=False, font=font, finalize=True, icon=APP_ICON)


def highlight_text(widget, keyword, tag, start='1.0', end=tk.END):
    current = start
    first_match = None
    while True:
        current = widget.search(keyword, current, stopindex=end)
        if not current:
            break
        if not first_match:
            first_match = current
        end_match = widget.index(f"{current}+{len(keyword)}c")
        widget.tag_add(tag, current, end_match)
        current = end_match
    widget.tag_config(tag, background='yellow')  # 普通高亮配置
    return first_match



def highlight_current(widget, start, end, current_tag):
    """高亮显示当前聚焦的匹配项。"""
    widget.tag_add(current_tag, start, end)
    widget.tag_config(current_tag, background='dark grey')  # 当前聚焦项的高亮配置


def find_previous(widget, keyword, start='end', end='1.0'):
    # 逆向搜索，从结束向开始
    current = start
    while True:
        current = widget.search(keyword, current, stopindex=end, backwards=True)
        if not current:
            break
        start_match = widget.index(f"{current}+{len(keyword)}c")
        return current  # 返回找到的第一个匹配项的开始位置
    return None


def main():
    multiprocessing.freeze_support()

    log.basicConfig(filename='rtt.log', filemode='w', level=log.INFO, format='%(asctime)s %(message)s',
                    datefmt='%Y/%m/%d %I:%M:%S')

    # 读取json配置文件
    with open('config.json', 'r') as f:
        js_cfg = json.load(f)

    font = js_cfg['font'][0] + ' '
    font_size = js_cfg['font_size']
    rtt_cur_version = 'v2.3.0'

    sec1_layout = [[sg.T('过滤', font=font), sg.In(js_cfg['filter'], key='filter', size=(50, 1)),
                    sg.Checkbox('打开过滤器', default=False, key='filter_en', enable_events=True, font=font),
                    sg.Checkbox('取反过滤器', default=False, key='filter_inverse', enable_events=False, font=font),
                    ]
                   ]
    tx_data_type = ['ASC', 'HEX']
    right_click_menu = ['', ['清除窗口数据', '滚动到最底端']]

    tx_data_layout = [[sg.Button('发送数据', key='tx_data', pad=((5, 5), (5, 15)), size=(8, 1),
                                 button_color=('grey0', 'grey100'))],
                      [sg.Combo(tx_data_type, tx_data_type[0], readonly=True, key='tx_data_type', size=(8, 1))]]

    layout = [[sg.Button('J_Link连接', key='connect', size=(10, 1), font=font, button_color=('grey0', 'grey100')),
               sg.Button('打开时间戳', font=font, button_color=('grey0', 'grey100'), key='open_timestamp'),
               sg.Button('实时保存数据', font=font, size=(14, 1), button_color=('grey0', 'grey100'),
                         key='real_time_save_data'),
               sg.Button('保存全部数据', font=font, button_color=('grey0', 'grey100'), key='save_all_data'),
               sg.Button('一键跳转', font=font, button_color=('grey0', 'grey100'), key='skip_to_file'),
               sg.Button('配置', button_color=('grey0', 'grey100'), pad=((200, 1), (1, 1)), key='config', size=(9, 1)),
               sg.Button('波形绘制', button_color=('grey0', 'grey100'), key='wave', size=(9, 1))],

              [Collapsible(sec1_layout, 'sec1_key', '过滤设置', font=font, collapsed=True)],

              [sg.Multiline(autoscroll=True, key=DB_OUT, size=(100, 25), right_click_menu=right_click_menu,
                            font=(font + font_size + ' bold'))],

              [sg.Frame('', tx_data_layout, key='tx_button'), sg.Multiline('', font=(font + font_size + ' bold'),
                                                                           key='data_input', size=(89, 4),
                                                                           enable_events=False),
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

    window = sg.Window(rtt_cur_version, layout, finalize=True, resizable=True, icon=APP_ICON)

    window.set_min_size(window.size)
    window[DB_OUT].expand(True, True, True)
    window['data_input'].expand(True, True, True)
    window['history_data'].expand(True, False, False)

    update_connect_button_text(window, js_cfg['hw_sel'])
    jk_obj = bds_jk.BDS_Jlink(hw_error, hw_warn, char_format=js_cfg['char_format'])
    ser_obj = bds_ser.BDS_Serial(hw_error, hw_warn, char_format=js_cfg['char_format'])

    hw_obj = jk_obj
    threading.Thread(target=hw_rx_thread, daemon=True).start()
    threading.Thread(target=version_detect_thread, args=(window, rtt_cur_version), daemon=True).start()

    # 启动键盘监听线程
    threading.Thread(target=listen_for_arrow_keys, daemon=True).start()

    mul_scroll = False
    real_time_save_file_name = ''
    log_remain_str = ''

    wv.wave_init()
    hw_obj.reg_dlog_M_callback(wv.wave_data)
    ser_obj.reg_dlog_M_callback(wv.wave_data)

    sg.cprint_set_output_destination(window, DB_OUT)

    time_diff = td.TimeDifference()

    rtt_update = ''
    data_input_focus_state = False
    text_focus_state = False
    new_index = 0
    find_window = None
    text_widget = window[DB_OUT].Widget
    last_search_keyword = ''
    last_search_index = '1.0'
    last_highlight_end = '1.0'
    search_direction = 'next'

    while True:
        win, event, values = sg.read_all_windows(timeout=150)

        if win == window and event == sg.WIN_CLOSED:
            hw_obj.hw_close()
            break

        try:
            focus = window.find_element_with_focus()
            text_focus_state = False if focus is None else True
            if focus != 'popdown':
                data_input_focus_state = True if focus == window['data_input'] else False
        except:
            pass

        y1, y2 = text_widget.yview()
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
            sg.popup(values['hw_error'], icon=APP_ICON)
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
                sg.popup('[Error]无数据!!!', icon=APP_ICON)
        elif event == '滚动到最底端':
            mul_scroll = True
            window[DB_OUT].update(autoscroll=True)
        elif event == '清除窗口数据':
            window[DB_OUT].update('')
        elif event == 'tx_data':
            if hw_obj.hw_is_open():
                input_data = window['data_input'].get()
                js_cfg['user_input_data'] = update_user_input_list(input_data, js_cfg['user_input_data'])
                window['history_data'].update(input_data, values=js_cfg['user_input_data'])
                with open('config.json', 'w') as f:
                    json.dump(js_cfg, f, indent=4)
                if window['tx_data_type'].get() == 'HEX':
                    try:
                        print([int(i, 16) for i in input_data.split(' ')])
                        hw_obj.hw_write([int(i, 16) for i in input_data.split(' ')])
                    except:
                        sg.popup_no_wait('数据格式错误。数据类型请选择HEX，数据之间用空格隔开。', icon=APP_ICON)
                else:
                    try:
                        input_data = extract_outside_brackets_corrected(input_data) + js_cfg['line_break']
                        print(input_data)
                        hw_obj.hw_write([ord(i) for i in input_data])
                    except Exception as e:
                        sg.popup_no_wait("%s" % e, icon=APP_ICON)
            else:
                sg.popup('请先连接硬件', icon=APP_ICON)
        elif event == 'history_data':
            window['data_input'].update(window['history_data'].get())
        elif event is not None and event.startswith('sec1_key'):
            window['sec1_key'].update(visible=not window['sec1_key'].visible)
            window['sec1_key' + '-BUTTON-'].update(
                window['sec1_key'].metadata[0] if window['sec1_key'].visible else window['sec1_key'].metadata[1])
        elif event is not None and event.startswith('sec2_key'):
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
                err_code = hw_config_dialog(js_cfg)
                if err_code == 0:
                    update_connect_button_text(window, js_cfg['hw_sel'])
                    hw_obj.hw_set_char_format(js_cfg['char_format'])
                elif err_code == 1:
                    hw_obj.hw_close()
                    break
            else:
                sg.popup_no_wait('请先断开硬件连接！', icon=APP_ICON)
        elif event == 'wave':
            if hw_obj.hw_is_open():
                if len(js_cfg['curves_name']) > 0:
                    wv.wave_cmd('wave reset')
                    wv.startup_wave(js_cfg['y_range'], js_cfg['y_label_text'],
                                    [v for v in js_cfg['curves_name'].split('&&') if v != ''])
                else:
                    sg.popup_no_wait('没有设置任何轴名称，请至少设置一个轴名称', icon=APP_ICON)
            else:
                sg.popup_no_wait('请先连接硬件', icon=APP_ICON)
        elif event == 'skip_to_file':
            try:
                os.startfile(os.path.dirname(os.path.realpath(sys.argv[0])) + '\\aaa_log')
            except Exception as e:
                sg.popup_no_wait("%s" % e, icon=APP_ICON)
        elif event == 'latest_release':
            rtt_update = update_reminder_dialog(font, values['latest_release'])
            if rtt_update != '':
                break
        elif data_input_focus_state and (event == 'KEY_UP' or event == 'KEY_DOWN'):
            new_item, new_index = get_next_item(js_cfg['user_input_data'], new_index, event)
            if new_item is not None and new_item != '':
                window['data_input'].update(new_item)
        elif event == 'CTRL_F':
            if not find_window and text_focus_state:
                # 创建一个搜索窗体
                find_window = create_find_window(font=font)
                last_search_keyword = ''

        if win == find_window and find_window is not None and event is None:
            # 移除全部标签
            text_widget.tag_remove('found', '1.0', tk.END)
            text_widget.tag_remove('current', '1.0', tk.END)
            find_window.close()
            find_window = None
        elif event in ('find_next', 'find_pre'):
            find_key = find_window['find_key'].get()
            if find_key == '':
                sg.popup('请输入需要查找字符串', icon=APP_ICON)
                continue
            if find_key != last_search_keyword:
                # text_widget.tag_remove('found', '1.0', tk.END)
                # text_widget.tag_remove('current', '1.0', tk.END)
                if highlight_text(text_widget, find_key, 'found') is None:
                    sg.popup('没有找到目标字符串', icon=APP_ICON)
                    continue
                last_search_keyword = find_key
                last_search_index = '1.0'
                last_highlight_end = text_widget.index(tk.END)
                last_highlight_end = text_widget.index(f"{last_highlight_end}-1c")
                search_direction = 'next'  # 重置搜索方向
            try:
                if event == 'find_next':
                    if search_direction == 'prev':  # 如果之前是向上搜索
                        last_search_index = text_widget.index(f"{last_search_index}+{len(last_search_keyword)}c")
                        search_direction = 'next'
                    next_index = text_widget.search(last_search_keyword, last_search_index, stopindex=tk.END)
                    if next_index:
                        if text_widget.tag_ranges('current'):
                            start_current = text_widget.index('current.first')
                            text_widget.tag_remove('current', start_current, tk.END)
                        end_index = text_widget.index(f"{next_index}+{len(last_search_keyword)}c")
                        # 判断是否需要高亮新的文本
                        print(next_index, last_highlight_end)
                        if text_widget.compare(next_index, '>=', last_highlight_end):
                            # 从其上一个位置开始高亮
                            start_highlight = text_widget.index(f"{next_index}-1c")
                            highlight_text(text_widget, last_search_keyword, 'found', start=start_highlight)
                            last_highlight_end = text_widget.index(tk.END)

                        highlight_current(text_widget, next_index, end_index, 'current')
                        text_widget.see(next_index)
                        last_search_index = end_index
                    else:
                        sg.popup_no_wait('未找到更多匹配信息!', title='警告', icon=APP_ICON, font=font, keep_on_top=True)
                        last_search_index = '1.0'  # 重置搜索索引
                else:
                    if search_direction == 'next':  # 如果之前是向下搜索
                        # 先检查 last_search_index 是否已经指向一个已找到的字符串
                        if text_widget.tag_ranges('current'):
                            # 将 last_search_index 移动到当前聚焦字符串的开始位置
                            current_start = text_widget.index('current.first')
                            # 然后向前移动一个字符
                            last_search_index = text_widget.index(f"{current_start}-1c")
                        search_direction = 'prev'
                    previous_index = find_previous(text_widget, find_key, start=last_search_index)
                    if previous_index:
                        if text_widget.tag_ranges('current'):
                            start_current = text_widget.index('current.first')
                            text_widget.tag_remove('current', start_current, tk.END)
                        end_index = text_widget.index(f"{previous_index}+{len(last_search_keyword)}c")
                        highlight_current(text_widget, previous_index, end_index, 'current')
                        text_widget.see(previous_index)
                        last_search_index = previous_index
                    else:
                        sg.popup_no_wait('未找到更多匹配信息!', title='警告', icon=APP_ICON, font=font, keep_on_top=True)
            except Exception as e:
                log.info(str(e))
                sg.popup('Error:', str(e), icon=APP_ICON, font=font)

        log_process(window, hw_obj, js_cfg, auto_scroll=mul_scroll)
        # time_diff.print_time_difference()

    if rtt_update != '':
        print(rtt_update)
        os.startfile(rtt_update)

    if find_window is not None:
        find_window.close()
    window.close()


if __name__ == '__main__':
    main()
