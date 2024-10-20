import tkinter as tk
import PySimpleGUI as sg

class TextSearcher:
    def __init__(self, text_widget, icon):
        self._text_widget = text_widget
        self._last_search_keyword = ''
        self._last_search_index = '1.0'
        self._last_highlight_end = '1.0'
        self._search_direction = 'next'
        self.icon = icon

    def search(self, keyword, direction):
        if keyword != self._last_search_keyword:
            self._clear_previous_search()
            if not self._highlight_all(keyword):
                return False
            self._reset_search(keyword)
        
        try:
            if direction == 'next':
                return self._search_next(keyword)
            else:
                return self._search_previous(keyword)
        except Exception as e:
            sg.popup('Error:', str(e), icon=self.icon)
            return False

    def reset(self):
        self._last_search_keyword = ''
        self._last_search_index = '1.0'
        self._last_highlight_end = '1.0'
        self._search_direction = 'next'
        self._clear_previous_search()

    def _clear_previous_search(self):
        self._text_widget.tag_remove('found', '1.0', tk.END)
        self._text_widget.tag_remove('current', '1.0', tk.END)

    def _highlight_all(self, keyword):
        if self._highlight_text(keyword, 'found') is None:
            sg.popup('没有找到目标字符串', icon=self.icon)
            return False
        return True

    def _reset_search(self, keyword):
        self._last_search_keyword = keyword
        self._last_search_index = '1.0'
        self._last_highlight_end = self._text_widget.index(f"{self._text_widget.index(tk.END)}-1c")
        self._search_direction = 'next'

    def _search_next(self, keyword):
        if self._search_direction == 'prev':
            self._last_search_index = self._text_widget.index(f"{self._last_search_index}+{len(keyword)}c")
        self._search_direction = 'next'
        next_index = self._text_widget.search(keyword, self._last_search_index, stopindex=tk.END)
        if next_index:
            end_index = self._text_widget.index(f"{next_index}+{len(keyword)}c")
            self._highlight_current(next_index, end_index)
            self._text_widget.see(next_index)
            self._last_search_index = end_index
            return True
        else:
            self._handle_no_more_matches()
            self._last_search_index = '1.0'
            return False

    def _search_previous(self, keyword):
        if self._search_direction == 'next':
            if self._text_widget.tag_ranges('current'):
                current_start = self._text_widget.index('current.first')
                self._last_search_index = current_start
            else:
                self._last_search_index = self._text_widget.index(tk.END)
        self._search_direction = 'prev'
        
        previous_index = self._find_previous(keyword, start=self._last_search_index)
        if previous_index:
            end_index = self._text_widget.index(f"{previous_index}+{len(keyword)}c")
            self._highlight_current(previous_index, end_index)
            self._text_widget.see(previous_index)
            self._last_search_index = previous_index
            return True
        else:
            self._handle_no_more_matches()
            self._last_search_index = self._text_widget.index(tk.END)
            return False

    def _highlight_current(self, start, end):
        self._text_widget.tag_remove('current', '1.0', tk.END)
        self._text_widget.tag_add('current', start, end)
        self._text_widget.tag_config('current', background='dark grey')

    def _handle_no_more_matches(self):
        sg.popup_no_wait('未找到更多匹配信息!', title='警告', keep_on_top=True, icon=self.icon)

    def _highlight_text(self, keyword, tag, start='1.0', end=tk.END):
        current = start
        first_match = None
        while True:
            current = self._text_widget.search(keyword, current, stopindex=end)
            if not current:
                break
            if not first_match:
                first_match = current
            end_match = self._text_widget.index(f"{current}+{len(keyword)}c")
            self._text_widget.tag_add(tag, current, end_match)
            current = end_match
        self._text_widget.tag_config(tag, background='yellow')
        return first_match

    def _find_previous(self, keyword, start='end', end='1.0'):
        current = self._text_widget.index(start)
        while True:
            current = self._text_widget.search(keyword, current, stopindex=end, backwards=True)
            if not current:
                break
            return current
        return None
