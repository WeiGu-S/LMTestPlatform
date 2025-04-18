from PySide6.QtWidgets import (
    QDial, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QDateEdit, QGridLayout, QFrame,
    QSpacerItem, QSizePolicy, QDialog, QTextEdit
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QColor, QPalette

class DatasetDialog(QDialog):
    def __init__(self, parent=None, dataset=None):
        super().__init__(parent)
        # 设置对话框标题
        self.setWindowTitle("数据集信息")
        # 设置对话框大小
        self.setMinimumSize(480, 380)
        self.resize(520, 420)  # 设置默认大小
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                border: 1px solid #e4e7ed;
                border-radius: 8px;
                box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
            }
        """)
        # 初始化界面布局
        self.init_ui()
        # 如果传入数据集则填充内容
        if dataset:
            self.fill_dataset_data(dataset)
            
    def init_ui(self):
        """初始化界面"""
        # 主体布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)  # 增加外边距
        main_layout.setSpacing(20)  # 增加控件间距
        self.setLayout(main_layout)
        
        # 创建表单区域
        form_layout = QGridLayout()
        form_layout.setContentsMargins(0, 0, 0, 15)  # 增加表单区域底部边距
        form_layout.setHorizontalSpacing(20)  # 增加水平间距
        form_layout.setVerticalSpacing(18)  # 增加垂直间距
        
        # 数据集名称输入
        name_label = QLabel("数据集名称:")
        name_label.setStyleSheet("QLabel { font-size: 15px; font-weight: 500; color: #333333; }")
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("QLineEdit { border: 1px solid #dcdfe6; border-radius: 4px; padding: 8px 12px; background-color: #ffffff; font-size: 14px; color: #606266; min-width: 240px; } QLineEdit:hover { border-color: #c0c4cc; } QLineEdit:focus { border-color: #409eff; box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2); }")
        self.name_input.setPlaceholderText("请输入数据集名称")
        self.name_input.setMinimumWidth(240)
        self.name_input.setMinimumHeight(36)
        self.name_input.setMaxLength(255)
        form_layout.addWidget(name_label, 0, 0)
        form_layout.addWidget(self.name_input, 0, 1)
        
        # 数据集类型选择
        category_label = QLabel("数据类型:")
        category_label.setStyleSheet("QLabel { font-size: 15px; font-weight: 500; color: #333333; }")
        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(36)
        self.category_combo.setMinimumWidth(240)
        self.category_combo.setStyleSheet("""
            QComboBox { 
                border: 1px solid #dcdfe6; 
                border-radius: 4px; 
                padding: 8px 12px; 
                background-color: #ffffff; 
                font-size: 14px; 
                color: #606266; 
                min-width: 240px; 
            } 
            QComboBox:hover { 
                border-color: #c0c4cc; 
            }
            QComboBox:focus { 
                border-color: #409eff; 
                box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2); 
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                border-left: none;
            }
        """)
        self.category_combo.addItems(["视频", "图片", "文本", "音频"])
        form_layout.addWidget(category_label, 1, 0)
        form_layout.addWidget(self.category_combo, 1, 1)
        
        # 数据集状态选择
        status_label = QLabel("状态:")
        status_label.setStyleSheet("QLabel { font-size: 15px; font-weight: 500; color: #333333; }")
        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(36)
        self.status_combo.setMinimumWidth(240)
        self.status_combo.setStyleSheet("""
            QComboBox { 
                border: 1px solid #dcdfe6; 
                border-radius: 4px; 
                padding: 8px 12px; 
                background-color: #ffffff; 
                font-size: 14px; 
                color: #606266; 
                min-width: 240px; 
            } 
            QComboBox:hover { 
                border-color: #c0c4cc; 
            }
            QComboBox:focus { 
                border-color: #409eff; 
                box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2); 
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                border-left: none;
            }
        """)
        self.status_combo.addItems(["启用", "停用"])
        form_layout.addWidget(status_label, 2, 0)
        form_layout.addWidget(self.status_combo, 2, 1)
        
        # 备注输入
        desc_label = QLabel("备注:")
        desc_label.setStyleSheet("QLabel { font-size: 15px; font-weight: 500; color: #333333; }")
        self.desc_input = QTextEdit()
        self.desc_input.setMinimumHeight(80)
        self.desc_input.setMinimumWidth(240)
        self.desc_input.setStyleSheet("""
            QTextEdit { 
                border: 1px solid #dcdfe6; 
                border-radius: 4px; 
                padding: 8px 12px; 
                background-color: #ffffff; 
                font-size: 14px; 
                color: #606266; 
                min-width: 240px; 
            } 
            QTextEdit:hover { 
                border-color: #c0c4cc; 
            }
            QTextEdit:focus { 
                border-color: #409eff; 
                box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2); 
            }
        """)
        self.desc_input.setPlaceholderText("请输入备注")
        form_layout.addWidget(desc_label, 3, 0)
        form_layout.addWidget(self.desc_input, 3, 1)
        
        # 添加表单到主体布局
        main_layout.addLayout(form_layout)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #ebeef5; margin-top: 1px; margin-bottom: 1px;")
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 6, 0, 0)  # 增加按钮区域上边距
        button_layout.setSpacing(15)  # 增加按钮间距
        button_layout.setAlignment(Qt.AlignCenter) 
        button_layout.addStretch()  # 添加伸缩因子，使按钮居中
        
        # 确认和取消按钮
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.setMinimumSize(90, 36)
        self.confirm_btn.setCursor(Qt.PointingHandCursor)  # 设置鼠标悬停时为手型光标
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #409eff;
                color: white;
                border-radius: 4px;
                font-size: 15px;
                font-weight: 500;
                padding: 8px 20px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #66b1ff;
            }
            QPushButton:pressed {
                background-color: #3a8ee6;
            }
        """)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumSize(90, 36)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)  # 设置鼠标悬停时为手型光标
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f7fa;
                color: #606266;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                font-size: 15px;
                font-weight: 500;
                padding: 8px 20px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #ecf5ff;
                color: #409eff;
                border-color: #c6e2ff;
            }
            QPushButton:pressed {
                background-color: #e6ebf5;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.confirm_btn)
        
        main_layout.addLayout(button_layout)
        
    def fill_dataset_data(self, dataset):
        """填充数据集内容"""
        self.name_input.setText(dataset.get('dataset_name', ''))
        index = self.category_combo.findText(dataset.get('dataset_category', ''))
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        index = self.status_combo.findText(dataset.get('status', ''))
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        self.desc_input.setText(dataset.get('remark', ''))
        # 设置焦点到名称输入框
        self.name_input.setFocus()
