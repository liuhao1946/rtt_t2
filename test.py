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

def main():
    data = "123nihao\nabctest\ncdfnif\n...\ntest2\n..."
    sg.theme('DefaultNoMoreNagging')
    layout = [
        [sg.Multiline(data, size=(40, 20), key='-TEXT-')],
        [sg.Input(key='-SEARCH-'), sg.Button('Find', key='-FIND-')]
    ]

    window = sg.Window('Text Search', layout, finalize=True)
    text_widget = window['-TEXT-'].Widget
    last_search_keyword = ''
    last_search_index = '1.0'
    last_highlight_end = '1.0'

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == '-FIND-':
            search_keyword = values['-SEARCH-']

            if search_keyword != last_search_keyword:
                last_search_keyword = search_keyword
                text_widget.tag_remove('found', '1.0', tk.END)
                text_widget.tag_remove('current', '1.0', tk.END)
                last_search_index = '1.0'
                last_highlight_end = '1.0'
                highlight_text(text_widget, last_search_keyword, 'found')

            next_index = text_widget.search(last_search_keyword, last_search_index, stopindex=tk.END)
            if next_index:
                text_widget.tag_remove('current', '1.0', tk.END)
                end_index = text_widget.index(f"{next_index}+{len(last_search_keyword)}c")

                # 判断是否需要高亮新的文本
                if text_widget.compare(next_index, '>', last_highlight_end):
                    highlight_text(text_widget, last_search_keyword, 'found', start=next_index)
                    last_highlight_end = text_widget.index(tk.END)

                highlight_current(text_widget, next_index, end_index, 'current')
                text_widget.see(next_index)
                last_search_index = end_index
            else:
                sg.popup('No more matches found')
                last_search_index = '1.0'  # 重置搜索索引

    window.close()

if __name__ == '__main__':
    main()
