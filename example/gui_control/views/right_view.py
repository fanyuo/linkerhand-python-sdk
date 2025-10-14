import sys, os, time, random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QPushButton,
    QWidget, QGridLayout, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor

current_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.abspath(os.path.join(current_dir, "../../.."))
sys.path.append(target_dir)
from LinkerHand.utils.load_write_yaml import LoadWriteYaml


class RightView(QMainWindow):
    add_button_handle = pyqtSignal(str)
    handle_button_click = pyqtSignal(str)

    def __init__(self, hand_joint="L20", hand_type="left"):
        super().__init__()
        self.hand_joint = hand_joint
        self.hand_type = hand_type
        self.buttons = []
        self.yaml = LoadWriteYaml()
        self.all_action = self.yaml.load_action_yaml(hand_type=self.hand_type, hand_joint=self.hand_joint)

        # 新增状态变量
        self.sequential_play_active = False
        self.random_play_active = False
        self.sequential_timer = None
        self.random_timer = None

        self.setWindowTitle("按钮网格布局")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()
        self.init_buttons()

    def init_ui(self):
        # 主窗口容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # 输入框和按钮容器
        self.button_container = QWidget()
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_layout.setSpacing(10)

        # 输入框
        self.input_field = QLineEdit()
        self.button_layout.addWidget(self.input_field)

        # 添加按钮
        self.add_button = QPushButton("添加")
        self.add_button.setFixedSize(150, 30)
        self.add_button.clicked.connect(self.add_button_to_list)
        self.button_layout.addWidget(self.add_button)

        # 猜拳按钮
        self.rps_button = QPushButton("猜拳")
        self.rps_button.setFixedSize(150, 30)
        self.button_layout.addWidget(self.rps_button)

        # 随机动作按钮
        self.rdm_button = QPushButton("随机动作")
        self.rdm_button.setFixedSize(150, 30)
        self.button_layout.addWidget(self.rdm_button)

        # 全动作顺序遍历按钮（带状态显示）
        self.sequential_display_button = QPushButton("顺序执行 (关闭)")
        self.sequential_display_button.setFixedSize(150, 30)
        self.sequential_display_button.setStyleSheet(self._get_toggle_button_style(False))
        # self.sequential_display_button.clicked.connect(self.toggle_sequential_play)
        self.button_layout.addWidget(self.sequential_display_button)

        # 循环随机动作按钮（带状态显示）
        self.rdm_display_button = QPushButton("随机循环 (关闭)")
        self.rdm_display_button.setFixedSize(150, 30)
        self.rdm_display_button.setStyleSheet(self._get_toggle_button_style(False))
        # self.rdm_display_button.clicked.connect(self.toggle_random_play)
        self.button_layout.addWidget(self.rdm_display_button)

        # 将按钮容器添加到主布局
        self.main_layout.addWidget(self.button_container)

        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_area.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll_area)

        # 网格布局参数
        self.row = 0
        self.column = 0
        self.BUTTONS_PER_ROW = 2

    def _get_toggle_button_style(self, is_active):
        """获取切换按钮样式"""
        if is_active:
            return """
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: 1px solid #388E3C;
                    border-radius: 4px;
                    padding: 5px;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: 1px solid #D32F2F;
                    border-radius: 4px;
                    padding: 5px;
                }
            """

    def toggle_sequential_play(self):
        """切换顺序执行状态"""
        self.sequential_play_active = not self.sequential_play_active
        state = "开启" if self.sequential_play_active else "关闭"
        self.sequential_display_button.setText(f"顺序执行 ({state})")
        self.sequential_display_button.setStyleSheet(
            self._get_toggle_button_style(self.sequential_play_active)
        )

        if self.sequential_play_active:
            self._start_sequential_play()
        else:
            self._stop_sequential_play()


    def _start_random_play(self):
        """开始随机执行"""
        self.random_timer = QTimer()
        self.random_timer.timeout.connect(self._execute_random_action)
        self.random_timer.start(1500)  # 1.5秒间隔

    def _stop_random_play(self):
        """停止随机执行"""
        if hasattr(self, 'random_timer'):
            self.random_timer.stop()
            del self.random_timer

    def _execute_random_action(self):
        """执行随机动作"""
        valid_actions = [
            a for a in self.all_action
            if a['ACTION_NAME'] != "过渡状态"
        ]
        if valid_actions:
            action = random.choice(valid_actions)
            self.handle_button_click.emit(action['ACTION_NAME'])

    def init_buttons(self):
        if not self.all_action:
            return

        for item in self.all_action:
            button = QPushButton(item["ACTION_NAME"])
            button.setFixedSize(100, 30)
            button.clicked.connect(
                lambda checked, text=item["ACTION_NAME"]: self.handle_button_click.emit(text)
            )
            self.scroll_layout.addWidget(button, self.row, self.column,
                                         alignment=Qt.AlignLeft | Qt.AlignTop)

            self.column += 1
            if self.column >= self.BUTTONS_PER_ROW:
                self.column = 0
                self.row += 1

    def add_button_to_list(self):
        text = self.input_field.text().strip()
        if text:
            button = QPushButton(text)
            button.setFixedSize(100, 30)
            button.clicked.connect(
                lambda checked, t=text: self.handle_button_click.emit(t)
            )
            self.scroll_layout.addWidget(button, self.row, self.column,
                                         alignment=Qt.AlignLeft | Qt.AlignTop)

            self.column += 1
            if self.column >= self.BUTTONS_PER_ROW:
                self.column = 0
                self.row += 1

            self.input_field.clear()
            self.buttons.append(button)
            self.add_button_handle.emit(text)

    def clear_scroll_layout(self):
        """清空滚动布局"""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def closeEvent(self, event):
        """关闭窗口时清理资源"""
        self._stop_sequential_play()
        self._stop_random_play()
        event.accept()