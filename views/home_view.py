from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        
        # 创建主布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 创建外层框架
        home_frame = QWidget()
        home_frame.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                background-image: url(/Users/weigu/Desktop/00001.jpg);
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(home_frame)
        
        # 创建框架内部布局
        frame_layout = QVBoxLayout()
        home_frame.setLayout(frame_layout)
        
        # 添加欢迎标签
        welcome_label = QLabel("欢迎使用 上研院 大模型测试平台 v1.0")
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #2c3e50;
                padding: 20px;
            }
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        
        # 使用伸缩器使标签垂直居中
        frame_layout.addStretch(1)
        frame_layout.addWidget(welcome_label)
        frame_layout.addStretch(1)
