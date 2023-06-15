<!--
 * @Author: liuhao1946 2401569420@qq.com
 * @Date: 2023-06-15 22:18:35
 * @LastEditors: liuhao1946 2401569420@qq.com
 * @LastEditTime: 2023-06-16 00:48:39
 * @FilePath: \undefinedc:\Users\LH\Desktop\bds_tool\README.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->

# 简介

bds_tool是一个免费、易用的多功能调试工具，它将很好的替代我之前做的[RTT-T](https://gitee.com/bds123/RTT-T)。它具有如下特点：

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

---
## 使用指南
#### 软件的界面构成
主界面

配置界面

#### RTT(J_Link)通信

1. 点击主界面**配置**按钮。

2. 选择你的MCU、J_Link通信速度。

3. 根据需要勾选连接MCU时是否复位MCU。

4. 点击保存按钮，退出配置界面。

5. 在主界面上点击**J_Link连接**按钮。

> Note:
> 1. 使用RTT时，需要安装官方的[J_Link](https://www.segger.com/downloads/jlink/)组件。否则会因为bds_tool无法调用J_Link的静态库而无法使用。
> 2. 对于工具不支持的芯片型号，参考[添加芯片](使用J_Link时，如何添加bds_tool不支持的芯片型号？)
> 3. **RTT目前只支持0通道，不支持其他通道**。这意味着你只能调用SEGGER_RTT_printf(0, "test\n")发送数据，而不能调用SEGGER_RTT_printf(1,"test\n")去发送数据。

#### 串口通信

1. 点击主界面的**配置**按钮。

2. 选择COM口、波特率。

3. 点击保存按钮，退出配置界面。

4. 在主界面上点击**J_Link连接**按钮。

#### 显示中文字体
1. 将你的编辑器（keil、vs、IAR等）编码格式设置为**UTF-8**格式。

2. 点击主界面的**配置**按钮。

3. 在编码格式的栏位中，选中utf-8。此时，工具将使用uft-8解码从MCU发送的中文字符。

> Note:
    1. 工具默认选择的编码格式是**asc**，这也是我推荐的格式。因为工具使用该格式时，处理效率更高。
    2. 如果对中文字符显示有需求，你的数据不要**一直**以超过100Hz(10ms)的频率发送log数据。否则会造成工具无法显示或者及时显示你发过来的log，以**asc**格式发送则没有限制。

#### 发送带有颜色的字体

#### 配置过滤项目

#### 波形显示

---

## FAQ
#### 使用J_Link时，如何添加bds_tool不支持的芯片型号？

#### 如果你选择的芯片不能被软件识别？

#### 如何更高效的利用一键保存功能？

---

## 写在最后
本项目是免费使用的，之所以这么做是因为我个人受益于开源，因此对于开源事业做一点微薄贡献一直是我很想做的事情之一。对我而言，可能更重要的想在这个世界留下一点痕迹，当有人受益于此，我便十分欣慰。假如你想表达感谢，请点个Star，你的Star就是我前进的最大动力。



