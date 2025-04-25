from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit, QFrame,
    QPushButton, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from utils.logger import get_logger
import enum

logger = get_logger("data_collection_dialog")


class DataCollectionDialog(QDialog):
    confirmed = Signal(dict)

    def __init__(self, parent=None, data_collection=None, mode="insert"):
        super().__init__(parent)
        self.data_collection = data_collection
        self.mode = mode
        self.setup_ui()
        self.setup_style()
        self.setup_connections()

        if self.mode == 'edit' and self.data_collection:
            self.setWindowTitle("修改数据集")
            self.fill_data()
        else:
            self.setWindowTitle("创建数据集")

    def setup_ui(self):
        self.setMinimumSize(250, 380)
        # self.resize(450, 380)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(8)

        main_layout.addStretch(1)    
        self.init_form_area(main_layout)
        main_layout.addStretch(1)
        self.init_button_area(main_layout)

    def init_form_area(self, parent_layout):
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(12, 12, 12, 12)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(20)

        # 所属项目
        self.project_name_input = self.create_line_edit("请输入所属项目")
        self.add_form_row(form_layout, 0, "所属项目:", self.project_name_input)

        # 数据集名称
        self.name_input = self.create_line_edit("请输入数据集名称")
        self.add_form_row(form_layout, 1, "数据集名称:", self.name_input)

        parent_layout.addWidget(form_frame)

    def init_button_area(self, parent_layout):
        button_frame = QFrame()
        button_frame.setFrameShape(QFrame.StyledPanel)
        button_layout = QHBoxLayout(button_frame)
        button_frame.setStyleSheet("""
            QHBoxLayout {
                margin: 0;
                spacing: 6px;
            }
        """)
        button_layout.setContentsMargins(0, 4, 0, 4)
        button_layout.setSpacing(6)

        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
                min-height: 50px;
                min-width: 50px;
            }
            QPushButton:hover {
                cursor: pointer;
            }
            QPushButton:pressed {
                padding: 4px;
            }
        """

        self.confirm_btn = QPushButton()
        self.confirm_btn.setObjectName("confirmBtn")
        self.confirm_btn.setProperty("class", "primary")
        self.confirm_btn.setStyleSheet(button_style + """
            QPushButton {
                image: url(utils/img/confirm.png);
            }
        """)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setProperty("class", "secondary")
        self.cancel_btn.setStyleSheet(button_style + """
            QPushButton {
                image: url(utils/img/cancel.png);
            }
        """)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.confirm_btn)
        button_layout.addStretch()

        parent_layout.addWidget(button_frame)

    def create_line_edit(self, placeholder):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setMinimumSize(240, 36)
        line_edit.setMaxLength(255)
        line_edit.setProperty("class", "form-input")
        return line_edit

    def add_form_row(self, layout, row, label_text, widget):
        label = QLabel(label_text)
        label.setProperty("class", "form-label")
        label.setFixedWidth(80)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(label, row, 0)
        layout.addWidget(widget, row, 1)

    def setup_connections(self):
        self.cancel_btn.clicked.connect(self.reject)
        self.confirm_btn.clicked.connect(self.emit_confirmed)

    def emit_confirmed(self):
        form_data = self.get_form_data()
        form_data["mode"] = self.mode
        if self.mode == 'edit' and self.data_collection:
            form_data["collection_id"] = self.data_collection.collection_id
        self.confirmed.emit(form_data)
        self.accept()

    def fill_data(self):
        if not self.data_collection:
            return
        self.project_name_input.setText(self.data_collection.project_name or '')
        self.name_input.setText(self.data_collection.collection_name or '')

    def get_form_data(self):
        return {
            'collection_name': self.name_input.text(),
            'project_name': self.project_name_input.text()
        }

    def setup_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fb;
                border: 1px solid #dfe4ec;
                border-radius: 6px;
            }

            .form-label {
                font-size: 15px;
                font-weight: bold;
                color: #333333;
            }

            .form-input {
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #ffffff;
                font-size: 14px;
                color: #606266;
            }

            .form-input:hover {
                border-color: #409eff;
                box-shadow: 0 0 4px rgba(64, 158, 255, 0.2);
            }

            .form-input:focus {
                border-color: #409eff;
                box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
            }
        """)

        self.confirm_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))