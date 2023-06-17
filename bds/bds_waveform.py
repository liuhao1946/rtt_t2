import time
from time import perf_counter
import pyqtgraph as pg
from multiprocessing import Process, Queue, Value
# from pyqtgraph.graphicsItems.ViewBox import ViewBox
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import math
from functools import partial

global wave_data_q, wave_run_flag, wave_cmd_q, wave_obj, wave_pause_flag

# app = pg.mkQApp()
# from datetime import datetime

MENU_PAUSE_TEXT = ['暂停', '开始']
MENU_REGION_TEXT = ['打开区域统计', '关闭统计区域']
MENU_GO_BACK_WAVE_FRONT = ['回到波形最前端']
MENU_HIDE_TEXT = ['显示波形', '☑', '□']


def find_nearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx - 1]) < math.fabs(value - array[idx])):
        return idx - 1
    else:
        return idx


def wave_queue_clr(q):
    q_z = q.qsize()
    for _ in range(q_z):
        q.get()


def app_range(start, dt, num):
    r = []
    for idx in range(num):
        start += dt
        r.append(start)

    return r


class waveform:
    def __init__(self, wave_sample_start, data_q, cmd_q, plot, pen_color, name, y_range,
                 y_text='', y_unit='', x_text='Time', x_unit='s', label_xy=None, label_odr=None):
        # self.start_time_s = self.last_time_s = perf_counter()
        self.last_run_s = self.run_s = perf_counter()
        self.start_time_s = self.last_time_s = 0
        self.cur_time_s = 0
        self.sta_inf_update_time = 0
        self.curve_max_point = 0
        self.mouse_press_x = 0
        self.mouse_move_x = 0
        self.curve_start_move = False
        self.curve_move_pause = False
        self.start_move_index = 0
        self.mouse_is_press = False
        self.mouse_move_sensitivity = 0.2
        self.visible_area_max_point = 0
        self.wave_sample_start = wave_sample_start
        # 0表示raw,1表示raw/lsb
        # self.data_type = data_type
        self.sta_inf_update_time_s = 5
        self.x_time_s = []
        self.y_data = {}
        self.curve = []
        self.curve_pen_color = pen_color
        self.axis_name = name
        self.data_q = data_q
        self.cmd_q = cmd_q
        self.plot = plot
        self.vb = plot.getViewBox()
        self.axis_x = plot.getAxis('bottom')
        self.axis_x.setTickSpacing(major=1, minor=1)
        # 根据name创建空列表
        for n in name:
            self.y_data[n] = []
        self.plot.addLegend()
        # 创建画布
        for i in range(len(name)):
            self.curve.append(self.plot.plot(pen=pg.mkPen(self.curve_pen_color[i], width=2), name=self.axis_name[i]))
        # for cur in self.curve:
        #    cur.setSymbol('o')
        #    cur.setSymbolSize(3)

        self.plot.setLabel('bottom', x_text, x_unit)
        self.plot.setLabel('left', text=y_text, units=y_unit)
        self.plot.setYRange(y_range[0], y_range[1])
        self.plot.showGrid(x=True, y=True)
        self.plot.setMouseEnabled(x=False, y=True)
        # 增加上下文菜单项
        # self.vb.menu.addMenu('2_0')
        self.menu_pause = self.vb.menu.addAction(MENU_PAUSE_TEXT[0])
        self.menu_pause.triggered.connect(self.menu_context_pause)
        self.menu_region = self.vb.menu.addAction(MENU_REGION_TEXT[0])
        self.menu_region.triggered.connect(self.menu_context_region)
        self.wave_front = self.vb.menu.addAction(MENU_GO_BACK_WAVE_FRONT[0])
        self.wave_front.triggered.connect(self.go_back_wave_front)

        self.wave_is_display = [True for _ in self.axis_name]
        self.menu_hide_curve = self.vb.menu.addMenu(MENU_HIDE_TEXT[0])
        self.menu_hide_action = []
        for index, v in enumerate(self.axis_name):
            self.menu_hide_action.append(self.menu_hide_curve.addAction(MENU_HIDE_TEXT[1] + ' ' + v))
            self.menu_hide_action[index].triggered.connect(partial(self.wave_hide, v))

        # 这里要修改GrahicsScene.py
        self.plot.scene().sigMousePress.connect(self.mouse_press)
        self.plot.scene().sigMouseRelease.connect(self.mouse_release)
        self.plot.scene().sigMouseMoved.connect(self.mouse_move)
        # self.proxy = pg.SignalProxy(self.plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_move)

        self.menu_x_range = self.vb.menu.addMenu('X轴可视范围')
        self.x_range_x10 = self.menu_x_range.addAction('☑ 10s')
        self.x_range_x5 = self.menu_x_range.addAction(' 5s')
        self.x_range_x2 = self.menu_x_range.addAction(' 2s')
        self.x_range_x10.triggered.connect(self.x_axis_range_x10)
        self.x_range_x2.triggered.connect(self.x_axis_range_x2)
        self.x_range_x5.triggered.connect(self.x_axis_range_x5)

        self.forced_update_wave = False

        # 区域标签
        self.lr = pg.LinearRegionItem()
        # 文本标签
        self.text = pg.TextItem("sta", anchor=(0, 0), angle=0, border='w', fill=(0, 0, 255, 100))

        self.label_odr = label_odr

        self.data_save_max_time_min = 6
        self.curve_start_move_time_s = 10
        self.drag_start_distance = 20
        self.curve_start_move_time_s_last = 0
        self.label_xy = label_xy
        self.right_but_is_press = False
        self.odr_update_time = 0

        self.dt_interval = []
        self.dt_num = []
        self.mean_dt = 0

    def set_wave_display(self, index, display=True):
        self.wave_is_display[index] = display
        if display:
            self.curve[index].setPen(self.curve_pen_color[index], width=2)
        else:
            # RGBA
            self.curve[index].setPen('#00000000', width=1)

    def wave_hide(self, curver_name):
        index = self.axis_name.index(curver_name)
        if self.menu_hide_action[index].text().startswith(MENU_HIDE_TEXT[1]):
            self.menu_hide_action[index].setText(MENU_HIDE_TEXT[2] + ' ' + self.axis_name[index])
            self.set_wave_display(index, display=False)
        else:
            self.set_wave_display(index)
            self.menu_hide_action[index].setText(MENU_HIDE_TEXT[1] + ' ' + self.axis_name[index])

    def sta_inf_update_time_set_ms(self, ms):
        # self.sta_inf_update_time_s = ms / 10
        pass

    def x_axis_range_x10(self):
        self.curve_start_move_time_s = 10
        self.drag_start_distance = 20
        self.x_range_x10.setText('☑ 10s')
        self.x_range_x5.setText(' 5s')
        self.x_range_x2.setText(' 2s')

    def x_axis_range_x5(self):
        self.curve_start_move_time_s = 5
        self.drag_start_distance = 15
        self.x_range_x10.setText(' 10s')
        self.x_range_x5.setText('☑ 5s')
        self.x_range_x2.setText(' 2s')

    def x_axis_range_x2(self):
        self.curve_start_move_time_s = 2
        self.drag_start_distance = 3
        self.x_range_x10.setText('10s')
        self.x_range_x5.setText('5s')
        self.x_range_x2.setText('☑ 2s')

    def mouse_press(self, ev):
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = ev.scenePos()
            if self.vb.sceneBoundingRect().contains(pos) and not self.right_but_is_press:
                # self.mouse_press_x = self.vb.mapToView(QtCore.QPointF(pos.x(), 0)).x()
                self.mouse_press_x = pos.x()
                if self.menu_region.text() == MENU_REGION_TEXT[1]:
                    region = self.lr.getRegion()
                    # NOTE:视图坐标与感知坐标不一样
                    r_map_x1 = self.vb.mapToView(QtCore.QPointF(region[0], 0)).x()
                    r_map_x2 = self.vb.mapToView(QtCore.QPointF(region[1], 0)).x()
                    press_x1 = self.vb.mapSceneToView(pos).x()

                    if press_x1 < r_map_x1 - 0.2 or press_x1 > r_map_x2 + 0.2:
                        self.mouse_is_press = True
                else:
                    self.mouse_is_press = True
            self.right_but_is_press = False
        else:
            self.right_but_is_press = True

    def mouse_release(self, ev):
        self.mouse_is_press = False

    def mouse_move(self, pos):
        # 右键上下文菜单打开后，移动鼠标时没有鼠标移动事件
        if self.vb.sceneBoundingRect().contains(pos):
            # if self.label != None:
            map_pos = self.vb.mapSceneToView(pos)
            self.label_xy.setText('x:%0.6f' % map_pos.x() + ' y:%0.6f' % map_pos.y())
            self.mouse_move_x = pos.x()
            # print(self.mouse_move_x)

    def mouse_move_sensitivity_set(self, sensitivity):
        self.mouse_move_sensitivity = sensitivity

    def wave_set_start_move_time_s(self, time_s=10):
        if time_s < 3:
            time_s = 3
        self.curve_start_move_time_s = time_s

    def wave_set_data_save_max_time_min(self, time_min):
        if time_min < 1:
            time_min = 1
        self.data_save_max_time_min = time_min

    def wave_cmd_rx(self):
        q_size = self.cmd_q.qsize()
        if q_size > 0:
            cmd = self.cmd_q.get()
            if cmd == 'wave reset':
                self.wave_update_start()

    def wave_update(self):
        """
        定时调用
        """
        # 解析来自主进程的命令
        self.wave_cmd_rx()

        self.sta_inf_update_time += 1
        if self.sta_inf_update_time > self.sta_inf_update_time_s:
            self.sta_inf_update_time = 0
            self.region_sta_inf_view()

        self.odr_update_time += 1
        if self.odr_update_time >= 100:
            self.odr_update_time = 0
            if self.mean_dt != 0:
                odr_str = 'Mean ODR: %0.1f Hz' % (1 / self.mean_dt)
            else:
                odr_str = 'Mean ODR: in calculation...'
            self.label_odr.setText(odr_str)

        if self.wave_sample_start.value:
            self.run_s = perf_counter()
            q_size = self.data_q.qsize()
            if q_size > 0:
                # 估算点间隔
                self.dt_interval.append(self.run_s - self.last_run_s)
                self.dt_num.append(q_size)
                if len(self.dt_interval) > 20:
                    del self.dt_interval[0]
                    del self.dt_num[0]
                self.mean_dt = sum(self.dt_interval) / sum(self.dt_num)
                self.last_run_s = self.run_s

                # 确保点与点之间是dt的整数倍，否则曲线点之间的时间是不均匀的
                self.x_time_s += app_range(self.cur_time_s, self.mean_dt, q_size)
                self.cur_time_s = self.x_time_s[-1]

                for _ in range(q_size):
                    data = self.data_q.get()
                    index = 0
                    data_len = len(data)
                    axis_len = len(self.axis_name)
                    if data_len > axis_len:
                        data = data[:-(data_len - axis_len)]

                    # print(data)
                    for _, v in enumerate(data):
                        self.y_data[self.axis_name[index]].append(v)
                        index += 1

                # 超过指定的时间需要删除一些内容，以节省内存
                if self.cur_time_s > self.data_save_max_time_min * 60:
                    del self.x_time_s[0:q_size]
                    for name in self.axis_name:
                        del self.y_data[name][0:q_size]

                state = self.visible_area_change()
                if not self.wave_drag():
                    if self.cur_time_s <= self.data_save_max_time_min * 60:
                        self.curve_max_point += q_size

                    # print(self.curve_max_point)
                    start_idx = self.curve_max_point - self.visible_area_max_point
                    end_idx = self.curve_max_point
                    for index, c in enumerate(self.curve):
                        c.setData(x=self.x_time_s[start_idx:end_idx],
                                  y=self.y_data[self.axis_name[index]][start_idx:end_idx])
                elif state:
                    self.forced_update_wave = True

        else:
            # 如果波形被暂停，只检测拖拽动作
            if self.visible_area_change():
                self.forced_update_wave = True
            self.wave_drag()

        if self.forced_update_wave:
            start_idx = self.curve_max_point - self.visible_area_max_point
            end_idx = self.curve_max_point
            for index, c in enumerate(self.curve):
                c.setData(x=self.x_time_s[start_idx:end_idx],
                          y=self.y_data[self.axis_name[index]][start_idx:end_idx])
            self.forced_update_wave = False

    def visible_area_change(self):
        state = False
        delta_time_s = self.cur_time_s - self.start_time_s
        if delta_time_s >= self.curve_start_move_time_s:
            if self.curve_start_move_time_s_last != self.curve_start_move_time_s:
                state = self.curve_start_move = True
                s_idx = find_nearest(self.x_time_s, self.cur_time_s - self.curve_start_move_time_s)
                self.visible_area_max_point = len(self.x_time_s[s_idx:])
                self.curve_start_move_time_s_last = self.curve_start_move_time_s
        else:
            self.curve_start_move = False
            self.visible_area_max_point = self.curve_max_point

        return state

    def wave_drag(self):
        if self.mouse_is_press and self.curve_start_move:
            distance = self.mouse_move_x - self.mouse_press_x
            # print(self.mouse_move_x,self.mouse_press_x,self.mouse_move_x-self.mouse_press_x)
            if distance >= self.drag_start_distance or distance <= -self.drag_start_distance:
                # print(distance)
                self.curve_move_pause = True
                self.mouse_press_x = self.mouse_move_x
                # TODO:缩放系数最好根据点的时间间隔来确定。点越密集，移动点数应该越多才对
                if self.mean_dt != 0:
                    move_point_count = int((40.0 / (self.mean_dt * 1000)) * distance)
                else:
                    move_point_count = int(distance)
                self.curve_max_point -= move_point_count

                data_len = len(self.x_time_s)
                if self.curve_max_point >= data_len:
                    self.curve_max_point = data_len
                    self.curve_move_pause = False
                if self.curve_max_point < self.visible_area_max_point:
                    self.curve_max_point = self.visible_area_max_point

                start_idx = self.curve_max_point - self.visible_area_max_point
                end_idx = self.curve_max_point
                for index, c in enumerate(self.curve):
                    c.setData(x=self.x_time_s[start_idx:end_idx],
                              y=self.y_data[self.axis_name[index]][start_idx:end_idx])
        return self.curve_move_pause

    def wave_update_stop(self):
        # self.plot.setMouseEnabled(x=True, y=True)
        self.wave_sample_start.value = 0

    def wave_update_start(self):
        # self.plot.setMouseEnabled(x=False, y=True)
        self.wave_sample_start.value = 1
        self.curve_max_point = 0
        self.curve_start_move = False
        self.curve_move_pause = False
        self.curve_start_move_time_s_last = 0

        del self.x_time_s[:]
        for index in range(len(self.axis_name)):
            del self.y_data[self.axis_name[index]][:]

        self.last_time_s = 0
        self.cur_time_s = self.start_time_s = 0
        self.last_run_s = self.run_s = perf_counter()

        self.dt_interval = []
        self.dt_num = []

        # self.last_time_s = self.start_time_s = perf_counter()
        # TODO:进程队列可能有队列清除方法
        # self.data_q.queue.clear()
        wave_queue_clr(self.data_q)
        # self.data_q.queue.clear()

    def region_to_list_index_map(self):
        region = self.lr.getRegion()
        map_x1 = self.vb.mapToView(QtCore.QPointF(region[0], 0))
        map_x2 = self.vb.mapToView(QtCore.QPointF(region[1], 0))
        # print(map_x1,map_x2)
        x1 = find_nearest(self.x_time_s, map_x1.x())
        x2 = find_nearest(self.x_time_s, map_x2.x())

        return [x1, x2]

    def region_sta_inf_cal(self):
        """
        计算区域中的统计信息
        :return 统计信息对应的字符串信息
        """
        x1, x2 = self.region_to_list_index_map()

        delta_t = abs(self.x_time_s[x1] - self.x_time_s[x2])
        str_inf = '△T:%0.6f s\n' % delta_t

        for index in range(len(self.axis_name)):
            if self.wave_is_display[index]:
                y_data = self.y_data[self.axis_name[index]][x1:x2 + 1]
                y_max = np.max(y_data)
                y_min = np.min(y_data)
                y_mean = np.mean(y_data)
                y_std = np.std(y_data)
                str_inf += self.axis_name[index] + '-max:{:0.3f},min:{:0.3f},mean:{:0.3f},std:{:0.3f}'.format(y_max,
                                                                                                              y_min,
                                                                                                              y_mean,
                                                                                                              y_std)
            else:
                continue
            str_inf += '\n\n'

        return str_inf.rstrip('\n')

    def region_sta_inf_view(self):
        # 确保区域内有数据且区域标签已打开
        if self.x_time_s and self.menu_region.text() == MENU_REGION_TEXT[1]:
            sta_inf = self.region_sta_inf_cal()

            region = self.lr.getRegion()
            sys_y = self.plot.getViewBox().mapFromView(QtCore.QPointF(0, self.plot.viewRange()[1][1]))

            self.text.setPos(region[1], sys_y.y())
            self.text.setText(sta_inf)

    def menu_context_pause(self):
        if self.menu_pause.text() == MENU_PAUSE_TEXT[1]:
            self.menu_pause.setText(MENU_PAUSE_TEXT[0])
            self.wave_update_start()
        else:
            self.menu_pause.setText(MENU_PAUSE_TEXT[1])
            self.wave_update_stop()

    def menu_context_region(self):
        if self.menu_region.text() == MENU_REGION_TEXT[0]:
            self.menu_region.setText(MENU_REGION_TEXT[1])
            # 计算可视范围
            view_range_x = self.plot.viewRange()[0]
            x1 = (view_range_x[0] + view_range_x[1]) / 2 - 0.5
            x2 = (view_range_x[0] + view_range_x[1]) / 2 + 0.5
            # 将视图中的坐标转换为系统坐标
            sys_x1 = self.vb.mapFromView(QtCore.QPointF(x1, 0))
            sys_x2 = self.vb.mapFromView(QtCore.QPointF(x2, 0))
            # lr = pg.LinearRegionItem()
            self.lr.setParentItem(self.plot.getViewBox())
            self.lr.setRegion([sys_x1, sys_x2])
            # 创建文本标签并定位到区域的右侧
            # text = pg.TextItem("sta", anchor=(0, 0), angle=0, border='w', fill=(0, 0, 255, 100))
            self.text.setParentItem(self.plot.getViewBox())
            view_range_y = self.plot.viewRange()[1]
            sys_y = self.vb.mapFromView(QtCore.QPointF(0, view_range_y[1]))
            self.text.setPos(sys_x2.x(), sys_y.y())
        else:
            self.menu_region.setText(MENU_REGION_TEXT[0])
            self.vb.removeItem(self.lr)
            self.vb.removeItem(self.text)

    def go_back_wave_front(self):
        if self.curve_move_pause:
            self.curve_max_point = len(self.x_time_s)
            self.curve_move_pause = False


