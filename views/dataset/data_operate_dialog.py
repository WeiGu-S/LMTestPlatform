from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit, QFrame,
    QPushButton, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from utils.logger import get_logger
from models.enum import QuestionType, QuestionLabel, DataType

logger = get_logger("data_dialog")


class DataDialog(QDialog):
    confirmed = Signal(dict)

    def __init__(self, parent=None, data=None, mode="insert"):
        super().__init__(parent)
        self.data = data
        self.mode = mode
        self.setup_ui()
        self.setup_style()
        self.setup_connections()

        if self.mode == 'edit' and self.data:
            self.setWindowTitle("修改数据")
            self.fill_data()
        else:
            self.setWindowTitle("创建数据")

    def setup_ui(self):
        self.setMinimumSize(450, 380)
        # self.resize(450, 380)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 24, 12, 24)
        main_layout.setSpacing(8)

        self.init_title_area(main_layout,self.mode)
        # main_layout.addStretch(1)    
        self.init_form_area(main_layout)
        # main_layout.addStretch(1)
        self.init_button_area(main_layout)

    def init_title_area(self, parent_layout, mode="insert"):
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fb;
                border:none;
                border-radius: 6px;
            }
        """)
        # title_frame.setFrameShape(QFrame.StyledPanel)
        title_layout = QHBoxLayout(title_frame) # 使用水平布局
        # title_layout.setContentsMargins(0)
        title_layout.setSpacing(0)
        if mode=="insert":
            title_label = QLabel("创建数据")
        else:
            title_label = QLabel("修改数据")
        title_label.setProperty("class", "title")
        # 设置字体样式
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 600;
                color: #1f2329;
            }
        """)
        title_layout.addStretch()
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        parent_layout.addWidget(title_frame)

    def init_form_area(self, parent_layout):
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: none;
                border-radius: 8px;
            }
        """)
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(12, 12, 12, 12)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(12)

        common_style = f"""
            font-family: 'Microsoft YaHei';
            font-size: 14px;
            color: #333;
            background: white;
            border: 1px solid #dcdfe6;
            border-radius: 4px;
            padding: 6px ;
            min-height: 24px;
        """

        combo_style = f"""
            QComboBox {{
                {common_style}
                min-width: 100px;
            }}
            QComboBox:hover {{
                border-color: #c0c4cc;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url(utils/img/down_arrow.png);
                width: 12px;
                height: 12px;
            }}
        """

        # 所属数据集名称
        self.dataset_input = self.create_line_edit("")
        self.add_form_row(form_layout, 0, "所属数据集:", self.dataset_input)
        # 数据分类
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItem("全部", None)
        for item in DataType:
            self.data_type_combo.addItem(item.display,item.value)
        self.add_form_row(form_layout, 1, "数据分类:", self.data_type_combo)
        self.data_type_combo.setStyleSheet(combo_style)
        # 题型
        self.question_type_combo = QComboBox()
        self.question_type_combo.addItem("全部", None)
        for item in QuestionType:
            self.question_type_combo.addItem(item.display,item.value)
        self.add_form_row(form_layout, 2, "题型:", self.question_type_combo)
        self.question_type_combo.setStyleSheet(combo_style)
        # 标签
        self.question_label_combo = QComboBox()
        self.question_label_combo.addItem("全部", None)
        for item in QuestionLabel:
            self.question_label_combo.addItem(item.display,item.value)
        self.add_form_row(form_layout, 3, "标签:", self.question_label_combo)
        self.question_label_combo.setStyleSheet(combo_style)
        # 上下文
        self.context_input = self.create_text_edit()
        self.add_form_row(form_layout, 4, "上下文:", self.context_input)
        # 问题
        self.question_input = self.create_text_edit()
        self.add_form_row(form_layout, 5, "问题:", self.question_input)
        # 答案
        self.answer_input = self.create_text_edit()
        self.add_form_row(form_layout, 6, "答案:", self.answer_input)
        
        parent_layout.addWidget(form_frame)

    def init_button_area(self, parent_layout):
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: none;

            }
        """)
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
    

    def create_text_edit(self):
        text_edit = QTextEdit()
        text_edit.setMinimumSize(240, 36)
        text_edit.setProperty("class", "form-text-input")
        text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #ffffff;
                font-size: 14px;
                color: #606266;
            }
            QTextEdit:hover {
                border-color: #409eff;
            }
            QTextEdit:focus {
                border-color: #409eff;
            }
        """)
        return text_edit

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
        if self.mode == 'edit' and self.data:
            form_data["data_id"] = self.data.get("data_id")
        self.confirmed.emit(form_data)
        self.accept()

    def fill_data(self):
        if not self.data:
            return
        self.dataset_input.setText(str(self.data.get("data_id", "")))
        
        # 设置数据分类
        data_type = self.data.get("data_type")
        if data_type:
            index = self.data_type_combo.findData(data_type)
            if index >= 0:
                self.data_type_combo.setCurrentIndex(index)
        
        # 设置题型
        question_type = self.data.get("question_type")
        if question_type:
            index = self.question_type_combo.findData(question_type)
            if index >= 0:
                self.question_type_combo.setCurrentIndex(index)
        
        # 设置标签
        question_label = self.data.get("question_label")
        if question_label:
            index = self.question_label_combo.findData(question_label)
            if index >= 0:
                self.question_label_combo.setCurrentIndex(index)
        
        # 设置上下文、问题和答案
        self.context_input.setText(self.data.get("context", ""))
        self.question_input.setText(self.data.get("question", ""))
        self.answer_input.setText(self.data.get("answer", ""))

    def get_form_data(self):
        return {
            'data_type': self.data_type_combo.currentData(),
            'question_type': self.question_type_combo.currentData(),
            'question_label': self.question_label_combo.currentData(),
            'context': self.context_input.toPlainText(),
            'question': self.question_input.toPlainText(),
            'answer': self.answer_input.toPlainText()
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
           
        """)

        self.confirm_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))