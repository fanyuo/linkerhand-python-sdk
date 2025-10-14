from PyQt5.QtWidgets import (QMainWindow, QSplitter, QApplication, QMessageBox,
                             QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
                             QScrollArea, QGridLayout, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, QCoreApplication
import yaml, os, sys, time, json, random
from views.left_view import LeftView
from views.right_view import RightView
from views.wave_form_plot import WaveformPlot

current_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.abspath(os.path.join(current_dir, "../.."))
sys.path.append(target_dir)
from LinkerHand.linker_hand_api import LinkerHandApi
from LinkerHand.utils.load_write_yaml import LoadWriteYaml
from LinkerHand.utils.color_msg import ColorMsg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_hand_joint()
        self.api = LinkerHandApi(hand_joint=self.hand_joint, hand_type=self.hand_type)
        self.touch_type = -1
        self._init_gui_view()

        if self.hand_joint == "L21":
            self.add_button_position = [255] * 25
            self.set_speed(speed=[60, 220, 220, 220, 220])
            self.touch_type = self.api.get_touch_type()

    def play_rock_paper_scissors(self):
        """执行猜拳动作
        随机选择石头、剪刀或布的动作并执行
        """
        choices = ["石头", "剪刀", "布"]
        selected_choice = random.choice(choices)

        # 显示选择结果
        # QMessageBox.information(self, "猜拳结果", f"我出的是: {selected_choice}")

        # 查找并执行对应的动作
        self.execute_action(selected_choice)

    def execute_action(self, target_action):
        """执行动作（使用Qt非阻塞延时）"""
        try:
            # 从YAML配置文件中加载所有动作
            all_action = self.yaml.load_action_yaml(hand_type=self.hand_type, hand_joint=self.hand_joint)
            if not all_action:
                QMessageBox.warning(self, "错误", "没有找到动作配置")
                return

            # 执行过渡状态
            transition_action = next(
                (a for a in all_action if a['ACTION_NAME'] == "过渡状态"),
                None
            )

            if transition_action:
                # 执行过渡动作
                self._execute_single_action(transition_action)

                # 使用QTimer实现非阻塞延时
                QTimer.singleShot(100, lambda: self._execute_target_action(target_action, all_action))
            else:
                # 如果没有过渡状态，直接执行目标动作
                self._execute_target_action(target_action, all_action)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"执行动作时出错: {str(e)}")

    def _execute_single_action(self, action):
        """执行单个动作"""
        try:
            position = action['POSITION']
            ColorMsg(msg=f"动作名称:{action['ACTION_NAME']}, 动作数值:{position}", color="green")
            self.api.finger_move(pose=position)
            self.left_view.set_slider_values(values=position)
        except Exception as e:
            raise Exception(f"执行动作失败: {str(e)}")

    def _execute_target_action(self, target_action, all_action):
        """执行目标动作"""
        try:
            target = next(
                (a for a in all_action if a['ACTION_NAME'] == target_action),
                None
            )

            if target:
                self._execute_single_action(target)
            else:
                QMessageBox.warning(self, "错误", f"没有找到'{target_action}'的动作配置")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"执行目标动作失败: {str(e)}")

    def _init_hand_joint(self):
        """初始化手部关节配置
        从YAML配置文件中加载手部关节信息
        """
        self.yaml = LoadWriteYaml()
        self.setting = self.yaml.load_setting_yaml()
        self.left_hand = False
        self.right_hand = False
        self.hand_exists = False  # 初始化hand_exists

        if self.setting['LINKER_HAND']['LEFT_HAND']['EXISTS']:
            self.left_hand = True

        if self.left_hand and self.right_hand:
            self.left_hand = True

        if self.left_hand:
            print("左手")
            self.hand_exists = True
            self.hand_joint = self.setting['LINKER_HAND']['LEFT_HAND']['JOINT']
            self.hand_type = "left"

        self.init_pos = [255] * 10
        self.joint_name = []  # 初始化joint_name

        if self.hand_joint == "L21":
            self.init_pos = [96, 255, 255, 255, 255, 150, 114, 151, 189, 255, 180, 255, 255, 255, 255, 255, 255, 255,
                             255, 255, 255, 255, 255, 255, 255]
            self.joint_name = ["拇指根部", "食指根部", "中指根部", "无名指根部", "小指根部", "拇指侧摆", "食指侧摆",
                               "中指侧摆", "无名指侧摆", "小指侧摆", "拇指横摆", "预留", "预留", "预留", "预留",
                               "拇指中部", "预留", "预留", "预留", "预留", "拇指指尖", "食指指尖", "中指指尖",
                               "无名指指尖", "小指指尖"]

    def _init_gui_view(self):
        """初始化主窗口界面
        创建分割视图，左侧为滑动条控制，右侧为动作记录
        """
        if self.hand_type == "left":
            self.setWindowTitle(f"Linker_Hand:左手- {self.hand_joint} Control - Qt5 with ROS")
        self.setGeometry(100, 100, 600, 800)

        # 创建分割线
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                width:1px;
                background-color: lightgray;
                margin: 15px 20px;
            }
        """)

        # 左侧滑动条界面
        self.left_view = LeftView(joint_name=self.joint_name, init_pos=self.init_pos)
        splitter.addWidget(self.left_view)
        self.left_view.slider_value_changed.connect(self.handle_slider_value_changed)

        # 右侧记录动作界面
        self.right_view = RightView(hand_joint=self.hand_joint, hand_type=self.hand_type)
        splitter.addWidget(self.right_view)

        # 安全连接信号
        self.right_view.handle_button_click.connect(self.handle_button_click)
        self.right_view.add_button_handle.connect(self.add_button_handle)
        self.right_view.rps_button.clicked.connect(self.play_rock_paper_scissors)
        self.right_view.rdm_button.clicked.connect(self.execute_random_action)
        # self.right_view.sequential_display_button.clicked.connect(self.execute_sequential_display)
        self.right_view.sequential_display_button.clicked.connect(self.toggle_sequential_play)
        self.right_view.rdm_display_button.clicked.connect(self.toggle_random_play)

        splitter.setSizes([600, 450])
        self.setCentralWidget(splitter)

    def handle_button_click(self, text):
        """处理按钮点击事件
        当点击动作按钮时，执行对应的手部动作
        """
        try:
            all_action = self.yaml.load_action_yaml(hand_type=self.hand_type, hand_joint=self.hand_joint)
            position = None  # 初始化position变量

            for index, pos in enumerate(all_action):
                if pos['ACTION_NAME'] == text:
                    position = pos['POSITION']
                    print(type(position))
                    break

            if position is None:
                QMessageBox.warning(self, "错误", f"未找到动作'{text}'的配置")
                return

            ColorMsg(msg=f"动作名称:{text}, 动作数值:{position}", color="green")
            self.api.finger_move(pose=position)
            self.left_view.set_slider_values(values=position)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理按钮点击时出错: {str(e)}")

    def add_button_handle(self, text):
        """处理添加按钮事件
        将当前滑动条位置保存为新的动作
        """
        try:
            self.add_button_position = self.left_view.get_slider_values()
            self.add_button_text = text
            self.yaml.write_to_yaml(action_name=text, action_pos=self.left_view.get_slider_values(),
                                    hand_joint=self.hand_joint, hand_type=self.hand_type)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存动作时出错: {str(e)}")

    def execute_random_action(self):
        """随机执行一个动作（排除过渡状态）"""
        try:
            # 加载所有动作配置
            all_actions = self.yaml.load_action_yaml(hand_type=self.hand_type, hand_joint=self.hand_joint)

            # 过滤掉过渡状态（确保至少有1个有效动作）
            valid_actions = [action for action in all_actions
                             if action['ACTION_NAME'] != "过渡状态"]

            if not valid_actions:
                QMessageBox.warning(self, "错误", "没有可用的动作配置")
                return

            # 随机选择一个有效动作
            selected_action = random.choice(valid_actions)

            # 执行选中的动作
            self.execute_action(selected_action['ACTION_NAME'])

        except Exception as e:
            QMessageBox.critical(self, "错误", f"随机执行动作时出错: {str(e)}")

    def toggle_sequential_play(self):
        """切换顺序执行状态"""
        self.right_view.sequential_play_active = not self.right_view.sequential_play_active
        state = "开启" if self.right_view.sequential_play_active else "关闭"
        self.right_view.sequential_display_button.setText(f"顺序执行 ({state})")
        self.right_view.sequential_display_button.setStyleSheet(
            self.right_view._get_toggle_button_style(self.right_view.sequential_play_active)
        )

        if self.right_view.sequential_play_active:
            self._start_sequential_play()
        else:
            self._stop_sequential_play()

    def _start_sequential_play(self):
        """非阻塞的顺序执行"""
        try:
            # 先停止可能存在的旧定时器
            if hasattr(self, 'sequential_timer'):
                self._stop_sequential_play()

            # 加载并过滤动作
            all_actions = self.yaml.load_action_yaml(hand_type=self.hand_type, hand_joint=self.hand_joint)
            self._sequential_actions = [a for a in all_actions if a['ACTION_NAME'] != "过渡状态"]

            if not self._sequential_actions:
                QMessageBox.warning(self, "警告", "没有可用的动作配置")
                return

            # 初始化索引
            self._current_seq_index = 0

            # 创建定时器
            self.sequential_timer = QTimer()
            self.sequential_timer.timeout.connect(self._execute_next_sequential)
            self.sequential_timer.start(3000)  # 1.5秒间隔

        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动顺序执行失败: {str(e)}")
            self._stop_sequential_play()

    def _execute_next_sequential(self):
        """执行下一个顺序动作"""
        try:
            if self._current_seq_index >= len(self._sequential_actions):
                self._current_seq_index = 0  # 循环执行

            action = self._sequential_actions[self._current_seq_index]
            self.execute_action(action['ACTION_NAME'])
            self._current_seq_index += 1

        except Exception as e:
            print(f"执行顺序动作出错: {str(e)}")
            self._stop_sequential_play()

    def _stop_sequential_play(self):
        """停止顺序执行"""
        if hasattr(self, 'sequential_timer') and self.sequential_timer:
            self.sequential_timer.stop()
            self.sequential_timer.deleteLater()
            del self.sequential_timer

    def toggle_random_play(self):
        """切换随机执行状态"""
        self.right_view.random_play_active = not self.right_view.random_play_active
        state = "开启" if self.right_view.random_play_active else "关闭"
        self.right_view.rdm_display_button.setText(f"随机循环 ({state})")
        self.right_view.rdm_display_button.setStyleSheet(
            self.right_view._get_toggle_button_style(self.right_view.random_play_active)
        )

        if self.right_view.random_play_active:
            self._start_random_play()
        else:
            self._stop_random_play()

    def _start_random_play(self):
        """非阻塞的随机执行"""
        try:
            # 先停止可能存在的旧定时器
            if hasattr(self, 'random_timer'):
                self._stop_random_play()

            # 创建定时器
            self.random_timer = QTimer()
            self.random_timer.timeout.connect(self._execute_random_action)
            self.random_timer.start(3000)  # 1.5秒间隔

        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动随机执行失败: {str(e)}")
            self._stop_random_play()

    def _execute_random_action(self):
        """执行随机动作"""
        try:
            all_actions = self.yaml.load_action_yaml(hand_type=self.hand_type, hand_joint=self.hand_joint)
            valid_actions = [a for a in all_actions if a['ACTION_NAME'] != "过渡状态"]

            if valid_actions:
                action = random.choice(valid_actions)
                self.execute_action(action['ACTION_NAME'])

        except Exception as e:
            print(f"执行随机动作出错: {str(e)}")
            self._stop_random_play()

    def _stop_random_play(self):
        """停止随机执行"""
        if hasattr(self, 'random_timer') and self.random_timer:
            self.random_timer.stop()
            self.random_timer.deleteLater()
            del self.random_timer

    def handle_slider_value_changed(self, slider_values):
        """处理滑动条值改变事件
        实时响应滑动条变化，控制手部动作
        """
        try:
            slider_values_list = []
            for key in slider_values:
                slider_values_list.append(slider_values[key])
            self.api.finger_move(pose=slider_values_list)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理滑动条变化时出错: {str(e)}")

    def update_label(self, index, value):
        """更新标签显示
        更新指定索引的关节位置显示
        """
        if 0 <= index < len(self.joint_name):
            self.left_view.labels[index].setText(f"{self.joint_name[index]}: {value}")

    def set_speed(self, speed=[180, 250, 250, 250, 250]):
        """设置手部动作速度
        Args:
            speed: 速度值列表
        """
        try:
            ColorMsg(msg=f"设置速度:{speed}", color="green")
            self.api.set_speed(speed)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"设置速度时出错: {str(e)}")

    def closeEvent(self, event):
        """关闭窗口事件处理
        关闭窗口时停止线程并释放资源
        """
        try:
            if hasattr(self, 'normal_force_plot'):
                self.normal_force_plot.close()
            if hasattr(self, 'approach_inc_plot'):
                self.approach_inc_plot.close()

            # 断开所有信号连接
            self.left_view.slider_value_changed.disconnect()
            if hasattr(self.right_view, 'handle_button_click'):
                self.right_view.handle_button_click.disconnect()
            if hasattr(self.right_view, 'add_button_handle'):
                self.right_view.add_button_handle.disconnect()
            if hasattr(self.right_view, 'rps_button'):
                self.right_view.rps_button.clicked.disconnect()

            self.close()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"关闭窗口时出错: {str(e)}")
        finally:
            event.accept()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"应用程序崩溃: {str(e)}")
        sys.exit(1)