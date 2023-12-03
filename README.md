
## 简介

RTT_T2是一个免费、易用的多功能调试工具，它将很好的替代我之前做的[RTT-T](https://gitee.com/bds123/RTT-T)。它具有如下特点：

* 可选RTT通信，部分性能优于J_Link RTT Viewer。

* 可选串口通信，方便不使用RTT的工程师适用。

* 串口接收支持3种格式，分别为utf-8、asc、hex，支持**中文显示**。

* J_Link接收支持2种格式，分别为utf-8、asc。支持**中文显示**。

* 绘制具有良好交互性的动态波形图，最多支持同时绘制3条曲线。

* 支持log字符串过滤，方便你过滤掉你不感兴趣的字符串。

* 支持以多种颜色显示log。

* 支持多行发送，方便发送各种字符串以及十六进制数据。

* 数据显示区内的数据不会自动清除。

* 数据显示区支持暂停在当前页面但不影响后续数据接收。

* 一键保存数据显示区的全部数据。

* 鼠标点击软件数据显示区，鼠标右键一键清除数据区域的log。

* 鼠标点击软件数据显示区，鼠标右键一键将数据区滚动条拉到最低端。

* **更多功能见文档.......**

对于源码感兴趣的朋友需要看一下[源码说明文档](https://gitee.com/bds123/bds_tool/blob/master/docs/source_code.md)。


软件**安装包**见仓库内的**发行版**部分，软件仅支持windows系统。

以下是两张软件演示的动图，第一次加载可能需要点时间（如果动图无法加载，可以直接去当前仓库目录下查看：images->1.gif以及2.gif ）。
![软件演示](https://gitee.com/bds123/bds_tool/raw/master/images/1.gif)
![波形显示器演示](https://gitee.com/bds123/bds_tool/raw/master/images/2.gif)

以下两张是软件的静态图片，这是为看不到动图的朋友准备的。
![](https://gitee.com/bds123/bds_tool/raw/master/images/7.jpg)
![](https://gitee.com/bds123/bds_tool/raw/master/images/8.jpg)


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
> 2. 对于工具不支持的芯片型号，参考**FAQ**。
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

#### 查找文本区字符串

该功能用于查找文本区域内你感兴趣的字符串，软件会**高亮**显示并**定位**目标字符串。

使用**快捷键<Ctrl+F>**，软件会弹出搜索框，在搜索框中输入要查找的字符串即可。

#### 发送带有颜色的字体
发送的数据在RTT_T2中显示什么颜色由MCU端决定，以RTT为例，串口类似：
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
//黑色。不带BDS_COLOR_TAG标签时，RTT_T2按照默认按照黑色显示
SEGGER_RTT_printf(0,"%s", s);
//蓝色
SEGGER_RTT_printf(0, BDS_COLOR_TAG "(%d)%s", BDS_LOG_COLOR_BLUE, s);
//紫色
SEGGER_RTT_printf(0, BDS_COLOR_TAG "(%d)%s", BDS_LOG_COLOR_VIOLET, s);
```

要注意的是，同一行的log显示的是同一个颜色，不同行中如果采用了不同的RGB色，在RTT_T2中显示的颜色是不一样的。另外，由于采用的是RGB色，你可以将你的log以**任何颜色**显示在RTT_T2中，而不仅仅限于例子中的几个颜色。

能被RTT_T2识别的颜色标签格式必须是: **BDS_COLOR_TAG(xxx)zzz\n**，xxx为颜色值，zzz为你自己的字符串。

对于发送带有颜色的字符，有一个简单的方法对**原始接口进行包装**，以**简化调用**，如下例子：
```c
//原始的打印蓝色字符的接口
SEGGER_RTT_printf(0, BDS_COLOR_TAG "(%d)%s", BDS_LOG_COLOR_BLUE, s);
//使用宏定义进行包装
#define rtt_print_blue(format, ...)   SEGGER_RTT_printf(0, BDS_COLOR_TAG"(%d)"format, BDS_LOG_COLOR_BLUE, ##__VA_ARGS__);   

//打印蓝色字符串
rtt_print_blue("%s\n", "test");

//原始的打印红色字符的接口
SEGGER_RTT_printf(0, BDS_COLOR_TAG "(%d)%s", BDS_LOG_COLOR_BLUE, s);
//使用宏定义进行包装
#define rtt_print_red(format, ...)   SEGGER_RTT_printf(0, BDS_COLOR_TAG"(%d)"format, BDS_LOG_COLOR_RED, ##__VA_ARGS__);  

//打印红色字符串
rtt_print_red("%s\n", "test");
```

#### 配置过滤项
rtt_t2的log过滤器是按照行过滤的。简单来说，就是过滤掉由用户指定的包含**指定字符串**的行，它的使用方法如下。

1. 打开主界面上的**过滤设置**选项。

2. 在文本输入框中输入你需要过滤的字符串。
    如果只需要过滤一个字符串，比如TAG=DLOG，你的过滤表达式只需要这么写：
    > TAG=DLOG

    如果需要**过滤多个不同的字符串**，不同的**字符串间需要用&&隔开**。比如你需要过滤包含TAG=DLOG以及TAG=BDS的行，你的过滤表达式应该这么写:
    > TAG=DLOG&&TAG=BDS

    此时，RTT_T2将过滤掉所有包含TAG=DLOG以及TAG=BDS的行。

3. **打开过滤器**复选框，过滤生效。

4. 勾选**取反过滤器**并打开过滤器，支持只保留你需要的行。比如你在文本输入框中的内容如下：
    > abc&&bcd123
    
    此时，过滤器会过滤掉**非abc**以及**非bcd123**的行。比如如果行内容为"hello bds abc\n"，该行内容不会被过滤。如果行内容为"hello bds\n"，那么该行将被过滤。当log显示错综复杂且log刷新很快的时，如果你此刻只想看到你想看的内容使用该功能将特别有用。

> Note:
    对于你设置的需要过滤的字符串，其字符串长度应该≥3，否则可能产生误过滤。


#### 搜索<_SEGGER_RTT>地址
rtt_t2默认是**自动搜索**(_SEGGER_RTT搜索**输入框空白**表示由rtt_t2自动搜索)你的SEGGER RTT代码中<_SEGGER_RTT>变量位于RAM中的地址，有时候因为一些情况导致自动搜索无效，此时需要手动设置<_SEGGER_RTT>的搜索起始地址以及搜索范围，这样rtt_t2可以在你设置的范围内找到<_SEGGER_RTT>地址。


关于如何设置起始地址以及搜索范围，参考[芯片能被识别但rtt_t2无法显示你发送过来的数据](#芯片能被识别但rtt_t2无法显示你发送过来的数据)

#### 发送数据到MCU

* 以ASC方式发送数据到MCU。如果需要发送的字符串后软件自动附带一个换行符，可以在**配置**选择需要的换行符类型。

* 以ASC发送数据时，允许在发送内容后**增加注释**，减少记忆负担。增加注释方法：
    > 命令字符串（注释）。比如abcd（这是一条测试指令），其中abcd为要发送的内容，括号内的内容为注释。软件在发送这个字符串时，会自动删除括号以及括号内的内容。
    

* **光标定位到数据发送框，使用键盘的'↑'/'↓'键可以像命令行一样翻看历史发送记录**。

* 以HEX方式发送数据到MCU。每个十六进制值之间以**空格**隔开，不足两位的十六进制**可以不补0**，十六进制也**不区分大小写**，以下的写法都是合法的。
    > 01 02 03 04 ad
    或者
    > 1 2 3 4 AD

#### 波形显示
波形显示可以用来研究数据的变化，帮助工程师寻找数据的规律以设计自己的算法。要利用这个功能，除了RTT_T2提供的波形显示器以外，还需要MCU端配合。

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
要想波形显示器能正常工作，MCU端向RTT_T2发送log时需要满足一定的数据格式。标准的数据格式如下：
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
> 1. 这里的X、Y、Z与**软件配置对话框**内的默认的曲线名称X、Y、Z是对应的。
> 2. 这里将浮点数统一为整数的一个原因有几点，首先是因为SEGGER_RTT_printf()接口不支持浮点数；其次，对于浮点数的格式化效率不如整数。

**上述显示三条曲线，如果你不需要显示这么多曲线，请特别注意下面的描述：**

不论你需要显示几个波形，都需要填充完整的(x,y,z)。如果你只有**一条波形**需要显示，log格式为：
  > TAG=DLOG M*P(x,0,0)\n
  
如果你只有**二条波形**需要显示，log格式为：
  > TAG=DLOG M*P(x,y,0)\n

---

## FAQ
#### 运行报错<TypeError: Expected to be given a valid DLL>
这个错误是因为rtt_t2依赖**JlinkArm.dll**，这个静态库来自官方J_Link软件包。因此，在使用rtt_t2前，你需要去J_Link的官网下载J_Link软件包[J_Link软件包](https://www.segger.com/downloads/jlink/)。

#### 使用J_Link时，如何添加RTT_T2不支持的芯片型号
1. 在J_Link的官方软件中找到你的目标芯片名称。
![](https://gitee.com/bds123/bds_tool/raw/master/images/6.jpg)

2. 将芯片名称添加到**应用程序**所在目录下的**config.json**文件。
![](https://gitee.com/bds123/bds_tool/raw/master/images/4.jpg)

![](https://gitee.com/bds123/bds_tool/raw/master/images/5.jpg)

也可参考[RTT-T](https://gitee.com/bds123/RTT-T)仓库的**RTT-T配置**部分，这里有更详细的描述。

实际上，由于ARM Cortex系列的兼容性，如果你的芯片不在J_Llink的官方软件中，你可以选择一颗具有**类似内核**比如nRF52840去连接你的目标设备，如果能通信上也是没问题的。另外，如果J_Link官方软件中没有你的MCU型号，你可能需要先去更新你的J_Link软件包，因为新的MCU可能会在J_Link新的软件包中。

#### 芯片能被识别但rtt_t2无法显示你发送过来的数据？
这种情况一般都是因为rtt_t2没有找到你的SEGGER RTT代码中<_SEGGER_RTT>变量地址，该地址定义在MCU的RAM中，具体位置可以看编译器生成的map文件。

打开rtt_t2的**配置**，设置_SEGGER_RTT的**起始地址**以及**地址范围**。输入地址以及地址范围要注意：
1. 起始地址必须**4字节对齐**。
2. 范围大小 ≥ 16字节。
3. 起始地址与范围大小间必须有一个空格。
4. 起始地址与范围大小是十六进制且必须以 "0x" 开头。

比如：
> 0x20000000 0x64

如果你不知道起始地址应该设置多少，有两个办法：
1. 查看map文件，看<_SEGGER_RTT>在map文件中的地址。
2. 参考芯片手册的**内存映射**部分的描述，你可以将起始地址设置为芯片的RAM起始地址，范围设置为整个RAM区域。

#### <保存全部数据>功能该怎么用？
点击**保存全部数据**按钮完成了两件事。一个是将RTT_T2的数据区内的log全部保存到txt文本，另一个是打开这个txt文本。所以如果你将**txt文本**的**默认打开程序**（通过windows系统）设置为**notepad**或者**其他你喜欢的编辑器**，你可以在一个非常强大的编辑器中搜索、编辑log。

#### J_Link的的数据传输速度可达多少？
![](https://gitee.com/bds123/bds_tool/raw/master/images/9.jpg)

从上图可见，RTT的传输速度可达1us传输82个字符，这速度还是相当可观的。

> 测试条件：STM32F407 Cortex-M4，时钟168M

还有一组RTT的传输速度曲线可供参考。
![](https://gitee.com/bds123/bds_tool/raw/master/images/10.png)

---

## 写在最后
本项目是免费使用的，之所以这么做是因为我个人受益于开源，因此对于开源事业做一点微薄贡献一直是我很想做的事情之一。对我而言，可能更重要的想在这个世界留下一点痕迹，当有人受益于此，我便十分欣慰。假如你想表达感谢，请点个Star，你的Star也是我前进的动力。



