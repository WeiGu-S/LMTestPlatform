from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit, QFrame,
    QPushButton
)
from PySide6.QtCore import Qt,Slot,Signal
from PySide6.QtGui import QCursor
from utils.logger import get_logger
from models.dataset_model import DatasetModel, DatasetStatus, DatasetCategory
from utils.database import DatabaseManager

logger = get_logger("dataset_dialog")

class DatasetDialog(QDialog):

    confirmed = Signal(dict)
    cancel_signal = Signal()
    def __init__(self, parent=None, dataset=None, mode="insert"):
        super().__init__(parent)
        self.dataset = dataset
        self.mode = mode
        self.setup_ui()
        self.setup_style()
        self.setup_connections()
        
        if self.mode == 'modify' and self.dataset:
            self.setWindowTitle("修改数据集")
            self.fill_data()
        else:
            self.setWindowTitle("创建数据集")

    def setup_ui(self):
        """初始化UI组件"""
        self.setWindowTitle("数据集信息")
        self.setMinimumSize(480, 380)
        self.resize(520, 420)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # 表单布局
        self.setup_form(main_layout)
        
        # 分隔线
        self.add_separator(main_layout)
        
        # 按钮区域
        self.setup_buttons(main_layout)

    def setup_form(self, parent_layout):
        """设置表单区域"""
        form_layout = QGridLayout()
        form_layout.setContentsMargins(0, 0, 0, 15)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(18)
        
        # 数据集名称
        self.name_input = self.create_line_edit("请输入数据集名称")
        self.add_form_row(form_layout, 0, "数据集名称:", self.name_input)
        
        # 数据类型
        self.category_combo = self.create_combo_box(["视频", "图片", "文本", "音频"])
        self.add_form_row(form_layout, 1, "数据类型:", self.category_combo)
        
        # 状态
        self.status_combo = self.create_combo_box(["启用", "停用"])
        self.add_form_row(form_layout, 2, "状态:", self.status_combo)
        
        # 备注
        self.remark_input = self.create_text_edit("请输入备注")
        self.add_form_row(form_layout, 3, "备注:", self.remark_input)
        
        parent_layout.addLayout(form_layout)

    def add_form_row(self, layout, row, label_text, widget):
        """添加表单行"""
        label = QLabel(label_text)
        label.setProperty("class", "form-label")
        layout.addWidget(label, row, 0)
        layout.addWidget(widget, row, 1)

    def create_line_edit(self, placeholder):
        """创建输入框"""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setMinimumSize(240, 36)
        line_edit.setMaxLength(255)
        line_edit.setProperty("class", "form-input")
        return line_edit

    def create_combo_box(self, items):
        """创建下拉框"""
        combo = QComboBox()
        combo.addItems(items)
        combo.setMinimumSize(240, 36)
        combo.setProperty("class", "form-combo")
        return combo

    def create_text_edit(self, placeholder):
        """创建文本编辑框"""
        text_edit = QTextEdit()
        text_edit.setPlaceholderText(placeholder)
        text_edit.setMinimumSize(240, 80)
        text_edit.setProperty("class", "form-text")
        return text_edit

    def add_separator(self, parent_layout):
        """添加分隔线"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setProperty("class", "separator")
        parent_layout.addWidget(separator)

    def setup_buttons(self, parent_layout):
        """设置按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 6, 0, 0)
        button_layout.setSpacing(15)
        
        # 确认按钮
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.setMinimumSize(90, 36)
        self.confirm_btn.setProperty("class", "primary-button")
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumSize(90, 36)
        self.cancel_btn.setProperty("class", "secondary-button")
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.confirm_btn)
        
        parent_layout.addLayout(button_layout)

    def setup_style(self):
        """设置样式表"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                border: 1px solid #e4e7ed;
                border-radius: 8px;
            }
            
            .form-label {
                font-size: 15px;
                font-weight: 500;
                color: #333333;
            }
            
            .form-input, .form-combo, .form-text {
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: #ffffff;
                font-size: 14px;
                color: #606266;
            }
            
            .form-input:hover, .form-combo:hover, .form-text:hover {
                border-color: #c0c4cc;
            }
            
            .form-input:focus, .form-combo:focus, .form-text:focus {
                border-color: #409eff;
                box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
            }
            
            .form-combo::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                border-left: none;
            }
            
            .separator {
                background-color: #ebeef5;
                margin: 1px 0;
                height: 1px;
            }
            
            .primary-button {
                background-color: #409eff;
                color: white;
                border-radius: 4px;
                font-size: 15px;
                font-weight: 500;
                padding: 8px 20px;
            }
            
            .primary-button:hover {
                background-color: #66b1ff;
            }
            
            .primary-button:pressed {
                background-color: #3a8ee6;
            }
            
            .secondary-button {
                background-color: #f5f7fa;
                color: #606266;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                font-size: 15px;
                font-weight: 500;
                padding: 8px 20px;
            }
            
            .secondary-button:hover {
                background-color: #ecf5ff;
                color: #409eff;
                border-color: #c6e2ff;
            }
            
            .secondary-button:pressed {
                background-color: #e6ebf5;
            }
        """)
        
        # 设置鼠标悬停样式
        self.confirm_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))

    def setup_connections(self):
        """连接信号与槽"""
        self.cancel_btn.clicked.connect(self.cancel_signal.emit)
        self.confirm_btn.clicked.connect(self.emit_confirmed)

    def emit_confirmed(self):
        """发射确认信号"""
        form_data = self.get_form_data()
        form_data["mode"] = self.mode
        if self.mode == 'edit':
            form_data["dataset_id"] = self.dataset.get('id')

        self.confirmed.emit(form_data)
        self.accept()

    def fill_data(self):
        """填充数据集数据"""
        self.setWindowTitle("修改数据集")
        self.name_input.setText(self.dataset.get('dataset_name', ''))
        
        category_index = self.category_combo.findText(
            self.dataset.get('dataset_category', ''))
        if category_index >= 0:
            self.category_combo.setCurrentIndex(category_index)
            
        status_index = self.status_combo.findText(
            self.dataset.get('status', ''))
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)
            
        self.remark_input.setText(self.dataset.get('remark', ''))
        self.name_input.setFocus()

    def get_form_data(self):
        """获取表单数据"""
        return {
            'dataset_name': self.name_input.text(),
            'dataset_category': self.category_combo.currentText(),
            'status': self.status_combo.currentText(),
            'remark': self.remark_input.toPlainText()
        }

    def set_form_data(self, dataset):
        """设置表单数据"""
        self.dataset = dataset
        self.fill_data()