def wave_data(data):
    if wave_pause_flag.value:
        # args[0] = {'x': x,'y':y,'z':z}
        wave_data_q.put(data)


def wave_cmd(cmd):
    wave_cmd_q.put(cmd)


def wave_init():
    global wave_data_q, wave_run_flag, wave_pause_flag, wave_cmd_q

    # Value、Array都是线程安全的,参考https://docs.python.org/zh-cn/3/library/multiprocessing.html
    wave_pause_flag = Value('i')
    wave_run_flag = Value('i')
    wave_data_q = Queue()
    wave_cmd_q = Queue()

    wave_run_flag.value = 0
    wave_pause_flag.value = 0


def wave_update():
    wave_obj.wave_update()


# wave_config = {'y_range' : [], 'y_text' : '','axis_name': ['','','']}
def wave_run(run_flag, pause_flag, data_q, cmd_q, cfg):
    global wave_obj

    run_flag.value = 1

    win = pg.GraphicsLayoutWidget(show=True)
    win.resize(1000, 700)
    win.setWindowTitle('实时波形图')
    win.addLabel("<b>实时波形图</b>")
    label_xy = pg.LabelItem(justify='right')
    label_odr = pg.LabelItem(justify='right')
    win.nextRow()
    win.addItem(label_xy)
    win.nextRow()
    win.addItem(label_odr)
    win.nextRow()

    pg.setConfigOptions(antialias=True)

    plot = win.addPlot()

    pen_color = [(255, 0, 0),           # 红
                 (0, 255, 0),           # 绿
                 (0, 0, 255),           # 蓝
                 (128, 0, 128),         # 紫
                 (255, 255, 0),         # 黄
                 (255, 255, 255),       # 白
                 ]
    wave_obj = waveform(pause_flag, data_q, cmd_q, plot, pen_color, cfg['axis_name'], cfg['y_range'],
                        y_text=cfg['y_text'], y_unit='', label_xy=label_xy, label_odr=label_odr)

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(wave_obj.wave_update)
    timer.start(10)
    # 窗体关闭自动退出进程
    pg.exec()

    pause_flag.value = 0
    run_flag.value = 0
    wave_queue_clr(data_q)


def startup_wave(y_range, y_text, axis_name):
    if wave_run_flag.value == 0:
        wave_run_flag.value = 1

        wave_config = {'y_range': y_range, 'y_text': y_text, 'axis_name': axis_name}
        wave_pro = Process(target=wave_run, args=(wave_run_flag, wave_pause_flag, wave_data_q, wave_cmd_q, wave_config),
                           daemon=True)
        wave_pro.start()

        return True
    else:
        return False


if __name__ == '__main__':
    pass
