from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit, QFrame,
    QPushButton, QSpacerItem, QSizePolicy, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from utils.logger import get_logger
from models.enum import ModelType, ConfigType, IsStream

logger = get_logger("model_config_dialog")

class ModelConfigDialog(QDialog):
    confirmed = Signal(dict)

    def __init__(self, parent=None, model_data=None, mode="insert"):
        super().__init__(parent)
        self.model_data = model_data
        self.mode = mode
        self.setup_ui()
        self.setup_style()
        self.setup_connections()

        if self.mode == 'edit' and self.model_data:
            self.setWindowTitle("修改模型")
            self.fill_data()
        else:
            self.setWindowTitle("创建模型")

    def setup_ui(self):
        self.setMinimumSize(450, 500)
        self.resize(600, 950)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 24, 12, 24)
        main_layout.setSpacing(8)

        self.init_title_area(main_layout, self.mode)
        self.init_form_area(main_layout)
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
        title_layout = QHBoxLayout(title_frame)
        title_layout.setSpacing(0)
        if mode=="insert":
            title_label = QLabel("创建模型")
        else:
            title_label = QLabel("修改模型")
        title_label.setProperty("class", "title")
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
                border-radius: 6px;
            }
        """)
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(12, 12, 12, 12)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(12)

        # 模型名称
        self.model_name_input = self.create_line_edit("请输入模型名称")
        self.add_form_row(form_layout, 0, "模型名称:", self.model_name_input)

        # 模型类型
        self.model_type_combo = self.create_combo_box()
        for item in ModelType:
            self.model_type_combo.addItem(item.display,item.value)
        self.add_form_row(form_layout, 1, "模型类型:", self.model_type_combo)

        # 配置用途
        self.config_type_combo = self.create_combo_box()
        for item in ConfigType:
            self.config_type_combo.addItem(item.display,item.value)
        self.add_form_row(form_layout, 2, "配置用途:", self.config_type_combo)

        # 是否流式
        self.is_stream_combo = self.create_combo_box()
        for item in IsStream:
            self.is_stream_combo.addItem(item.display,item.value)
        self.add_form_row(form_layout, 3, "是否流式:", self.is_stream_combo)

        # URL信息
        self.url_input = self.create_line_edit("请输入URL，如：https://xxx.openai.com/v1/xxxx")
        self.add_form_row(form_layout, 4, "URL:", self.url_input)

        # # Key信息
        # self.key_input = self.create_line_edit('请输入模型输入路径，如：messages;[0];input')
        # self.add_form_row(form_layout, 6, "输入路径:", self.key_input)

        # 请求头信息
        self.header_input = self.create_text_edit('请输入 JSON 格式请求头信息，如：\n{\n    "Content-Type": "application/json",\n    "Authorization": "Bearer {key}",\n    "key": "sk-xxxxx"\n}')
        self.add_form_row(form_layout, 5, "Headers:", self.header_input)

        # 请求体信息
        self.body_input = self.create_text_edit('请输入 JSON 格式请求体信息，如：\n{\n    "model": "gpt-3.5-turbo",\n    "messages": [{\n            "role": "user",\n            "content": {content}\n        }]\n}')
        self.add_form_row(form_layout, 6, "Body:", self.body_input)
        
        self.tips_label1 = QLabel("""
        <span style="color: #606266; font-size: 14px;">
            备注：需要模型输入内容，请在请求体中使用 {content} 占位符。
        </span>
        """)
        self.add_form_row(form_layout, 7, "", self.tips_label1)

        # 解析字段
        self.res_path_input = self.create_line_edit('请输入解析字段，如：messages;[0];content')
        self.add_form_row(form_layout, 8, "解析字段:", self.res_path_input)

        self.tips_label2 = QLabel("""
        <span style="color: #606266; font-size: 14px;">
            示例：{
            "messages":[{
                "role": "user",
                "content": "我是答案"
            }]
            } <br/>
            解析字段：messages;[0];content <br/>
        </span>
        """)
        # self.tips_label.setWordWrap(True)
        self.add_form_row(form_layout, 9, "", self.tips_label2)

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
        self.confirm_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.confirm_btn.setToolTip("确认")
        self.confirm_btn.setObjectName("confirmBtn")
        self.confirm_btn.setProperty("class", "primary")
        self.confirm_btn.setStyleSheet(button_style + """
            QPushButton {
                image: url(utils/img/confirm.png);
            }
        """)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setToolTip("取消")
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
    
    def create_text_edit(self, placeholder):
        text_edit = QTextEdit()
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
        text_edit.setPlaceholderText(placeholder)
        text_edit.setMinimumSize(240, 100)
        text_edit.setProperty("class", "form-input")
        return text_edit
    
    def create_combo_box(self):
        combo = QComboBox()
        combo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 8px;
                min-width: 100px;
            }
            QComboBox:hover {
                border-color: #409eff;
            }
            QComboBox:focus {
                border-color: #409eff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
                border: none;
            }
            QComboBox::down-arrow {
                image: url(utils/img/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        combo.setMinimumSize(240, 36)
        combo.setProperty("class", "form-input")
        return combo

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
        
        if not self.model_name_input.text():
            self.show_message("error", "错误", "模型名称不能为空")
            return
        if not self.url_input.text():
            self.show_message("error", "错误", "URL不能为空")
            return
            
        if self.mode == 'edit' and self.model_data:
            form_data["config_id"] = self.model_data.get("config_id")
        self.confirmed.emit(form_data)
        self.accept()

    def fill_data(self):
        if not self.model_data:
            return
        self.model_name_input.setText(self.model_data.get("model_name", ""))
        self.model_type_combo.setCurrentText(ModelType.display_of(self.model_data.get("model_type", "")))
        self.config_type_combo.setCurrentText(ConfigType.display_of(self.model_data.get("config_type", "")))
        self.is_stream_combo.setCurrentText(IsStream.display_of(self.model_data.get("is_stream", "")))
        self.url_input.setText(self.model_data.get("url_info", ""))
        self.header_input.setText(self.model_data.get("headers", ""))
        self.body_input.setText(self.model_data.get("body", ""))
        self.res_path_input.setText(self.model_data.get("res_path", ""))

    def get_form_data(self):
        return {
            'model_name': self.model_name_input.text(),
            'model_type': self.model_type_combo.currentData(),
            'config_type': self.config_type_combo.currentData(),
            'is_stream': self.is_stream_combo.currentData(),
            'url_info': self.url_input.text(),
            'headers': self.header_input.toPlainText(),
            'body': self.body_input.toPlainText(),
            'res_path': self.res_path_input.text()
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
            }

            .form-input:focus {
                border-color: #409eff;
            }

            QComboBox {
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #ffffff;
            }

            QComboBox:hover {
                border-color: #409eff;
            }

            QComboBox::drop-down {
                border: none;
            }

            QComboBox::down-arrow {
                image: url(utils/img/arrow-down.png);
                width: 12px;
                height: 12px;
            }
        """)

        self.confirm_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))

    def show_message(self, type, title, message):
        """显示信息对话框"""
        msg = QMessageBox()
        msg.setStyleSheet("""
            QMessageBox {
                font-family: "Microsoft YaHei";
                width: 300px;
                height: 150px;
            }
        """)
        if type == "error":
            msg.critical(self, title, message)
        elif type == "warning":
            msg.warning(self, title, message)
        else:
            msg.information(self, title, message)