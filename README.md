# LinkerHand-Python-SDK Fork 版本说明

## 我的补充说明

### 项目用途
本 Fork 主要用于本人学校的机械手展示与互动功能的实现，不保证能适用于其他情况。

### 主要修改
1. **默认配置调整**  
   - 修改 `hand_type` 和 `hand_joint` 默认参数。  
   - 默认使用 Windows 系统的 **PCAN_USBBUS1** 作为通信端口。  

2. **动作配置增强**  
   - 在 `./LinkerHand/Config/L21_positions.yaml` 增加多个新的动作及对应参数。

3. **GUI 功能拓展**  
   - 修改原项目 `./example/gui_control` 目录的代码内容。  
   - 新增程序功能：
     - **猜拳**
     - **随机动作**
     - **顺序执行**
     - **随机循环**
   - 添加 **Qt** 界面显示和按钮控制功能。

### 使用说明
1. 下载并安装驱动程序（Windows 用户）：  
   [Peak-System 驱动下载页面](https://peak-system.com.cn/driver/)  

2. 参考原项目的软件安装步骤完成安装后，运行以下代码：
    ```bash
   python ./example/gui_control/gui_control_add_display&interaction.py
    ```

### 注意事项
- 新增动作之间应加入 “过渡状态”，以防止关节运动冲突，减少机械损坏风险。

# 以下为原项目 README

## Overview
LinkerHand Python SDK

## Caution
- 请确保灵巧手未开启其他控制，如linker_hand_sdk_ros、动捕手套控制和其他控制灵巧手的topic。以免冲突。
- 请将固定灵巧手，以免灵巧手在运动时跌落。
- 请确保灵巧手电源与USB转CAN连接正确。

## Installation
&ensp;&ensp;您可以在安装requirements.txt后的情况下运行示例。仅支持 Python3。
- download

  ```bash
  # 开启CAN端口
  $ sudo /usr/sbin/ip link set can0 up type can bitrate 1000000 #USB转CAN设备蓝色灯常亮状态
  
  $ git clone https://github.com/linkerbotai/linker_hand_python_sdk.git
  ```

- install

  ```bash
  pip3 install -r requirements.txt
  ```

# CAN or RML485 协议切换
注：由于睿尔曼当前RM65的Python的485接口BUG问题，暂不支持
编辑config/setting.yaml配置文件，按照配置文件内注释说明进行参数修改。RML(睿尔曼API2) 通过睿尔曼机械臂进行485协议通讯控制LinkerHand
MODBUS: "None" or "RML"


## 相关文档
[Linker Hand API for Python Document](doc/API-Reference.md)

## 更新说明

- > ### release_2.1.9
 - 1、新增支持O6灵巧手

- > ### release_2.1.8
 - 1、修复偶发撞帧问题

- > ### 2.1.4
  - 1、新增支持L21
  - 2、新增支持矩阵式压力传感器
  - 3、支持L10 Mujoco仿真


- > ### 1.3.6
  - 支持LinkerHand L7/L20/L25版本灵巧手

- > ### 1.1.2
  - 支持LinkerHand L10版本灵巧手
  - 增加GUI控制L10灵巧手
  - 增加GUI显示L10灵巧手压感图形模式数据
  - 增加部分示例源码
  
- position与手指关节对照表

  L7:  ["大拇指弯曲", "大拇指横摆","食指弯曲", "中指弯曲", "无名指弯曲","小拇指弯曲","拇指旋转"]

  L10: ["拇指根部", "拇指侧摆","食指根部", "中指根部", "无名指根部","小指根部","食指侧摆","无名指侧摆","小指侧摆","拇指旋转"]

  L20: ["拇指根部", "食指根部", "中指根部", "无名指根部","小指根部","拇指侧摆","食指侧摆","中指侧摆","无名指侧摆","小指侧摆","拇指横摆","预留","预留","预留","预留","拇指尖部","食指末端","中指末端","无名指末端","小指末端"]

  L21: ["大拇指根部", "食指根部", "中指根部","无名指根部","小拇指根部","大拇指侧摆","食指侧摆","中指侧摆","无名指侧摆","小拇指侧摆","大拇指横滚","预留","预留","预留","预留","大拇指中部","预留","预留","预留","预留","大拇指指尖","食指指尖","中指指尖","无名指指尖","小拇指指尖"]

  L25: ["大拇指根部", "食指根部", "中指根部","无名指根部","小拇指根部","大拇指侧摆","食指侧摆","中指侧摆","无名指侧摆","小拇指侧摆","大拇指横滚","预留","预留","预留","预留","大拇指中部","食指中部","中指中部","无名指中部","小拇指中部","大拇指指尖","食指指尖","中指指尖","无名指指尖","小拇指指尖"]

## [L10_Example](example/L10)

&ensp;&ensp; __在运行之前, 请将 [setting.yaml](LinkerHand/config/setting.yaml) 的配置信息修改为您实际控制的灵巧手配置信息.__

- #### [0000-gui_control](example/gui_control/gui_control.py) 
- #### [0001-linker_hand_fast](example/L10/gesture/linker_hand_fast.py)
- #### [0002-linker_hand_finger_bend](example/L10/gesture/linker_hand_finger_bend.py)
- #### [0003-linker_hand_fist](example/L10/gesture/linker_hand_fist.py)
- #### [0004-linker_hand_open_palm](example/L10/gesture/linker_hand_open_palm.py)
- #### [0005-linker_hand_opposition](example/L10/gesture/linker_hand_opposition.py)
- #### [0006-linker_hand_sway](example/L10/gesture/linker_hand_sway.py)

- #### [0007-linker_hand_get_force](example/L10/get_status/get_force.py) #python3 get_force.py --hand_joint L10 --hand_type right
- #### [0008-linker_hand_get_speed](example/L10/get_status/get_set_speed.py) #python3 get_set_speed.py --hand_joint L10 --hand_type right --speed 100 123 211 121 222   注:L7 speed参数为7个，其他为5个
- #### [0009-linker_hand_get_state](example/L10/get_status/get_set_state.py) # python3 get_set_state.py --hand_joint L10 --hand_type right --position 100 123 211 121 222 255 255 255 255 255  position参数个数请参照position与手指关节对照表

- #### [0010-linker_hand_dynamic_grasping](example/L10/grab/dynamic_grasping.py)




## API 说明文档
[Linker Hand API for Python Document](doc/API-Reference.md)




