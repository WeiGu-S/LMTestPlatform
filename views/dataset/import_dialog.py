from webbrowser import get
from PySide6.QtWidgets import (
    QDial, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QDateEdit, QGridLayout, QFrame,
    QSpacerItem, QSizePolicy, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QColor, QPalette
from models.dataset_model import DatasetModel
from utils.database import DatabaseManager

class ImportDialog(QDialog):
    def __init__(self,parent = None,dataset_id=None):
        super().__init__(parent)
        # 设置对话框标题
        self.setWindowTitle("数据导入")
        # 设置对话框大小
        self.setMinimumSize(400, 300)
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
        main_layout.setContentsMargins(20, 20, 20, 20)  # 设置外边距
        main_layout.setSpacing(15)  # 设置控件间距
        self.setLayout(main_layout)

        # 创建表单区域
        form_layout = QGridLayout()
        form_layout.setContentsMargins(0, 0, 0, 10)  # 设置表单区域边距
        form_layout.setHorizontalSpacing(15)  # 水平间距

        # 数据集名称
        name_label = QLabel("数据集名称:")
        name_label.setStyleSheet("QLabel { font-size: 14px; color: #333333; }")
        self.name_input = QLineEdit()
        session = DatabaseManager.get_session()
        dataset_name = DatasetModel.get_dataset_by_id(session, self.dataset_id).get('name')
        self.name_input.setText(dataset_name)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #e4e7ed;
                border-radius: 4px;
                padding: 5px;
            }
        """)

        form_layout.addWidget(name_label, 0, 0)
        form_layout.addWidget(self.name_input, 0, 1)

        # 创建按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)  # 设置按钮区域边距
        button_layout.setSpacing(10)  # 按钮间距
        # 导入按钮
        self.import_btn = QPushButton("导入")
        self.import_btn.setMinimumSize(80, 32)
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #409eff;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #66b1ff;
            }
        """)

        button_layout.addWidget(self.import_btn)
        main_layout.addLayout(button_layout)

        # 表格区域
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["序号", "题干", "答案", "标签", "状态", "类型"])
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.table_widget)

        self.import_btn.clicked.connect(self.choose_file)

        # 底部按钮区域
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 10, 0, 0)  # 设置按钮区域边距
        bottom_layout.setSpacing(10)  # 按钮间距
        # 确认按钮
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.setMinimumSize(80, 32)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #409eff;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #66b1ff;
            }
        """)
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumSize(80, 32)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e4e7ed;
                color: #606266;
                border-radius: 4px;
            }
            QPushButton:hover {
                
                background-color: #dcdfe6;
                color: #606266;
            }
        """)
        bottom_layout.addWidget(self.confirm_btn)
        bottom_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(bottom_layout)
        # self.confirm_btn.clicked.connect(self.handle_import)

        # 分页控件区域
        # pagination_frame = QFrame()
        # pagination_frame.setStyleSheet("QFrame { background: #fff; border-radius: 8px; border: 1px solid #eaeaea; }")
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(2, 2, 2, 2)  # 增加上边距
        
        self.total_items_label = QLabel("共 0 条")
        self.total_items_label.setStyleSheet("font-size: 14px; color: #606266; border: none; padding: 0 0 0 10px;")
        pagination_layout.addWidget(self.total_items_label)
        # 总条数标签已添加，不需要重复添加
        # pagination_layout.addWidget(self.total_items_label)    

        self.prev_button = QPushButton("<")
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 0 4px 0 4px;
                font-size: 20px; 
                min-width: 16px;
                text-align: center;
            }
            QPushButton:hover {
                color: #409eff;
                border-color: #c6e2ff;
            }
            QPushButton:disabled {
                color: #c0c4cc;
                background-color: #f4f4f5;
                border-color: #e4e7ed;
            }
        """)

        self.page_combo = QComboBox()  # 用于显示和选择页码
        self.page_combo.setStyleSheet("""
            QComboBox {
                text-align: center !important;
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                padding: 6px 6px;
                background-color: #ffffff;
                font-size: 16px;
                color: #606266;
                min-width: 16px;
            }
            QComboBox:hover {
                border-color: #c0c4cc;
            }
            QComboBox:focus {
                border-color: #409eff;
            }
        """)
        
        self.next_button = QPushButton(">")
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 0 4px 0 4px;
                font-size: 20px; 
                min-width: 16px;
                text-align: center;
            }
            QPushButton:hover {
                color: #409eff;
                border-color: #c6e2ff;
            }
            QPushButton:disabled {
                color: #c0c4cc;
                background-color: #f4f4f5;
                border-color: #e4e7ed;
            }
        """)
        
        self.page_size_label = QLabel("10 条/页")
        self.page_size_label.setStyleSheet("font-size: 14px; color: #606266; border: 1px solid #dcdfe6; padding: 8px 0px; margin: 0;")

        pagination_layout.addWidget(self.total_items_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_combo)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_size_label)

        main_layout.addWidget(pagination_layout) # 添加包含分页控件的框架
