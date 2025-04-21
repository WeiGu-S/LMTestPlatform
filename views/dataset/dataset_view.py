from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QDateEdit, QGridLayout, QFrame,
    QSpacerItem, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QIcon, QColor, QFont, QPalette
from functools import partial
from utils.logger import get_logger

logger = get_logger("dataset_view")

class DatasetView(QWidget):
    # 定义所有信号
    query_signal = Signal(dict)      # 查询信号，传递过滤条件
    reset_signal = Signal()          # 重置信号
    insert_signal = Signal()         # 新建数据集信号
    export_signal = Signal()         # 导出数据信号
    page_changed_signal = Signal(int)    # 页码变化信号
    page_size_changed_signal = Signal(int)  # 每页条数变化信号
    modify_signal = Signal(str)      # 修改数据集信号，传递ID
    view_signal = Signal(str)        # 查看数据集信号，传递ID
    import_signal = Signal(str)       # 导入数据信号，传递ID
    delete_signal = Signal(str)       # 删除数据集信号，传递ID

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("数据集管理")
        self.resize(1200, 800)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # 1. 筛选区域
        self.setup_filter_area(main_layout)
        
        # 2. 操作按钮区域
        self.setup_action_buttons(main_layout)
        
        # 3. 表格区域
        self.setup_table_area(main_layout)
        
        # 4. 分页区域
        self.setup_pagination_area(main_layout)

    def setup_connections(self):
        """连接内部信号到槽函数"""
        # 查询按钮点击时发射查询信号
        self.query_button.clicked.connect(self.emit_query_signal)
        # 重置按钮点击时发射重置信号
        self.reset_button.clicked.connect(self.reset_signal.emit)
        # 新建按钮点击时发射新建信号
        self.insert_button.clicked.connect(self.insert_signal.emit)
        # 导出按钮点击时发射导出信号
        self.export_button.clicked.connect(self.export_signal.emit)
        # 分页控件信号连接
        self.prev_btn.clicked.connect(lambda: self.page_changed_signal.emit(self.current_page() - 1))
        self.next_btn.clicked.connect(lambda: self.page_changed_signal.emit(self.current_page() + 1))
        self.page_combo.currentTextChanged.connect(lambda: self.page_changed_signal.emit(self.current_page()))
        # self.page_size_combo.currentTextChanged.connect(lambda: self.page_size_changed_signal.emit(int(self.page_size_combo.currentText())))

    def emit_query_signal(self):
        """收集筛选条件并发射查询信号"""
        filters = {
            'dataset_name': self.name_filter_input.text().strip(),
            'status': self.status_filter_combo.currentText(),
            'dataset_category': self.category_filter_combo.currentText(),
            'start_date': self.start_date_edit.date(),
            'end_date': self.end_date_edit.date()
        }
        self.query_signal.emit(filters)

    def setup_filter_area(self, parent_layout):
        """设置筛选区域"""
        filter_frame = QFrame()
        filter_frame.setObjectName("filterFrame")
        filter_frame.setStyleSheet("""
            #filterFrame {
                background-color: #ffffff;
                border-radius: 6px;
                border: 1px solid #eaeaea;
                padding: 12px;
            }
        """)

        filter_layout = QGridLayout(filter_frame)
        filter_layout.setHorizontalSpacing(12)
        filter_layout.setVerticalSpacing(12)
        filter_layout.setContentsMargins(8, 8, 8, 8)

        # 第一行筛选条件
        # 集合名称
        name_label = QLabel("集合名称:")
        name_label.setStyleSheet("font-size: 14px; color: #333;")
        filter_layout.addWidget(name_label, 0, 0)

        self.name_filter_input = QLineEdit()
        self.name_filter_input.setPlaceholderText("输入名称关键词")
        self.name_filter_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 8px;
                min-width: 180px;
            }
        """)
        filter_layout.addWidget(self.name_filter_input, 0, 1)

        # 状态筛选
        status_label = QLabel("状态:")
        status_label.setStyleSheet("font-size: 14px; color: #333;")
        filter_layout.addWidget(status_label, 0, 2)

        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems(["全部", "启用", "禁用"])
        filter_layout.addWidget(self.status_filter_combo, 0, 3)

        # 数据分类
        category_label = QLabel("分类:")
        category_label.setStyleSheet("font-size: 14px; color: #333;")
        filter_layout.addWidget(category_label, 0, 4)

        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItems(["全部", "视频", "图片", "文本", "音频"])
        filter_layout.addWidget(self.category_filter_combo, 0, 5)

        # 第二行筛选条件 - 日期范围
        date_label = QLabel("创建时间:")
        date_label.setStyleSheet("font-size: 14px; color: #333;")
        filter_layout.addWidget(date_label, 1, 0)

        date_range_layout = QHBoxLayout()
        date_range_layout.setSpacing(8)
        date_range_layout.setContentsMargins(0, 0, 0, 0)

        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setCalendarPopup(True)

        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setCalendarPopup(True)

        date_range_layout.addWidget(self.start_date_edit)
        date_range_layout.addWidget(QLabel("至"))
        date_range_layout.addWidget(self.end_date_edit)
        date_range_layout.addStretch()

        filter_layout.addLayout(date_range_layout, 1, 1, 1, 3)

        # 操作按钮
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.query_button = QPushButton("查询")
        self.query_button.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)

        self.reset_button = QPushButton("重置")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #fff;
                color: #666;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 8px;
                min-width: 80px;
            }
            QPushButton:hover {
                color: #1890ff;
                border-color: #1890ff;
            }
        """)

        button_layout.addWidget(self.query_button)
        button_layout.addWidget(self.reset_button)
        filter_layout.addLayout(button_layout, 0, 6, 2, 1)

        parent_layout.addWidget(filter_frame)

    def setup_action_buttons(self, parent_layout):
        """设置操作按钮区域"""
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        self.insert_button = QPushButton("+ 新建数据集")
        self.insert_button.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)

        self.export_button = QPushButton("导出数据")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #fff;
                color: #666;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                color: #1890ff;
                border-color: #1890ff;
            }
        """)

        action_layout.addWidget(self.insert_button)
        action_layout.addWidget(self.export_button)
        action_layout.addStretch()

        parent_layout.addLayout(action_layout)

    def setup_table_area(self, parent_layout):
        """设置表格区域"""
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-radius: 6px;
                border: 1px solid #eaeaea;
            }
        """)

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # 创建表格
        self.dataset_table = QTableWidget()
        self.dataset_table.setColumnCount(7)
        self.dataset_table.setHorizontalHeaderLabels([
            "集合ID", "名称", "分类", "状态", "内容量", "创建时间", "操作"
        ])

        # 表格设置
        self.dataset_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dataset_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.dataset_table.setAlternatingRowColors(True)
        self.dataset_table.verticalHeader().setVisible(False)
        self.dataset_table.horizontalHeader().setStretchLastSection(False)
        
        # 设置列宽
        self.dataset_table.setColumnWidth(0, 80)   # ID
        self.dataset_table.setColumnWidth(1, 150)  # 名称
        self.dataset_table.setColumnWidth(2, 100)  # 分类
        self.dataset_table.setColumnWidth(3, 80)   # 状态
        self.dataset_table.setColumnWidth(4, 100)  # 内容量
        self.dataset_table.setColumnWidth(5, 150)  # 时间
        self.dataset_table.setColumnWidth(6, 200)  # 操作

        table_layout.addWidget(self.dataset_table)
        parent_layout.addWidget(table_frame, stretch=1)

    def setup_pagination_area(self, parent_layout):
        """设置分页区域"""
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-radius: 6px;
                border: 1px solid #eaeaea;
                padding: 8px;
            }
        """)

        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(8, 8, 8, 8)
        pagination_layout.setSpacing(12)

        # 总条数
        self.total_label = QLabel("共 0 条")
        self.total_label.setStyleSheet("font-size: 14px; color: #666;")

        # 分页控件
        self.prev_btn = QPushButton("上一页")
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #fff;
                color: #666;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                color: #1890ff;
                border-color: #1890ff;
            }
            QPushButton:disabled {
                color: #ccc;
                border-color: #eee;
            }
        """)

        self.next_btn = QPushButton("下一页")
        self.next_btn.setStyleSheet(self.prev_btn.styleSheet())

        # 页码选择
        self.page_combo = QComboBox()
        self.page_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 6px;
                min-width: 80px;
            }
        """)

        # # 每页条数选择
        # self.page_size_combo = QComboBox()
        # self.page_size_combo.addItems(["10", "20", "50", "100"])
        # self.page_size_combo.setCurrentText("10")
        # self.page_size_combo.setStyleSheet(self.page_combo.styleSheet())

        pagination_layout.addWidget(self.total_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_combo)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addWidget(QLabel("每页 10 条"))
        # pagination_layout.addWidget(self.page_size_combo)
        # pagination_layout.addWidget(QLabel("条"))

        parent_layout.addWidget(pagination_frame)

    def current_page(self):
        """获取当前页码"""
        return int(self.page_combo.currentText())

    def update_table(self, datasets, total_items, current_page, total_pages):
        """更新表格数据"""
        self.dataset_table.setRowCount(0)
        self.dataset_table.setRowCount(len(datasets))

        for row, dataset in enumerate(datasets):
            # 填充数据
            self.dataset_table.setItem(row, 0, QTableWidgetItem(str(dataset.get("id", ""))))
            self.dataset_table.setItem(row, 1, QTableWidgetItem(dataset.get("dataset_name", "")))
            self.dataset_table.setItem(row, 2, QTableWidgetItem(dataset.get("dataset_category", "")))
            
            status_item = QTableWidgetItem(dataset.get("status", ""))
            status_item.setTextAlignment(Qt.AlignCenter)
            self.dataset_table.setItem(row, 3, status_item)
            
            size_item = QTableWidgetItem(str(dataset.get("content_size", "")))
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.dataset_table.setItem(row, 4, size_item)
            
            time_item = QTableWidgetItem(dataset.get("created_time", ""))
            time_item.setTextAlignment(Qt.AlignCenter)
            self.dataset_table.setItem(row, 5, time_item)

            # 添加操作按钮
            self.add_action_buttons(row, str(dataset.get("id", "")))

        # 更新分页信息
        self.update_pagination(total_items, current_page, total_pages)

    def add_action_buttons(self, row, dataset_id):
        """为指定行添加操作按钮"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        # 查看按钮
        view_btn = QPushButton("查看")
        view_btn.setStyleSheet("""
            QPushButton {
                background: #e6f7ff;
                color: #1890ff;
                border: 1px solid #91d5ff;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #f0faff;
                border-color: #adc6ff;
            }
        """)
        view_btn.clicked.connect(lambda: self.view_signal.emit(dataset_id))

        # 编辑按钮
        edit_btn = QPushButton("编辑")
        edit_btn.setStyleSheet("""
            QPushButton {
                background: #f6ffed;
                color: #52c41a;
                border: 1px solid #b7eb8f;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #fafff0;
                border-color: #d9f7be;
            }
        """)
        edit_btn.clicked.connect(lambda: self.modify_signal.emit(dataset_id))

        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #fff1f0;
                color: #ff4d4f;
                border: 1px solid #ffa39e;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #fff7f7;
                border-color: #ffccc7;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_signal.emit(dataset_id))

        layout.addWidget(view_btn)
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addStretch()

        self.dataset_table.setCellWidget(row, 6, widget)

    def update_pagination(self, total_items, current_page, total_pages):
        """更新分页控件状态"""
        self.total_label.setText(f"共 {total_items} 条")
        
        # 更新页码下拉框
        self.page_combo.blockSignals(True)
        self.page_combo.clear()
        if total_pages > 0:
            self.page_combo.addItems([str(i) for i in range(1, total_pages + 1)])
            self.page_combo.setCurrentText(str(current_page))
        self.page_combo.blockSignals(False)
        
        # 更新按钮状态
        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

    def show_message(self, title, message):
        """显示信息对话框"""
        QMessageBox.information(self, title, message)

    def show_error(self, title, message):
        """显示错误对话框"""
        QMessageBox.critical(self, title, message)

    def show_warning(self, title, message):
        """显示警告对话框"""
        QMessageBox.warning(self, title, message)

    def ask_confirmation(self, title, message):
        """显示确认对话框"""
        reply = QMessageBox.question(self, title, message, 
                                    QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes