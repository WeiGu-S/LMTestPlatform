from subprocess import call
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QDateEdit, QGridLayout, QFrame,
    QSpacerItem, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt, QDate, Signal, QSize
from PySide6.QtGui import QIcon, QColor, QFont, QPalette, QPixmap
from functools import partial
from sqlalchemy import true
from utils.database import DatabaseManager
from utils.logger import get_logger
from views.dataset import data_collection_details_dialog
from models.enum import ModelType,ConfigType
from models.data_collection_son_model import DataModel

logger = get_logger("model_config_view")

class ModelConfigView(QWidget):
    # 定义所有信号
    query_signal = Signal(dict)      # 查询信号，传递过滤条件
    reset_signal = Signal()          # 重置信号
    model_insert_signal = Signal()         # 新建模型信号
    export_signal = Signal()         # 导出数据信号
    page_changed_signal = Signal(int)    # 页码变化信号
    edit_signal = Signal(str)      # 修改模型信号，传递ID
    view_signal = Signal(str)        # 查看模型信号，传递ID
    call_signal = Signal(str)       # 导入数据信号，传递ID
    delete_signal = Signal(str)       # 删除模型信号，传递ID
    delete_confirm_signal = Signal(str) # 删除确认信号, 传递ID
    prev_page_signal = Signal(int)
    next_page_signal = Signal(int)

    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.per_page = 10
        self.total_pages = 0
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("模型管理")
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
        self.insert_button.clicked.connect(self.model_insert_signal.emit)
        # 导出按钮点击时发射导出信号
        self.export_button.clicked.connect(self.export_signal.emit)
        # 分页控件信号连接
        self.prev_btn.clicked.connect(self.prev_page_signal_emit)
        self.next_btn.clicked.connect(self.next_page_signal_emit)

    def emit_query_signal(self):
        """收集筛选条件并发射查询信号"""
        filters = {
            'model_name': self.model_name_input.text(),
            'model_type': self.model_type_combo.currentData(),
            'config_type': self.config_type_combo.currentData(),
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
        # 模型名称
        project_label = QLabel("模型名称:")
        project_label.setStyleSheet("font-size: 14px; color: #333;")
        filter_layout.addWidget(project_label, 0, 0)

        self.model_name_input = QLineEdit()
        self.model_name_input.setPlaceholderText("请输入模型名称")
        self.model_name_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 8px;
                min-width: 150px;
            }
        """)
        filter_layout.addWidget(self.model_name_input, 0, 1)
        
        combo_style = f"""
            QComboBox {{
                font-size: 14px;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 8px;
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
        # 模型类型
        name_label = QLabel("模型类型:")
        name_label.setStyleSheet("font-size: 14px; color: #333;")
        filter_layout.addWidget(name_label, 0, 2)
        self.model_type_combo = QComboBox()
        self.model_type_combo.setStyleSheet(combo_style)
        self.model_type_combo.addItems(["全部"])
        for item in ModelType:
            self.model_type_combo.addItem(item.display,item.value)
        filter_layout.addWidget(self.model_type_combo, 0, 3)

        # 配置用途
        config_type_label = QLabel("配置用途:")
        config_type_label.setStyleSheet("font-size: 14px; color: #333;")
        filter_layout.addWidget(config_type_label, 0, 4)
        self.config_type_combo = QComboBox()
        self.config_type_combo.setStyleSheet(combo_style)
        self.config_type_combo.addItems(["全部"])
        for item in ConfigType:
            self.config_type_combo.addItem(item.display,item.value)
        filter_layout.addWidget(self.config_type_combo, 0, 5)
        # 模型名称

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

        self.query_button = QPushButton()
        self.query_button.setToolTip("查询")
        self.query_button.setCursor(Qt.PointingHandCursor)
        self.query_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
                height: 40px;
                min-width: 60px;
                image: url(utils/img/search.png);
            }
            QPushButton:pressed {
                padding: 4px;
            }
        """)

        self.reset_button = QPushButton()
        self.reset_button.setToolTip("重置")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
                height: 40px;
                min-width: 60px;
                image: url(utils/img/reset.png);
            }
            QPushButton:pressed {
                padding: 4px;
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

        self.insert_button = QPushButton()
        self.insert_button.setToolTip("新增模型")
        self.insert_button.setCursor(Qt.PointingHandCursor)
        self.insert_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0;
                image: url(utils/img/add.png);
                min-width: 24px;
                min-height: 24px;
            }
            QPushButton:hover {
                text-decoration: 新增模型;
            }
            QPushButton:pressed {
                padding: 4px;
            }
        """)

        self.export_button = QPushButton()
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666;
                border: none;
                border-radius: 4px;
                padding: 0;
                image: url(utils/img/export.png);
                min-width: 24px;
                min-height: 24px;
            }
            QPushButton:hover {
                text-decoration: 导出数据;
            }
            QPushButton:pressed {
                padding: 4px;
            }
        """)

        action_layout.addWidget(self.insert_button)
        action_layout.addStretch()

        parent_layout.addLayout(action_layout)

    def setup_table_area(self, parent_layout):
        """表格区域样式"""
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
        table_layout.setSpacing(6)

        # 创建表格
        self.models_table = QTableWidget()
        self.models_table.setObjectName("dataTable")
        self.models_table.setColumnCount(6)
        self.models_table.setHorizontalHeaderLabels(["序号", "模型名称", "模型类型", "配置用途", "创建时间", "操作"])
        
        # 表头样式
        header = self.models_table.horizontalHeader()
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
                font-size: 14px;
                font-weight: 500;
                qproperty-alignment: AlignCenter;
            }
        """)
        
        # 字体设置
        header_font = QFont("Microsoft YaHei", 14, QFont.Medium)
        header.setFont(header_font)
        
        # 列宽设置（自适应+固定结合）
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 序号
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 模型名称
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # 模型类型
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 配置用途
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # 时间
        
        self.models_table.setColumnWidth(0, 60)   # 序号
        self.models_table.setColumnWidth(2, 100)  # 模型类型
        self.models_table.setColumnWidth(3, 100)  # 内容量
        self.models_table.setColumnWidth(4, 150)  # 时间
        self.models_table.setColumnWidth(5, 200)  # 操作（加宽）

        # 行高设置
        self.models_table.verticalHeader().setDefaultSectionSize(50)
        self.models_table.verticalHeader().setVisible(False)
        # 表格样式设置        
        self.models_table.setStyleSheet("""
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
                padding: 0;
                border-bottom: 1px solid #f0f0f0;
                border-left: 1px solid #f0f0f0;
            }
            QTableWidget#dataTable::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        
        # 通用设置
        self.models_table.setSelectionBehavior(QTableWidget.SelectRows) # 整行选中
        self.models_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 不可编辑
        self.models_table.setAlternatingRowColors(True)  # 交替行颜色
        self.models_table.verticalHeader().setVisible(False)   # 隐藏垂直表头
        self.models_table.verticalHeader().setDefaultSectionSize(44)  # 行高
        
        # 启用平滑滚动
        self.models_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel) 
        self.models_table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)

        table_layout.addWidget(self.models_table)
        parent_layout.addWidget(table_frame, stretch=1)

    def setup_pagination_area(self, parent_layout):
        """设置分页区域"""
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet("""
            QFrame {
                background-color: #fff;
                border-radius: 8px;
                border: 1px solid #eaeaea;
                padding: 4pxpx;
                min-height: 30px;
            }
        """)

        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(8, 4, 8, 4) 
        pagination_layout.setSpacing(8)

        # 总条数显示
        self.total_label = QLabel("共 0 条")
        self.total_label.setStyleSheet("font-size: 14px; color: #555; border: none; padding:6px;")
        pagination_layout.addWidget(self.total_label)
        pagination_layout.addStretch()

        # 上一页按钮
        self.prev_btn = QPushButton()
        self.prev_btn.setToolTip("上一页")
        self.prev_btn.setFixedSize(24, 24)
        self.prev_btn.setStyleSheet(self.page_button_style())
        self.prev_btn.setIcon(QIcon("utils/img/left.png"))
        self.prev_btn.setIconSize(QSize(24, 24))
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        pagination_layout.addWidget(self.prev_btn)

        # 页码按钮容器
        self.page_buttons = []
        self.page_button_container = QHBoxLayout()
        self.page_button_container.setSpacing(4)
        pagination_layout.addLayout(self.page_button_container)

        # 下一页按钮
        self.next_btn = QPushButton()
        self.next_btn.setToolTip("下一页")
        self.next_btn.setFixedSize(24, 24)
        self.next_btn.setStyleSheet(self.page_button_style())
        self.next_btn.setIcon(QIcon("utils/img/right.png"))
        self.next_btn.setIconSize(QSize(24, 24))
        self.next_btn.setCursor(Qt.PointingHandCursor)
        pagination_layout.addWidget(self.next_btn)

        parent_layout.addWidget(pagination_frame)
    
    def page_button_style(self, active=False):
        """设置分页按钮样式"""
        base_style = """
            QPushButton {
                background-color: transparent;
                color: #666;
                border: none;
                border-radius: 4px;
                padding: 0;
                min-width: 24px;
                min-height: 24px;
            }
            QPushButton:disabled {
                color: #ccc;
            }
            QPushButton:pressed {
                padding: 2px 0 0 2px;
            }
        """
        if active:
            return base_style + """
                QPushButton {
                    background-color: #fff;
                    color: #1e90ff;
                    font-weight: bold;
                }
            """
        else:
            return base_style + """
                QPushButton {
                    background-color: #fff;
                }
            """

    def update_table(self, models, total_items, current_page, total_pages):
        """更新表格数据和分页信息"""
         # 先清除所有 cellWidgets（按钮等）
        for row in range(self.models_table.rowCount()):
            for col in range(self.models_table.columnCount()):
                widget = self.models_table.cellWidget(row, col)
                if widget:
                    widget.setParent(None)
        # 处理空数据状态
        if not models:
            self.models_table.setRowCount(1)
            self.models_table.setSpan(0, 0, 1, self.models_table.columnCount())
            no_data_item = QTableWidgetItem("暂无数据")
            no_data_item.setTextAlignment(Qt.AlignCenter)
            self.models_table.setItem(0, 0, no_data_item)

            self.update_pagination(0, 1, 1)
            self.prev_btn.setDisabled(True)
            self.next_btn.setDisabled(True)
            return
        self.current_page = current_page
        self.total_pages = total_pages
        self.models_table.setRowCount(0)  # 清空表格
        self.models_table.setRowCount(len(models))
        with DatabaseManager().get_session() as session:
            for row, model in enumerate(models):
                # 填充数据
                # 第一列默认填充序号，且固定为 1-10
                index_item = QTableWidgetItem(str(row + 1))
                index_item.setTextAlignment(Qt.AlignCenter) # 添加居中对齐
                self.models_table.setItem(row, 0, index_item)

                self.models_table.setItem(row, 1, QTableWidgetItem(model.get("model_name", "")))

                model_type_item = QTableWidgetItem(ModelType.display_of(model.get("model_type", "")))
                self.models_table.setItem(row, 2, model_type_item)
                model_type_item.setTextAlignment(Qt.AlignCenter) # 添加居中对齐
                
                config_type_item = QTableWidgetItem(ConfigType.display_of(model.get("config_type", "")))
                self.models_table.setItem(row, 3, config_type_item)
                config_type_item.setTextAlignment(Qt.AlignCenter) # 添加居中对齐

                time_item = QTableWidgetItem(model.get("created_time", ""))
                time_item.setTextAlignment(Qt.AlignCenter)
                self.models_table.setItem(row, 4, time_item)

                # 添加操作按钮
                self.add_action_buttons(row, str(model.get("config_id", "")))

        # 更新分页信息
        self.total_pages = total_pages
        self.update_pagination(total_items, current_page, total_pages)

    def add_action_buttons(self, row, config_id):
        """添加操作列按钮"""
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
            padding: 0;
            min-width: 30px; /* 增加最小宽度以容纳图标和文字 */
            min-height: 30px; /* 设置合适的最小高度 */
            font-family: 'Microsoft YaHei';
        }
        QPushButton:pressed {
            padding: 2px 3px; /* 轻微调整按压效果 */
        }
        """
        
        # 查看按钮（优化图标显示）
        view_btn = QPushButton()
        view_btn.setToolTip("查看")
        view_btn.setStyleSheet(base_style + """
            background: transparent;
            image: url(utils/img/view.png);
            width: 16px;
            height: 16px;
            border: none;
        """)
        view_btn.setCursor(Qt.PointingHandCursor)
        
        # 编辑按钮（修正尺寸）
        edit_btn = QPushButton()
        edit_btn.setToolTip("编辑模型")
        edit_btn.setStyleSheet(base_style + """
            background: transparent;
            image: url(utils/img/edit.png);
            width: 16px;
            height: 16px;
            border: none;
        """)
        edit_btn.setCursor(Qt.PointingHandCursor)

        # 导入按钮
        call_btn = QPushButton()
        call_btn.setToolTip("导入数据")
        call_btn.setStyleSheet(base_style + """
            background: transparent;
            image: url(utils/img/call.png);
            width: 12px;
            height: 12px;
            border: none;
        """)
        call_btn.setCursor(Qt.PointingHandCursor)
        
        # 删除按钮（确保可见性）
        delete_btn = QPushButton()
        delete_btn.setToolTip("删除模型")
        delete_btn.setStyleSheet(base_style + """
            background: transparent;
            image: url(utils/img/delete.png);
            width: 12px;
            height: 12px;
            border: none;
        """)
        delete_btn.setCursor(Qt.PointingHandCursor)
        
        # 事件绑定
        view_btn.clicked.connect(lambda: self.view_signal.emit(config_id))
        edit_btn.clicked.connect(lambda: self.edit_signal.emit(config_id))
        call_btn.clicked.connect(lambda: self.call_signal.emit(config_id))
        delete_btn.clicked.connect(lambda: self.delete_signal.emit(config_id))
        
        # 添加到布局（保持等间距）
        # button_layout.addWidget(view_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(call_btn)
        button_layout.addWidget(delete_btn)
        
        # 设置到表格
        self.models_table.setCellWidget(row, 5, button_widget)
        
        # 强制列宽设置（双重保障）
        if self.models_table.columnWidth(5) < 220:
            self.models_table.setColumnWidth(5, 220)
        

    def reset_filters(self):
        """重置筛选条件"""
        self.model_name_input.clear()
        self.model_type_combo.setCurrentIndex(0)
        self.config_type_combo.setCurrentIndex(0)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.end_date_edit.setDate(QDate.currentDate())

        self.reset_signal.emit()

    def update_pagination(self, total_items, current_page, total_pages):
        """更新分页信息，确保超过 8 页时固定为 8 个按钮"""
        self.total_label.setText(f"共 {total_items} 条")

        while self.page_button_container.count():
            item = self.page_button_container.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        self.page_buttons.clear()

        if total_pages <= 0:
            return

        # 分页显示规则
        max_buttons = 9  # 固定 8 个分页按钮
        boundary_count = 1  # 首页和尾页显示数量
        around_count = 2    # 当前页前后显示的数量

        # 根据当前页计算需要显示的分页按钮
        def get_pages():
            pages = set()

            # 首页、尾页
            pages.update(range(1, min(boundary_count + 1, total_pages + 1)))
            pages.update(range(max(total_pages - boundary_count + 1, 1), total_pages + 1))

            # 当前页附近
            if total_pages < max_buttons:
                pages.update(range(1, total_pages + 1))
            else:
                if current_page <= around_count + boundary_count:
                    pages.update(range(1, around_count + boundary_count + 4))
                elif current_page >= total_pages - around_count - boundary_count:
                    pages.update(range(total_pages - around_count - boundary_count - 2, total_pages + 1))
                else:
                    pages.update(range(max(current_page - around_count, 1), min(current_page + around_count + 1, total_pages + 1)))

            return sorted(pages)

        page_list = get_pages()

        # 根据总页数和当前页动态计算分页按钮
        final_pages = []
        prev_page = None

        # 插入省略号（'...'）
        for page in page_list:
            if prev_page is not None and page - prev_page > 1:
                if prev_page < current_page:
                    final_pages.append("prev_ellipsis")  # 使用字符串表示省略号，而不是 None
                else:
                    final_pages.append("next_ellipsis")  # 使用字符串表示省略号，而不是 None
                # final_pages.append("...")  # 使用字符串表示省略号，而不是 None
            final_pages.append(page)
            prev_page = page

        # 如果分页按钮数量超过 8，固定展示 8 个按钮
        if len(final_pages) > max_buttons:
            # 保留首页和尾页
            first_pages = final_pages[:2]  # 首页部分
            last_pages = final_pages[-2:]  # 尾页部分

            # 当前页附近的页码
            middle_pages = final_pages[2:-2]

            # 限制为最多 8 个按钮
            middle_pages = middle_pages[:max_buttons - 4]  # 留出两位首页，尾页，和省略号

            final_pages = first_pages + middle_pages + last_pages

        # 创建分页按钮
        for page in final_pages:
            if page == "prev_ellipsis":
                # 省略号
                ellipsis = QPushButton("···")
                ellipsis.setToolTip("更多")
                ellipsis.setStyleSheet(self.page_button_style())
                ellipsis.setFixedSize(24, 24)
                ellipsis.clicked.connect(lambda _, current_page=current_page: self.page_changed_signal.emit(max(1,current_page - 5))) # 前省略号
                self.page_button_container.addWidget(ellipsis)
            elif page == "next_ellipsis":
                # 省略号
                ellipsis = QPushButton("···")
                ellipsis.setToolTip("更多")
                ellipsis.setStyleSheet(self.page_button_style()) 
                ellipsis.setFixedSize(24, 24)
                ellipsis.clicked.connect(lambda _, current_page=current_page: self.page_changed_signal.emit(min(total_pages, current_page + 5))) # 后省略号
                self.page_button_container.addWidget(ellipsis)
            else:
                # 分页按钮
                btn = QPushButton(str(page))
                btn.setFixedSize(24, 24)
                btn.setStyleSheet(self.page_button_style(active=(page == current_page)))
                btn.clicked.connect(lambda _, page=page: self.page_changed_signal.emit(page))
                self.page_buttons.append(btn)
                self.page_button_container.addWidget(btn)

        # 更新上一页/下一页状态
        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

    def show_message(self, type, title, message):
        """显示信息对话框"""
        message_types = {
            'warning': QMessageBox.warning,
            'error': QMessageBox.critical,
            'info': QMessageBox.information
        }
        message_func = message_types.get(type, QMessageBox.information)
        message_func(self, title, message)

    def ask_for_confirmation(self, title, message, config_id=None):
        """显示删除确认对话框"""
        # 创建消息框实例
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIconPixmap(QPixmap("utils/img/info.png").scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        # 配置按钮
        yes_button = msg_box.button(QMessageBox.Yes)
        no_button = msg_box.button(QMessageBox.No)
        yes_button.setText("确认")
        no_button.setText("取消") 
        yes_button.setObjectName("yesButton")
        no_button.setObjectName("noButton")
        
        # 设置消息框样式
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                font-family: "Microsoft YaHei";
                border-radius: 8px;
                padding: 12px;
            }
            QMessageBox QLabel {
                color: #374151;
                font-size: 14px;
                line-height: 1.6;
                padding: 4px;
                min-width: 200px;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                min-height: 32px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: 500;
                padding: 6px 12px;
                margin: 0 4px;
            }
            QPushButton#yesButton {
                background-color: #2196F3;
                color: white;
                border: none;
            }
            QPushButton#yesButton:hover {
                background-color: #1976D2;
            }
            QPushButton#yesButton:pressed {
                background-color: #1565C0;
            }
            QPushButton#noButton {
                background-color: #F5F5F5;
                color: #333333;
                border: 1px solid #E0E0E0;
            }
            QPushButton#noButton:hover {
                background-color: #EEEEEE;
                border-color: #BDBDBD;
            }
            QPushButton#noButton:pressed {
                background-color: #E0E0E0;
            }
        """)

        # 绑定确认信号
        if config_id is not None:
            yes_button.clicked.connect(
                lambda: self.delete_confirm_signal.emit(str(config_id))
            )

        # 显示对话框并返回结果
        return msg_box.exec() == QMessageBox.Yes

    def prev_page_signal_emit(self):
        if self.current_page > 1:
            new_page = self.current_page - 1
            self.page_changed_signal.emit(new_page)
            
    def next_page_signal_emit(self):
        if self.current_page < self.total_pages:
            new_page = self.current_page + 1
            self.page_changed_signal.emit(new_page)
