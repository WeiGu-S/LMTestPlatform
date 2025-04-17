from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        welcome_label = QLabel("欢迎使用 上研院 大模型测试平台 v1.0")
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                color: #2c3e50;
                padding: 20px;
            }
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        
        layout.addStretch(1)
        layout.addWidget(welcome_label)
        layout.addStretch(1)