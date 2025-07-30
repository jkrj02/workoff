import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QTimeEdit, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint
from PyQt5.QtGui import QPalette, QColor, QCursor, QPainter, QBrush
from qt_material import apply_stylesheet
import subprocess
import os
import sys

# if getattr(sys, 'frozen', False):  
#     # exe 运行时
#     current_dir = os.path.dirname(sys.executable)
# else:  
#     # 普通 Python 脚本运行时
#     current_dir = os.path.dirname(os.path.abspath(__file__))

# # 找到 JAR 路径
# jar_path = os.path.join(current_dir, "backend-1.0-SNAPSHOT.jar")

API_BASE = "http://localhost:8080/api"

def info(msg):
    print(f"[INFO] {msg}")

class TimerWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        info("TimerWindow 初始化")
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(300, 120)
        self.move_to_bottom_right()
        
        # 添加拖拽移动功能
        self.dragging = False
        self.offset = QPoint()
        
        # 背景透明度状态
        self.background_opacity = 0.0

        self.label = QLabel("00小时00分钟")
        self.label.setStyleSheet("color: rgb(42,157,143); font-size: 22px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignCenter)  # 文字居中
        self.progress = QProgressBar()
        self.progress.setFixedHeight(16)
        # self.progress.setStyleSheet("""
        #     QProgressBar {background: rgba(255,255,255,0.2); border: 2px solid rgba(255, 255, 255, 0.6); border-radius: 8px;}
        #     QProgressBar::chunk {background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4caf50, stop:1 #81c784);border-radius: 8px;}
        # """
        # )
        self.close_btn = QPushButton("←")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self.close_timer)
        self.close_btn.hide()  # 初始隐藏
        # 将关闭按钮设置为子窗口，并定位到右上角
        self.close_btn.setParent(self)
        self.close_btn.move(270, 10)  # 右上角位置，适应新的窗口宽度300px

        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addSpacing(20)  # 增加文字和进度条之间的间距
        vbox.addWidget(self.progress)
        vbox.addStretch()
        vbox.setContentsMargins(24, 24, 24, 8)  # 减少底部边距，让内容更靠近底部
        
        self.setLayout(vbox)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圆角矩形背景
        brush = QBrush(QColor(255, 255, 255, int(255 * self.background_opacity)))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def move_to_bottom_right(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 320, screen.height() - 160)  # 调整位置适应新宽度
        info(f"TimerWindow 移动到右下角: ({self.x()}, {self.y()})")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
            info(f"开始拖拽窗口，鼠标位置: {event.pos()}")

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            new_pos = self.mapToParent(event.pos() - self.offset)
            self.move(new_pos)
            # info(f"拖拽窗口到新位置: ({self.x()}, {self.y()})")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            info(f"结束拖拽窗口，最终位置: ({self.x()}, {self.y()})")

    def enterEvent(self, event):
        self.background_opacity = 0.2  # 鼠标进入时半透明背景
        self.close_btn.show()
        self.update()  # 重绘窗口
        info("鼠标进入倒计时窗口，显示返回按钮，背景变为半透明")

    def leaveEvent(self, event):
        self.background_opacity = 0.0  # 鼠标离开时完全透明背景
        self.close_btn.hide()
        self.update()  # 重绘窗口
        info("鼠标离开倒计时窗口，隐藏返回按钮，背景恢复完全透明")

    def close_timer(self):
        self.timer.stop()
        self.hide()
        info("关闭倒计时窗口，返回主界面")
        self.parent().show_main()

    def update_time(self):
        info("请求后端 /api/time 获取倒计时数据")
        try:
            resp = requests.get(f"{API_BASE}/time", timeout=2)
            data = resp.json()
            left = int(data['left'])
            percent = float(data['percent'])
            h = left // 60
            m = left % 60
            self.label.setText(f"{h:02d}小时{m:02d}分钟")
            self.progress.setValue(int(percent * 100))
            info(f"倒计时更新: 剩余 {h:02d}:{m:02d}, 进度 {percent*100:.1f}%")
        except Exception as e:
            self.label.setText("无法连接后端服务")
            self.progress.setValue(0)
            info(f"倒计时更新失败: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        info("主界面初始化")
        self.setWindowTitle("下班倒计时")
        self.setFixedSize(400, 220)

        self.start_time = QTimeEdit()
        self.end_time = QTimeEdit()
        self.start_time.setDisplayFormat("HH:mm")
        self.end_time.setDisplayFormat("HH:mm")

        self.load_config()

        form = QVBoxLayout()
        form.addWidget(QLabel("上班时间:"))
        form.addWidget(self.start_time)
        form.addSpacing(5)  # 增加上班时间和下班时间标签之间的间距
        form.addWidget(QLabel("下班时间:"))
        form.addWidget(self.end_time)
        form.addSpacing(10)  # 增加下班时间和开始按钮之间的间距

        self.start_btn = QPushButton("开始倒计时")
        self.start_btn.clicked.connect(self.start_timer)

        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addWidget(self.start_btn)
        vbox.addStretch()
        vbox.setContentsMargins(24, 24, 24, 8)

        central = QWidget()
        central.setLayout(vbox)
        self.setCentralWidget(central)

        self.timer_window = TimerWindow(self)

    def load_config(self):
        info("请求后端 /api/config 获取上下班时间")
        try:
            resp = requests.get(f"{API_BASE}/config", timeout=2)
            data = resp.json()
            self.start_time.setTime(QTime.fromString(data['start'], "HH:mm"))
            self.end_time.setTime(QTime.fromString(data['end'], "HH:mm"))
            info(f"获取到配置: 上班 {data['start']}, 下班 {data['end']}")
        except Exception as e:
            info(f"获取配置失败: {e}")

    def start_timer(self):
        start = self.start_time.time().toString("HH:mm")
        end = self.end_time.time().toString("HH:mm")
        info(f"提交配置到后端: 上班 {start}, 下班 {end}")
        try:
            requests.post(f"{API_BASE}/config", json={"start": start, "end": end}, timeout=2)
            info("配置提交成功，切换到倒计时窗口")
        except Exception as e:
            QMessageBox.warning(self, "错误", "无法连接后端服务")
            info(f"配置提交失败: {e}")
            return
        self.hide()
        self.timer_window.show()
        self.timer_window.update_time()

    def show_main(self):
        info("返回主界面")
        self.show()

if __name__ == '__main__':
    info("应用启动")
    
    # # 启动 Java 后端（后台运行）
    # subprocess.Popen(["java", "-jar", jar_path])

    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')  # 你也可以改成 dark_teal.xml
    # 设置全局背景透明
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(0, 0, 0, 0))
    app.setPalette(palette)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_()) 