from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QGridLayout, QDialog
)
from PySide6.QtCore import Qt
from models.dataset_model import DatasetModel
from utils.database import DatabaseManager

class ImportDialog(QDialog):
    def __init__(self, parent=None, dataset_id=None):
        super().__init__(parent)
        self.dataset_id = dataset_id
        # 设置对话框标题
        self.setWindowTitle("数据导入")
        # 设置对话框大小
        self.setMinimumSize(800, 600)
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                border: 1px solid #e4e7ed;
                border-radius: 4px;
            }
        """)
        # 初始化界面布局
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        # 主体布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        # 顶部区域
        top_layout = QHBoxLayout()
        
        # 选择文件按钮
        self.select_file_btn = QPushButton("选择文件")
        self.select_file_btn.setMinimumSize(100, 32)
        self.select_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #409eff;
                color: white;
                border-radius: 4px;
                width: 60px;
                height: 32px;
            }
            QPushButton:hover {
                background-color: #66b1ff;
            }
        """)
        self.select_file_btn.clicked.connect(self.select_file)
        top_layout.addWidget(self.select_file_btn)
        # top_layout.addStretch()
        
        main_layout.addLayout(top_layout)

        # 表格区域
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["序号", "标题", "答案", "标签"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e4e7ed;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #f5f7fa;
                padding: 5px;
                border: none;
                border-right: 1px solid #e4e7ed;
                border-bottom: 1px solid #e4e7ed;
            }
        """)
        # 设置列宽
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 280)
        self.table.setColumnWidth(2, 280)
        self.table.setColumnWidth(3, 180)
        
        main_layout.addWidget(self.table)

        # 底部按钮区域
        button_layout = QHBoxLayout()     
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)   
        # 确定按钮
        self.confirm_btn = QPushButton()
        # self.confirm_btn.setMinimumSize(80, 32)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                image: url(utils/img/confirm.png);
                width: 40px;
                height: 40px;
            }
            QPushButton:hover {
                cursor: pointer;
            }
            QPushButton:pressed {
                padding: 4px;
            }
        """)
        self.confirm_btn.clicked.connect(self.import_confirmed)
        
        # 取消按钮
        self.cancel_btn = QPushButton()
        self.cancel_btn.setMinimumSize(80, 32)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                image: url(utils/img/cancel.png);
                width: 40px;
                height: 40px;
            }
            QPushButton:hover {
                cursor: pointer;
            }
            QPushButton:pressed {
                padding: 4px;
            }
        """)
        
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)

    def select_file(self):
        """选择文件并读取数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            # TODO: 实现文件读取逻辑
            pass

    def import_confirmed(self):
        """导入确认"""
        # TODO: 实现导入逻辑
        self.accept()