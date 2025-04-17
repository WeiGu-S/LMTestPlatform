from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QDateEdit, QGridLayout, QFrame,
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QDate

class DatasetDialog(QWidget):
    def __init__(self, parent=None, dataset=None):
        super().__init__(parent)
        # 初始化界面布局
        self.init_ui()
        # 如果传入数据集则填充内容
        if dataset:
            self.fill_dataset_data(dataset)
            
    def init_ui(self):
        """初始化界面"""
        # 主体布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 创建表单区域
        form_layout = QGridLayout()
        
        # 数据集名称输入
        name_label = QLabel("数据集名称:")
        self.name_input = QLineEdit()
        form_layout.addWidget(name_label, 0, 0)
        form_layout.addWidget(self.name_input, 0, 1)
        
        # 数据集类型选择
        type_label = QLabel("数据类型:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["训练集", "验证集", "测试集"])
        form_layout.addWidget(type_label, 1, 0)
        form_layout.addWidget(self.type_combo, 1, 1)
        
        # 数据集状态选择
        status_label = QLabel("状态:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["启用", "停用"])
        form_layout.addWidget(status_label, 2, 0)
        
        # 数据集描述输入
        desc_label = QLabel("描述:")
        self.desc_input = QLineEdit()
        form_layout.addWidget(desc_label, 3, 0)
        form_layout.addWidget(self.desc_input, 3, 1)
        
        # 添加表单到主体布局
        main_layout.addLayout(form_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 确认和取消按钮
        self.confirm_btn = QPushButton("确认")
        self.cancel_btn = QPushButton("取消")
        
        button_layout.addStretch()
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
    def fill_dataset_data(self, dataset):
        """填充数据集内容"""
        self.name_input.setText(dataset.get('name', ''))
        index = self.type_combo.findText(dataset.get('type', ''))
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        if dataset.get('create_date'):
            self.date_edit.setDate(QDate.fromString(dataset['create_date'], Qt.ISODate))
        self.desc_input.setText(dataset.get('description', ''))
