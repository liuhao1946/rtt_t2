
## 简介

RTT_T2是一个免费、易用的多功能调试工具，它将很好的替代我之前做的[RTT-T](https://gitee.com/bds123/RTT-T)。它具有如下特点：

* 可选RTT通信，部分性能优于J_Link RTT Viewer。

* 可选串口通信，方便不使用RTT的工程师适用。

* 绘制具有良好交互性的动态波形图，最多支持同时绘制3条曲线。

* 支持log字符串过滤，方便你过滤掉你不感兴趣的字符串。

* 支持MCU端发送的**中文字符**。

* 支持以多种颜色显示log。

* 支持多行发送，方便发送各种字符串以及十六进制数据。

* 数据显示区内的数据不会自动清除。

* 数据显示区支持暂停在当前页面但不影响后续数据接收。

* 一键保存数据显示区的全部数据。

* 鼠标点击软件数据显示区，鼠标右键一键清除数据区域的log。

* 鼠标点击软件数据显示区，鼠标右键一键将数据区滚动条拉到最低端。

![软件演示](https://gitee.com/bds123/bds_tool/raw/master/images/1.gif)
![波形显示器演示](https://gitee.com/bds123/bds_tool/raw/master/images/2.gif)

对于源码感兴趣的朋友需要看一下[源码说明文档](https://gitee.com/bds123/bds_tool/blob/master/docs/source_code.md)。

---
## 使用指南
#### RTT(J_Link)通信

1. 点击主界面**配置**按钮。

2. 选择你的MCU、J_Link通信速度。

3. 根据需要勾选连接MCU时是否复位MCU。

4. 点击保存按钮，退出配置界面。

5. 在主界面上点击**J_Link连接**按钮。

> Note:
> 1. 使用RTT时，需要安装官方的[J_Link](https://www.segger.com/downloads/jlink/)组件。否则会因为RTT_T2无法调用J_Link的静态库而无法使用。
> 2. 对于工具不支持的芯片型号，参考[添加芯片](使用J_Link时，如何添加RTT_T2不支持的芯片型号？)
> 3. **RTT目前只支持0通道，不支持其他通道**。这意味着你只能调用SEGGER_RTT_printf(0, "test\n")发送数据，而不能调用SEGGER_RTT_printf(1,"test\n")去发送数据。

#### 串口通信

1. 点击主界面的**配置**按钮。

2. 选择COM口、波特率。

3. 点击保存按钮，退出配置界面。

4. 在主界面上点击**串口连接**按钮。

> Note: 
> 1. 目前只支持接收**字符格式**数据。
> 2. 如果要发送十六进制数据，请在MCU端将HEX数据转换为字符串后再发送到工具。

#### 显示中文字体
1. 将你的编辑器（keil、vs、IAR等）编码格式设置为**UTF-8**格式。

2. 点击主界面的**配置**按钮。

3. 在编码格式的栏位中，选中utf-8。此时，工具将使用uft-8解码从MCU发送的中文字符。

> Note:
>1. 工具默认选择的编码格式是**asc**，这也是我推荐的格式。因为工具使用该格式时，处理效率更高。
>2. 如果对中文字符显示有需求，你的数据不要**一直**以超过100Hz(10ms)的频率发送log数据。否则会造成工具无法显示或者及时显示你发过来的log，以**asc**格式发送则没有限制。

#### 发送带有颜色的字体
发送的数据在rtt_t中显示什么颜色由MCU端决定，以RTT为例，串口类似：
```c
#define BDS_COLOR_TAG           "BDSCOL"

#define BDS_LOG_COLOR_BLACK     0x000000 //黑色
#define BDS_LOG_COLOR_RED       0xFF3030 //共色
#define BDS_LOG_COLOR_GREEN     0x008B00 //绿色
#define BDS_LOG_COLOR_BLUE      0x00008B //蓝色
#define BDS_LOG_COLOR_VIOLET    0x9932CC //紫色

char *s = "test\n";

//红色
SEGGER_RTT_printf(0, BDS_COLOR_TAG "(%d)%s", BDS_LOG_COLOR_RED, s);
//绿色
SEGGER_RTT_printf(0, BDS_COLOR_TAG "(%d)%s", BDS_LOG_COLOR_GREEN, s);
//黑色
SEGGER_RTT_printf(0, BDS_COLOR_TAG "(%d)%s", BDS_LOG_COLOR_BLACK, s);
//黑色。不带BDS_COLOR_TAG标签时，rtt_t按照默认按照黑色显示
SEGGER_RTT_printf(0,"%s", s);
//蓝色
SEGGER_RTT_printf(0, BDS_COLOR_TAG "(%d)%s", BDS_LOG_COLOR_BLUE, s);
//紫色
SEGGER_RTT_printf(0, BDS_COLOR_TAG "(%d)%s", BDS_LOG_COLOR_VIOLET, s);
```

要注意的是，同一行的log显示的是同一个颜色，不同行中如果采用了不同的RGB色，在rtt_t中显示的颜色是不一样的。另外，由于采用的是RGB色，你可以将你的log以**任何颜色**显示在rtt_t中，而不仅仅限于例子中的几个颜色。

能被rtt_t识别的颜色标签格式必须是: **BDS_COLOR_TAG(xxx)zzz\n**，xxx为颜色值，zzz为你自己的字符串。

#### 配置过滤项
1. 打开主界面上的**过滤设置**选项。

2. 输入你需要过滤的字符串。
    如果只需要过滤一个字符串，比如TAG=DLOG，你的过滤表达式只需要这么写：
    > TAG=DLOG

    如果需要**过滤多个不同的字符串**，不同的**字符串间需要用&&隔开**。比如你需要过滤包含TAG=DLOG以及TAG=BDS的行，你的过滤表达式应该这么写:
    > TAG=DLOG&&TAG=BDS

    此时，rtt_t将过滤掉所有包含TAG=DLOG以及TAG=BDS的行。

> Note:
    对于你设置的需要过滤的字符串，其字符串长度应该≥3，否则可能产生误过滤，这一点是显而易见的。


#### 波形显示
波形显示可以用来研究数据的变化，帮助工程师寻找数据的规律以设计自己的算法。要利用这个功能，除了rtt_t提供的波形显示器以外，还需要MCU端配合。

##### 波形显示器

* 可配置y轴的默认范围，y轴的轴名称，以及3条曲线的名称。
    > 打开配置对话框，按照需要设置波形的默认参数。
    这里要注意以下**曲线名称**的设置问题。如果你只需要绘制**一条曲线**，只需要设置一条曲线的名称，假设这条曲线的名称为'X'，那么你只需要在曲线名称中填写：**X**。如果有**两条曲线**，假设名称分别为'X'、'Y'。此时你需要在曲线名称中填写：**X&&Y**，**不同的曲线名称之间用&&隔开**。如果有**三条曲线**，假设名称分别为'X'、'Y'、'Z'，此时你需要在曲线名称中填写：**X&&Y&&Z**。

* 使用鼠标滚轮控制y轴的尺度，方便观察细节以及动态调整y轴范围。

* 存在多条曲线时，可以隐藏不需要观察的波形。
    > 鼠标右键 → 隐藏波形 

* 可选的x轴(时间轴)可视范围，默认10s。以方便观察波形细节。
    > 鼠标右键 → x轴可视范围 

* 打开统计功能，它将统计你标记的区域内的几条曲线的统计参数。包括最大值、最小值、平均值、标准差。
    > 鼠标右键 → 打开统计区域

* 暂停实时波形，以观察当前波形特征。
    > 鼠标右键 → 暂停

* 拖拽实时波形，观察历史数据的同时不影响实时接收的数据。注意的是，波形只支持6分钟的数据回溯，这样设计是为了节省内存，不过，如果有需求，这一点可以在后续的软件版本中修改。
    > 点击鼠标左键不放，向左或者向右拖拽波形

* 导出x轴(时间轴)可视范围内的全部数据。
    > Export... → 导出格式选择CSV → Export

* 一键回到波形最前端。该功能方便历史波形数据回溯时快速的跟踪当前波形的最新状态。
    > 鼠标右键 → 回到波形最前端

##### MCU向波形显示器发送数据
要想波形显示器能正常工作，MCU端向rtt_t发送log时需要满足一定的数据格式。标准的数据格式如下：
> TAG=DLOG M*P(x,y,z)\n

上述的字符串中，TAG=DLOG表示log标签，M是关键字，这是不可改的。x、y、z是原始数据转换为整形的结果，P指示了原始数据后的小数点位数。假设原始数据为X、Y、Z，则x、y、z与X、Y、Z以及P的关系如下：


* X、Y、Z为**整数**，P=0。x=X，y=Y，z=Z，此时x、y、z表示整型数。
    ```c
    static uint32_t sn = 0;
    int32_t X=-100,Y=105,Z=20;
    int32_t x,y,z;

    x = X;
    y = Y;
    z = Z;
    SEGGER_RTT_printf(0,  BDS_COLOR_TAG"(%d)TAG=DLOG SN(%d)M*%d(%d,%d,%d)\n", BDS_LOG_COLOR_RED, sn++, 0, x, y, z);

    //格式化后的字符串
    "BDSCOL(16724016)TAG=DLOG SN(0)M*0(x,y,z)\n"
    ```

* X、Y、Z为**浮点数**，P!=0。x=X * 10^P， y=Y * 10^P， z=Z * 10^P。
    ```c
    static uint32_t sn = 0;
    float X=0.123,Y=5.638941,Z=9.8874;
    int32_t x,y,z;

    x = X * 10;
    y = Y * 10;
    z = Z * 10;
    //保留1位小数点
    SEGGER_RTT_printf(0,  BDS_COLOR_TAG"(%d)TAG=DLOG SN(%d)M*%d(%d,%d,%d)\n", BDS_LOG_COLOR_RED, sn++, 1, x, y, z);
    //格式化后的字符串:"BDSCOL(16724016)TAG=DLOG SN(0)M*1(x,y,z)\n"

    x = X * 100;
    y = Y * 100;
    z = Z * 100;
    //保留2位小数点，其他位数的小数点类似
    SEGGER_RTT_printf(0,  BDS_COLOR_TAG"(%d)TAG=DLOG SN(%d)M*%d(%d,%d,%d)\n", BDS_LOG_COLOR_RED, sn++, 2, x, y, z);
    //格式化后的字符串:"BDSCOL(16724016)TAG=DLOG SN(0)M*2(x,y,z)\n"
    ```

> Note:
> 1. 这里的X、Y、Z与**软件配置对话框**内的X、Y、Z轴名称是对应的。
> 2. 这里将浮点数统一为整数的一个原因有几点，首先是因为SEGGER_RTT_printf()接口不支持浮点数；其次，对于浮点数的格式化效率不如整数。

**上述显示三条曲线，如果你不需要显示这么多曲线，请特别注意下面的描述：**
如果你只有**一条波形**需要显示，也需要填充完整的(X,Y,Z)：
  > TAG=DLOG M*P(X,0,0)\n
  
如果你只有**二条波形**需要显示：
  > TAG=DLOG M*P(X,Y,0)\n


---

## FAQ
#### 使用J_Link时，如何添加RTT-T2不支持的芯片型号？
1. 在J_Link的官方软件中找到你的目标芯片名称。
![](https://gitee.com/bds123/bds_tool/raw/master/images/6.jpg)

2. 将芯片名称添加到**应用程序**所在目录下的**config.json**文件。
![](https://gitee.com/bds123/bds_tool/raw/master/images/4.jpg)

![](https://gitee.com/bds123/bds_tool/raw/master/images/5.jpg)

也可参考[RTT-T](https://gitee.com/bds123/RTT-T)仓库的**RTT-T配置**部分，这里有更详细的描述。

#### 如果你选择的芯片不能被RTT-T2识别怎么办？
有时候你已经正确的获得了你的芯片在J_Link中的命名，但当你尝试使用RTT-T2去连接芯片时要么不成功，要么无法进行RTT通信，这个时候你可以将芯片选择为**nRF52840xxAA**后在尝试。

#### 如何更高效的利用保存全部保存功能？
由于点击**保存全部数据**按钮完成了两件事，一件将RTT-T2的数据区内的log全部保存到txt文本。另一件是打开这个txt文本。所以如果你将**txt文本的默认打开程序设置为notepad或者vs**，你可以在一个非常强大的编辑器中搜索、编辑log。这也是为什么RTT-T2没有做log检索功能的一个原因。

---

## 写在最后
本项目是免费使用的，之所以这么做是因为我个人受益于开源，因此对于开源事业做一点微薄贡献一直是我很想做的事情之一。对我而言，可能更重要的想在这个世界留下一点痕迹，当有人受益于此，我便十分欣慰。假如你想表达感谢，请点个Star，你的Star也是我前进的动力。



