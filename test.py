import PySimpleGUI as sg
import tkinter as tk

def highlight_text(widget, keyword, tag, current_tag, start='1.0'):
    """高亮显示所有匹配项，并返回第一个匹配项的位置。"""
    first_match = None
    current = start
    while True:
        current = widget.search(keyword, current, stopindex=tk.END)
        if not current:
            break
        if not first_match:
            first_match = current
        end = widget.index(f"{current}+{len(keyword)}c")
        widget.tag_add(tag, current, end)
        widget.tag_config(tag, background='yellow')  # 普通高亮配置
        current = end
    return first_match

def highlight_current(widget, start, end, current_tag):
    """高亮显示当前聚焦的匹配项。"""
    widget.tag_add(current_tag, start, end)
    widget.tag_config(current_tag, background='magenta')  # 当前聚焦项的高亮配置

def main():
    data = "123nihao\nabctest\ncdfnif\n...\ntest2\n...123nihaoppp\nabctest\ncdfnif\n...\ntest2\n..." \
           "123nihao\nabctest\ncdfnif\n...\ntest2\n...123nihao\nabctest\ncdfnif\n...\ntest2\n..." \
           "123nihao\nabctest\ncdfnif\n...\ntest2\n...123nihao\nabctest\ncdfnif\n...\ntest2\n..." \
           "123nihao\nabctest\ncdfnif\n...\ntest2\n...123nihao\nabctest\ncdfnifppp\n...\ntest2\n..."
    sg.theme('DefaultNoMoreNagging')
    layout = [
        [sg.Multiline(data, size=(40, 20), key='-TEXT-')],
        [sg.Input(key='-SEARCH-'), sg.Button('Find', key='-FIND-')]
    ]

    window = sg.Window('Text Search', layout, finalize=True)
    text_widget = window['-TEXT-'].Widget
    last_search_keyword = ''
    last_search_index = '1.0'

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == '-FIND-':
            if values['-SEARCH-'] != last_search_keyword:
                last_search_keyword = values['-SEARCH-']
                text_widget.tag_remove('found', '1.0', tk.END)
                text_widget.tag_remove('current', '1.0', tk.END)
                last_search_index = '1.0'

            if last_search_keyword:
                next_index = highlight_text(text_widget, last_search_keyword, 'found', 'current', last_search_index)
                if next_index:
                    text_widget.tag_remove('current', '1.0', tk.END)  # 移除旧的当前标签
                    end_index = f"{next_index}+{len(last_search_keyword)}c"
                    highlight_current(text_widget, next_index, end_index, 'current')
                    text_widget.see(next_index)
                    last_search_index = end_index
                else:
                    sg.popup('No more matches found')
                    last_search_index = '1.0'

    window.close()

if __name__ == '__main__':
    main()
