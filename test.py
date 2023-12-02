import PySimpleGUI as sg
import tkinter as tk

def highlight_text(widget, keyword, tag, start='1.0'):
    """高亮显示关键字，并返回第一个匹配项的位置。"""
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
        widget.tag_config(tag, background='yellow', foreground='black')
        current = end
    return first_match

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
                last_search_index = '1.0'

            if last_search_keyword:
                next_index = highlight_text(text_widget, last_search_keyword, 'found', last_search_index)
                if next_index:
                    text_widget.see(next_index)
                    last_search_index = text_widget.index(f"{next_index}+{len(last_search_keyword)}c")
                else:
                    sg.popup('No more matches found')
                    last_search_index = '1.0'

    window.close()

if __name__ == '__main__':
    main()
