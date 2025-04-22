from sqlite3 import connect
from tkinter import YES
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QDateEdit, QGridLayout, QFrame,
    QSpacerItem, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QIcon, QColor, QFont, QPalette
from functools import partial

from sqlalchemy import true
from utils.logger import get_logger
from views.dataset import dataset_details_dialog

logger = get_logger("dataset_view")

class DatasetView(QWidget):
    # 定义所有信号
    query_signal = Signal(dict)      # 查询信号，传递过滤条件
    reset_signal = Signal()          # 重置信号
    insert_signal = Signal()         # 新建数据集信号
    export_signal = Signal()         # 导出数据信号
    page_changed_signal = Signal(int)    # 页码变化信号
    page_size_changed_signal = Signal(int)  # 每页条数变化信号
    edit_signal = Signal(str)      # 修改数据集信号，传递ID
    view_signal = Signal(str)        # 查看数据集信号，传递ID
    import_signal = Signal(str)       # 导入数据信号，传递ID
    delete_signal = Signal(str)       # 删除数据集信号，传递ID
    delete_confirm_signal = Signal(str) # 删除确认信号, 传递ID

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
        self.reset_button.clicked.connect(self.reset_filters)
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
                border-radius: 8px;
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
        self.name_filter_input.setPlaceholderText("请输入集合名称")
        self.name_filter_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 8px;
                min-width: 150px;
            }
        """)
        filter_layout.addWidget(self.name_filter_input, 0, 1)

        # 状态筛选
        status_label = QLabel("状态:")
        status_label.setStyleSheet("font-size: 14px; color: #333;")
        filter_layout.addWidget(status_label, 0, 2)

        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems(["全部", "启用", "停用"])
        filter_layout.addWidget(self.status_filter_combo, 0, 3)
        self.status_filter_combo.setStyleSheet("""
            QComboBox {
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                color: #333;
                background: white;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 6px 12px 6px 8px;
                min-width: 80px;
                selection-background-color: #e6f7ff;
            }
            QComboBox:hover {
                border-color: #c0c4cc;
            }
            QComboBox:focus {
                border-color: #1890ff;
                box-shadow: 0 0 3px rgba(24, 144, 255, 0.3);
            }
            QComboBox:on {
                background: #f5f5f5;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
                border: none;
                padding: 0;
            }
            QComboBox::down-arrow {
                image: url(utils/img/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)

        # 数据分类
        category_label = QLabel("分类:")
        category_label.setStyleSheet("font-size: 14px; color: #333;")
        filter_layout.addWidget(category_label, 0, 4)

        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItems(["全部", "视频", "图片", "文本", "音频"])
        filter_layout.addWidget(self.category_filter_combo, 0, 5)
        self.category_filter_combo.setStyleSheet(self.status_filter_combo.styleSheet())

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
        self.start_date_edit.setStyleSheet("""
            QDateEdit {
                font-family: 'Microsoft YaHei';
                font-size: 14px;
                color: #333;
                background: white;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 6px 12px 6px 8px;
                min-width: 100px;
            }
            QDateEdit:hover {
                border-color: #c0c4cc;
            }
            QDateEdit:focus {
                border-color: #1890ff;
                box-shadow: 0 0 3px rgba(24, 144, 255, 0.3);
            }
            QDateEdit:on {
                background: #f5f5f5;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
                border: none;
                padding: 0;
            }
            QDateEdit::down-arrow {
                image: url(utils/img/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)

        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setStyleSheet(self.start_date_edit.styleSheet())

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
            QPushButton:pressed {
                background-color: #096dd9;
                border-color: #096dd9;
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
            QPushButton:pressed {
                background-color: #f5f5f5;
                border-color: #d9d9d9;
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
            QPushButton:pressed {
                background-color: #096dd9;
                border-color: #096dd9;
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
            QPushButton:pressed {
                background-color: #f5f5f5;
                border-color: #d9d9d9;
            }
        """)

        action_layout.addWidget(self.insert_button)
        action_layout.addWidget(self.export_button)
        action_layout.addStretch()

        parent_layout.addLayout(action_layout)

    def setup_table_area(self, parent_layout):
        """优化后的表格区域样式"""
        # 表格容器
        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_frame.setStyleSheet("""
            #tableFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 0px;
            }
            QTableWidget#dataTable {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                selection-background-color: #e6f7ff;
                selection-color: #333;
                gridline-color: #e0e0e0;
                alternate-background-color: #f5f5f5;
            }
        """)

        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # 创建表格
        self.dataset_table = QTableWidget()
        self.dataset_table.setObjectName("dataTable")
        self.dataset_table.setColumnCount(7)
        self.dataset_table.setHorizontalHeaderLabels([
            "序号", "名称", "分类", "状态", "内容量", "创建时间", "操作"
        ])
        
        # 表头样式
        header = self.dataset_table.horizontalHeader()
        header.setObjectName("tableHeader")
        
        # 综合样式设置
        header.setStyleSheet("""
            QHeaderView#tableHeader {
                background-color: transparent;
                border-top left right: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QHeaderView#tableHeader::section {
                background-color: #f5f5f5;
                color: #333333;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                border-left: 1px solid #e0e0e0;
                padding: 10px 12px;
                font-family: "Microsoft YaHei";
                font-size: 13px;
                font-weight: 500;
                qproperty-alignment: AlignCenter;
            }
        """)
        
        # 字体设置
        header_font = QFont("Microsoft YaHei", 12, QFont.Medium)
        header.setFont(header_font)
        
        # 列宽设置（自适应+固定结合）
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 序号
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 名称自适应
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 分类
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 状态
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # 内容量
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # 时间
        
        self.dataset_table.setColumnWidth(0, 80)   # 序号
        self.dataset_table.setColumnWidth(2, 80)  # 分类
        self.dataset_table.setColumnWidth(3, 80)   # 状态
        self.dataset_table.setColumnWidth(4, 80)  # 内容量
        self.dataset_table.setColumnWidth(5, 150)  # 时间
        self.dataset_table.setColumnWidth(6, 200)  # 操作（加宽）
        # self.dataset_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)  # 操作列固定宽度
        # self.dataset_table.setColumnWidth(6, 200)  # 明确设置操作列宽度

        # 行高设置
        self.dataset_table.verticalHeader().setDefaultSectionSize(50)
        self.dataset_table.verticalHeader().setVisible(False)
        # 表格样式设置        
        self.dataset_table.setStyleSheet("""
            QTableWidget#dataTable {
                background-color: #ffffff;
                alternate-background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #f0f0f0;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
            }
            QTableWidget#dataTable::item {
                padding: 10px 12px;
                border-bottom: 1px solid #f0f0f0;
                border-left: 1px solid #f0f0f0;
            }
            QTableWidget#dataTable::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)

        
        # 通用设置
        self.dataset_table.setSelectionBehavior(QTableWidget.SelectRows) #
        self.dataset_table.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.dataset_table.setAlternatingRowColors(True) 
        self.dataset_table.verticalHeader().setVisible(False)  
        self.dataset_table.verticalHeader().setDefaultSectionSize(42)  # 行高
        
        # 启用平滑滚动
        self.dataset_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel) 
        self.dataset_table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)

        table_layout.addWidget(self.dataset_table)
        parent_layout.addWidget(table_frame, stretch=1)

    def setup_pagination_area(self, parent_layout):
        """设置分页区域"""
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-radius: 8px;
                border: 1px solid #eaeaea;
                padding: 8px;
            }
        """)

        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(8, 8, 8, 8)
        pagination_layout.setSpacing(12)

        # 总条数
        self.total_label = QLabel("共 0 条")
        self.total_label.setStyleSheet("font-size: 14px; color: #666;border: none;")

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
            QComboBox:hover {
                border-color: #c0c4cc;
            }
            QComboxBox:focus {
                border-color: #1890ff;
                box-shadow: 0 0 3px rgba(24, 144, 255, 0.3);
            }
            QComboBox:on {
                background: #f5f5f5;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
                border: none;
            }
        """)

        self.page_szie = QLabel("每页 10 条")
        self.page_szie.setStyleSheet(self.total_label.styleSheet()  )

        pagination_layout.addWidget(self.total_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_combo)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_szie)


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
            # self.dataset_table.setItem(row, 0, QTableWidgetItem(str(dataset.get("id", ""))))
            # 第一列默认填充序号，且固定为 1-10
            self.dataset_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
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
        """最终优化的操作列按钮（解决所有显示问题）"""
        # 创建按钮容器（使用QWidget更轻量）
        button_widget = QWidget()
        button_widget.setStyleSheet("background: transparent;")

        # 使用水平布局（带间距控制）
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(5, 2, 5, 2)  # 适当的内边距
        button_layout.setSpacing(6)  # 按钮间距
        
        # 基础按钮样式（调整尺寸和内边距）
        base_style = """
        QPushButton {
            border-radius: 3px;
            padding: 1px 2px; /* 调整内边距 */
            font-size: 12px;
            min-width: 40px; /* 增加最小宽度以容纳图标和文字 */
            max-width: 50px; /* 增加最大宽度 */
            min-height: 12px; /* 设置合适的最小高度 */
            font-family: 'Microsoft YaHei';
            text-align: center; /* 确保文本居中 */
        }
        QPushButton:pressed {
            padding: 2px 3px; /* 轻微调整按压效果 */
            margin: 1px 1px 0 1px;
        }
        """
        
        # 查看按钮（优化图标显示）
        view_btn = QPushButton("查看")
        # view_btn.setIcon(QIcon(":/icons/view.png"))
        view_btn.setStyleSheet(base_style + """
            background: #e6f7ff;
            color: #1890ff;
            border-color: #91d5ff;
        """)
        view_btn.setCursor(Qt.PointingHandCursor)
        
        # 编辑按钮（修正尺寸）
        edit_btn = QPushButton("编辑")
        # edit_btn.setIcon(QIcon(":/icons/edit.png"))
        edit_btn.setStyleSheet(base_style + """
            background: #f6ffed;
            color: #52c41a;
            border-color: #b7eb8f;
        """)
        edit_btn.setCursor(Qt.PointingHandCursor)

        # 导入按钮
        import_btn = QPushButton("导入")
        # import_btn.setIcon(QIcon(":/icons/import.png"))
        import_btn.setStyleSheet(base_style + """
            background: #fffbe6;
            color: #faad14;
            border-color: #ffe58f;
        """)
        import_btn.setCursor(Qt.PointingHandCursor)
        
        # 删除按钮（确保可见性）
        delete_btn = QPushButton("删除")
        # delete_btn.setIcon(QIcon(":/icons/delete.png"))
        delete_btn.setStyleSheet(base_style + """
            background: #fff1f0;
            color: #ff4d4f;
            border-color: #ffa39e;
        """)
        delete_btn.setCursor(Qt.PointingHandCursor)
        
        # 事件绑定
        view_btn.clicked.connect(lambda: self.view_signal.emit(dataset_id))
        edit_btn.clicked.connect(lambda: self.edit_signal.emit(dataset_id))
        import_btn.clicked.connect(lambda: self.import_signal.emit(dataset_id))
        delete_btn.clicked.connect(lambda: self.delete_signal.emit(dataset_id))
        
        # 添加到布局（保持等间距）
        button_layout.addWidget(view_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(import_btn)
        button_layout.addWidget(delete_btn)
        
        # 设置到表格（关键修复步骤）
        self.dataset_table.setCellWidget(row, 6, button_widget)
        
        # 强制列宽设置（双重保障）
        self.dataset_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        if self.dataset_table.columnWidth(6) < 220:
            self.dataset_table.setColumnWidth(6, 220)
        

    def reset_filters(self):
        """重置筛选条件"""
        self.name_filter_input.clear()
        self.category_filter_combo.setCurrentIndex(0)
        self.status_filter_combo.setCurrentIndex(0)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.end_date_edit.setDate(QDate.currentDate())

        self.reset_signal.emit()



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

    def ask_for_confirmation(self, title, message, dataset_id=None):
        """显示删除确认对话框（修正信号连接问题）"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # 添加自定义样式
        msg_box.setStyleSheet("""
            QMessageBox {
                font-family: "Microsoft YaHei";
                min-width: 300px;
                min-height: 150px;
            }
        """)
        
        # 连接确认信号
        if dataset_id is not None:
            yes_button = msg_box.button(QMessageBox.Yes)
            yes_button.clicked.connect(lambda: self.delete_confirm_signal.emit(str(dataset_id)))
        
        return msg_box.exec() == QMessageBox.Yes

    