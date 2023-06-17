## 源码的说明

这篇文档主要是对源码感兴趣的工程师做的简要说明。这里主要介绍一下我自己的开发环境以及使用的代码库版本、代码库修改的地方。

## 编译器
* 编译器 - PyCharm 

## 几个关键软件库
* PySimpleGUI，GUI模块，版本4.53.0。

* pylink，jlink模块，版本1.1.0。

* pyserial，串口模块，p版本3.5。

* pyqtgraph，绘图模块，版本0.12.4。

## 软件库中的修改

RTT-T2修改了2个模块，一个是PySimpleGUI，一个是pyqtgraph。

#### PySimpleGUI中的修改

在PysimpleGUI.py中增加如下代码，以获得多行控件滑动条的坐标：

```python
    def get_vscroll_position(self):
        """
        Get the relative position of the scrollbar

        :return: (y1,y2)
        :rtype: tuple
        """
        try:
            return self.Widget.yview()
        except Exception as e:
            print('Warning get the vertical scroll (yview failed)')
            print(e)
            return None
```

该行代码增加到模块中已有的set_vscroll_position()函数后面即可。

#### pyqtgraph中的修改
在pyqtgraph中新增了两个捕获鼠标按下与松开的事件通知，以计算鼠标移动距离，进而移动适当的波形数据点。需要在GraphicsScene.py中新增如下代码：

1. 定义鼠标按下，松开实例。

```python
    # 已有的
    sigMouseHover = QtCore.Signal(object)   ## emits a list of objects hovered over
    sigMouseMoved = QtCore.Signal(object)   ## emits position of mouse on every move
    sigMouseClicked = QtCore.Signal(object)   ## emitted when mouse is clicked. Check for event.isAccepted() to see whether the event has already been acted on.
    #新增的
    sigMousePress = QtCore.Signal(object)
    sigMouseRelease = QtCore.Signal(object)
```

2. 新增事件通知函数。

```python
def mousePressEvent(self, ev):
    # 已有的
    super().mousePressEvent(ev)
    # 新增的
    self.sigMousePress.emit(ev)
    .......

def mouseReleaseEvent(self, ev):
    # 新增的
    self.sigMouseRelease.emit(ev)
    # 已有的
            if self.mouseGrabberItem() is None:
            if ev.button() in self.dragButtons:
                if self.sendDragEvent(ev, final=True):
                    #print "sent drag event"
                    ev.accept()
                self.dragButtons.remove(ev.button())
    .......
```