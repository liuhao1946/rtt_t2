import PySimpleGUI as sg
import tkinter as tk

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
    widget.tag_add(current_tag, start, end)
    widget.tag_config(current_tag, background='blue', foreground='white')  # 当前聚焦项的高亮配置

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
    data = "123nihao\nabctest\ncdfnif\n...\ntest2\n..."
    sg.theme('DefaultNoMoreNagging')
    layout = [
        [sg.Multiline(data, size=(40, 20), key='-TEXT-')],
        [sg.Input(key='-SEARCH-'), sg.Button('Find Next', key='-FIND-NEXT-'), sg.Button('Find Previous', key='-FIND-PREV-')]
    ]

    window = sg.Window('Text Search', layout, finalize=True)
    text_widget = window['-TEXT-'].Widget
    last_search_keyword = ''
    last_search_index = '1.0'
    last_highlight_end = '1.0'
    search_direction = 'next'  # 添加一个变量来跟踪搜索方向

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event in ('-FIND-NEXT-', '-FIND-PREV-'):
            search_keyword = values['-SEARCH-']
            if search_keyword != last_search_keyword:
                last_search_keyword = search_keyword
                text_widget.tag_remove('found', '1.0', tk.END)
                text_widget.tag_remove('current', '1.0', tk.END)
                last_search_index = '1.0'
                last_highlight_end = '1.0'
                highlight_text(text_widget, last_search_keyword, 'found')
                search_direction = 'next'  # 重置搜索方向

            if event == '-FIND-NEXT-':
                if search_direction == 'prev':  # 如果之前是向上搜索
                    last_search_index = text_widget.index(f"{last_search_index}+{len(last_search_keyword)}c")
                    search_direction = 'next'
                next_index = text_widget.search(last_search_keyword, last_search_index, stopindex=tk.END)
                if next_index:
                    text_widget.tag_remove('current', '1.0', tk.END)
                    end_index = text_widget.index(f"{next_index}+{len(last_search_keyword)}c")

                    if text_widget.compare(next_index, '>=', last_highlight_end):
                        highlight_text(text_widget, last_search_keyword, 'found', start=next_index)
                        last_highlight_end = text_widget.index(tk.END)

                    highlight_current(text_widget, next_index, end_index, 'current')
                    text_widget.see(next_index)
                    last_search_index = end_index
                else:
                    sg.popup('No more matches found')
                    last_search_index = '1.0'
            else:
                if search_direction == 'next':  # 如果之前是向下搜索
                    # 先检查 last_search_index 是否已经指向一个已找到的字符串
                    if text_widget.tag_ranges('current'):
                        # 将 last_search_index 移动到当前聚焦字符串的开始位置
                        current_start = text_widget.index('current.first')
                        # 然后向前移动一个字符
                        last_search_index = text_widget.index(f"{current_start}-1c")
                    search_direction = 'prev'
                previous_index = find_previous(text_widget, last_search_keyword, start=last_search_index)
                if previous_index:
                    text_widget.tag_remove('current', '1.0', tk.END)
                    end_index = text_widget.index(f"{previous_index}+{len(last_search_keyword)}c")
                    highlight_current(text_widget, previous_index, end_index, 'current')
                    text_widget.see(previous_index)
                    last_search_index = previous_index
                else:
                    sg.popup('No more matches found')

    window.close()


if __name__ == '__main__':
    main()
