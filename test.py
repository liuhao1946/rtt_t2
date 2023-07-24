import re


color_pat = re.compile(r'BDSCOL\((\d{1,8})\)', re.I)


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


def log_print_line(s, auto_scroll=True):
    sv = ''
    need_s = ''
    color = 0
    pre_color = -1
    line_tag = re.findall('.+\n', s)
    for idx, v in enumerate(line_tag):
        match = color_pat.search(v)
        if match is None:
            if pre_color >= 0:
                print('1', 'text_color=#%06d' % pre_color, sv)
                # sg.cprint(sv, text_color='#%06X' % pre_color, end='', autoscroll=auto_scroll)
                sv = ''
                pre_color = -1
            sv += v
            need_s += v
            color = -1
        else:
            # 打印上一次v_idx < 0时的颜色(默认颜色)
            if sv != '' and color == -1:
                print('2', 'text_color=#%06X' % 0, sv)
                # sg.cprint(sv, text_color='#%06X' % 0, end='', autoscroll=auto_scroll)
                sv = ''
            try:
                color = int(match.group(1))  # 提取匹配的数字并转换为整数
                print('color:%d' % color)
            except Exception as e:
                # win[DB_OUT].write('[BDS LOG]RAW string:%s,color error:%s,error code:%s\n' % (s, v, e))
                # log.info('RAW string:%s,color error:%s,error code:%s\n' % (s, v, e))
                color = 0
            if pre_color < 0:
                pre_color = color
            if color == pre_color:
                temp_s = delete_str('BDSCOL\([0-9]{1,8}\)', v)
                need_s += temp_s
                sv += temp_s
            else:
                # 输出上一个颜色的字符串
                print('3', 'text_color=#%06X' % pre_color, sv)
                # sg.cprint(sv, text_color='#%06X' % pre_color, end='', autoscroll=auto_scroll)
                sv = delete_str('BDSCOL\([0-9]{1,8}\)', v)
                need_s += sv
            pre_color = color
    if color < 0:
        color = 0
    if sv != '':
        print('4', 'text_color=#%06X' % color, sv)
        # sg.cprint(sv, text_color='#%06X' % color, end='', autoscroll=auto_scroll)

    return need_s

s = 'BDSCOL(35584)[app_bat_init] current bat percent:0\n'

log_print_line(s)
