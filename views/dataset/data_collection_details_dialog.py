from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QHBoxLayout, QTabWidget, QWidget,
                            QFormLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
                            QHeaderView, QFrame, QSpacerItem, QSizePolicy, QLineEdit, QComboBox,QDateEdit)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QFont, QColor, QIntValidator, QIcon
from models import data_collection_son_model
from models.eum import DataType, QuestionLabel, QuestionType
from utils.logger import get_logger
from models.data_collection_model import DataCollectionModel
from models.data_collection_son_model import DataModel
from utils.database import DatabaseManager

logger = get_logger("dataset_details_dialog")

class DataCollectionDetailsDialog(QDialog):
    def __init__(self, data_collection, parent=None, collection_id=None):
        super().__init__(parent)
        self.data_collection = data_collection
        self.collection_id = collection_id
        self.current_page = 1
        self.per_page = 10
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("数据集详情")
        self.resize(1400, 830)  # 增大窗口尺寸
        self.setup_style()
        self.setup_ui()
        
    def setup_style(self):
        """设置整体样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F7FA;
                font-family: "Microsoft YaHei";
            }
            QLabel {
                color: #4B5563;
            }
            QLineEdit, QComboBox {
                border: 1px solid #D1D5DB;
                border-radius: 4px;
                padding: 6px 12px;
                min-height: 32px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3B82F6;
                outline: none;
            }
            QPushButton {
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
                min-height: 36px;
            }
            QPushButton.primary {
                background-color: #3B82F6;
                color: white;
                border: 1px solid #3B82F6;
            }
            QPushButton.primary:hover {
                background-color: #2563EB;
            }
            QPushButton.secondary {
                background-color: white;
                color: #4B5563;
                border: 1px solid #D1D5DB;
            }
            QPushButton.secondary:hover {
                background-color: #F3F4F6;
            }
            QTableWidget {
                border: 1px solid #E1E4E8;
                gridline-color: #E5E7EB;
                border-radius: 8px;
                margin: 0;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                padding: 12px;
                border: none;
                border-right: 1px solid #E5E7EB;
                border-bottom: 1px solid #E5E7EB;
                font-size: 13px;
                font-weight: 600;
                color: #374151;
            }
        """)
        
    def setup_ui(self):
        """设置UI布局"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        self.setLayout(main_layout)
        
        # 1. 顶部信息区域
        top_info_widget = self.create_top_info_widget()
        main_layout.addWidget(top_info_widget)
        # 2. 筛选区域
        filter_widget = self.create_filter_widget()
        main_layout.addWidget(filter_widget)
        # 3. 表格区域
        table_widget = self.create_table_widget()
        main_layout.addWidget(table_widget, 1)  # 添加伸缩因子
        # 4. 分页区域
        pagination_widget = self.create_pagination_widget()
        main_layout.addWidget(pagination_widget)
        # # 5. 按钮区域
        # button_widget = self.create_button_widget()
        # main_layout.addWidget(button_widget)
        
        # 初始加载数据
        self.load_table_data()

    def create_top_info_widget(self):
        """创建顶部信息区域 - 字段名与值同行展示 + 横向布局"""
        top_info_frame = QFrame()
        top_info_frame.setObjectName("topInfoFrame")
        top_info_frame.setStyleSheet("""
            #topInfoFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #eaeaea;
                padding: 2px;
            }
        """)

        main_layout = QVBoxLayout(top_info_frame)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)

        # ===== 顶部标题 =====
        title_label = QLabel("数据集详情")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1F2937;
                border-bottom: 2px solid #3B82F6;
                padding: 0; 
                margin: 0;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(50)

        main_layout.addWidget(title_label)

        # ===== 字段信息区域 =====
        info_card = QWidget()
        info_card.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #eaeaea;
                border-radius: 6px;
                padding: 6px;
            }
        """)

        fields_layout = QHBoxLayout(info_card)
        fields_layout.setContentsMargins(8, 8, 8, 8)
        fields_layout.setSpacing(40)

        fields = [
            ("所属项目", self.data_collection.project_name or "无"),
            ("数据集名称", self.data_collection.collection_name or "无")
        ]

        for label_text, value_text in fields:
            field_container = QWidget()
            field_layout = QHBoxLayout(field_container)
            field_container.setStyleSheet("""
                QWidget {
                    border: none;
                    margin: 0;
                }
            """)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(6)

            label = QLabel(f"{label_text}:")
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #6B7280;
                    font-family: 'Microsoft YaHei';
                    border: none;
                    margin: 0;
                }
            """)

            value = QLabel(value_text)
            value.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #111827;
                    font-family: 'Microsoft YaHei';
                    border: none;
                    padding: 6px;
                }
            """)

            field_layout.addWidget(label)
            field_layout.addWidget(value)
            fields_layout.addWidget(field_container)
            fields_layout.addStretch()

        # fields_layout.addStretch()
        main_layout.addWidget(info_card)

        return top_info_frame
   
    def create_filter_widget(self):
        """创建筛选区域 - 单行布局 & 控件高度统一"""
        filter_frame = QFrame()
        filter_frame.setObjectName("filterFrame")
        filter_frame.setStyleSheet("""
            #filterFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #eaeaea;
                padding: 4px;
            }
        """)

        layout = QHBoxLayout(filter_frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 通用样式定义
        COMMON_HEIGHT = 24
        common_style = f"""
            font-family: 'Microsoft YaHei';
            font-size: 14px;
            color: #333;
            background: white;
            border: 1px solid #dcdfe6;
            border-radius: 4px;
            padding: 6px ;
            min-height: {COMMON_HEIGHT}px;
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

        date_style = f"""
            QDateEdit {{
                {common_style}
                min-width: 120px;
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
                border: none;
            }}
            QDateEdit::down-arrow {{
                image: url(utils/img/down_arrow.png);
                width: 12px;
                height: 12px;
            }}
        """

        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
                min-height: 40px;
                min-width: 40px;
            }
            QPushButton:hover {
                cursor: pointer;
            }
            QPushButton:pressed {
                padding: 4px;
            }
        """

        # 数据分类
        label_style="""
            font-family: 'Microsoft YaHei';
            font-size: 14px;
            color: #6B7280;
            background: white;
            border: none;
            border-radius: 4px;
            padding: 4px ;
            min-height: 24px;
        """
        data_type_label = QLabel("数据分类:")
        data_type_label.setStyleSheet(label_style)
        layout.addWidget(data_type_label)
        self.type_combo = QComboBox()
        self.type_combo.addItem("全部",None)
        for item in DataType:
            self.type_combo.addItem(item.display,item.value)
        self.type_combo.setStyleSheet(combo_style)
        layout.addWidget(self.type_combo)
        layout.addStretch()

        # 题型
        question_type_label = QLabel("题型:")
        question_type_label.setStyleSheet(label_style)
        layout.addWidget(question_type_label)
        self.question_type_combo = QComboBox()
        self.question_type_combo.addItem("全部",None)
        for item in QuestionType:
            self.question_type_combo.addItem(item.display,item.value)
        self.question_type_combo.setStyleSheet(combo_style)
        layout.addWidget(self.question_type_combo)
        layout.addStretch()

        #标签
        question_tag_label = QLabel("标签:")
        question_tag_label.setStyleSheet(label_style)
        layout.addWidget(question_tag_label)
        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.addItem("全部",None)
        for item in QuestionLabel:
            self.tag_filter_combo.addItem(item.display,item.value)
        self.tag_filter_combo.setStyleSheet(combo_style)
        layout.addWidget(self.tag_filter_combo)
        layout.addStretch()

        # 日期范围
        created_time_label = QLabel("创建时间:")
        created_time_label.setStyleSheet(label_style)
        layout.addWidget(created_time_label)
        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setStyleSheet(date_style)
        layout.addWidget(self.start_date_edit)

        layout.addWidget(QLabel("至"))

        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setStyleSheet(date_style)
        layout.addWidget(self.end_date_edit)
        layout.addStretch()

        # 搜索按钮
        search_btn = QPushButton()
        search_btn.setObjectName("searchBtn")
        search_btn.setProperty("class", "primary")
        search_btn.setStyleSheet(button_style + """
            QPushButton {
                image: url(utils/img/search.png);
            }
        """)
        layout.addWidget(search_btn)

        # 重置按钮
        reset_btn = QPushButton()
        reset_btn.setObjectName("resetBtn")
        reset_btn.setProperty("class", "secondary")
        reset_btn.setStyleSheet(button_style + """
            QPushButton {
                image: url(utils/img/reset.png);
            }
        """)
        layout.addWidget(reset_btn)

        # 信号连接
        search_btn.clicked.connect(self.on_search_clicked)
        reset_btn.clicked.connect(self.on_reset_clicked)

        return filter_frame
    
    def create_table_widget(self):
        """创建表格区域"""
        # 创建表格容器
        table_container = QWidget()
        table_container.setMinimumSize(1000, 400)
        table_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                padding: 2px;
                border: none;
            }
        """)

        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(6)

        # 初始化表格
        self.data_table = QTableWidget()
        self.data_table.setObjectName("dataTable")

        self.data_table.setFont(QFont("Microsoft YaHei", 14))
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setColumnCount(7)

        # 调整列的顺序，将问题类型列置于数据分类之后
        headers = ["序号", "数据分类", "题型", "上下文", "问题", "答案", "问题标签"]
        self.data_table.setHorizontalHeaderLabels(headers)
        self.data_table.verticalHeader().setVisible(False)   # 隐藏垂直表头
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁用编辑
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选中
        self.data_table.setWordWrap(False)
        self.data_table.setSelectionMode(QTableWidget.SingleSelection)  # 单选
        self.data_table.verticalHeader().setDefaultSectionSize(44)  # 行高

        # 启用平滑滚动
        self.data_table.setVerticalScrollMode(QTableWidget.ScrollPerPixel) 
        self.data_table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        # 表头设置
        header = self.data_table.horizontalHeader() 
        header.setObjectName("tableHeader")

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
        header.setFont(QFont("Microsoft YaHei", 12, QFont.Medium))

        header.setStretchLastSection(False)  
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Fixed)

        # 表格样式设置        
        self.data_table.setStyleSheet("""
            QTableWidget#dataTable {
                background-color: #ffffff;
                alternate-background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #f0f0f0;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
                padding: 0;
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

        # 设置列宽
        self.data_table.setColumnWidth(0, 80) # 序号列
        self.data_table.setColumnWidth(1, 80)  # 数据类型列
        self.data_table.setColumnWidth(2, 80)  # 问题类型列
        self.data_table.setColumnWidth(3, 200)  # 上下文列
        self.data_table.setColumnWidth(4, 200)  # 问题列
        self.data_table.setColumnWidth(5, 200)  # 答案列
        self.data_table.setColumnWidth(6, 80)  # 标签列

        table_layout.addWidget(self.data_table)

        return table_container

    def create_pagination_widget(self):
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
        self.prev_btn.setFixedSize(24, 24)
        self.prev_btn.setStyleSheet(self.page_button_style())
        self.prev_btn.setIcon(QIcon("utils/img/left.png"))
        self.prev_btn.setIconSize(QSize(24, 24))
        self.prev_btn.clicked.connect(self.on_prev_page)
        pagination_layout.addWidget(self.prev_btn)

        # 页码按钮容器
        self.page_buttons = []
        self.page_button_container = QHBoxLayout()
        self.page_button_container.setSpacing(4)
        pagination_layout.addLayout(self.page_button_container)

        # 下一页按钮
        self.next_btn = QPushButton()
        self.next_btn.setFixedSize(24, 24)
        self.next_btn.setStyleSheet(self.page_button_style())
        self.next_btn.setIcon(QIcon("utils/img/right.png"))
        self.next_btn.setIconSize(QSize(24, 24))
        self.next_btn.clicked.connect(self.on_next_page)
        pagination_layout.addWidget(self.next_btn)

        return pagination_frame
    
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

    def create_button_widget(self):
        """创建按钮区域"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 12px 16px;
            }
        """)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

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

        # 确定按钮
        self.confirm_btn = QPushButton()
        self.confirm_btn.setObjectName("confirmBtn")
        self.confirm_btn.setProperty("class", "primary")
        self.confirm_btn.setStyleSheet(button_style + """
            QPushButton {
                image: url(utils/img/confirm.png);
            }
        """)
        # 取消按钮
        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setProperty("class", "secondary")
        self.cancel_btn.setStyleSheet(button_style + """
            QPushButton {
                image: url(utils/img/cancel.png);
            }
        """)
        # 添加到布局
        layout.addStretch(1)
        layout.addWidget(self.confirm_btn)
        layout.addWidget(self.cancel_btn)
        layout.addStretch(1)
        # 连接信号
        # self.confirm_btn.clicked.connect(self.on_confirm)
        self.cancel_btn.clicked.connect(self.reject)
        return widget
    
    def load_table_data(self):
        """加载表格数据"""
        try:
            # 清空现有数据
            self.data_table.setRowCount(0)
            
            # 获取筛选条件
            filters = {
                "data_type": self.type_combo.currentData(),
                "question_type": self.question_type_combo.currentData(),
                "tag": self.tag_filter_combo.currentData(),
                "page": self.current_page,
                "per_page": self.per_page
            }
            
            self.data_table.setRowCount(0)
            with DatabaseManager.get_session() as session:
                datas, total_items, total_pages = DataModel.get_paginated_data(
                        collection_id=int(self.collection_id),
                        session=session,
                        page=self.current_page,
                        per_page=10,
                        filters=filters
                    )

            # 处理空数据状态
            if not datas:
                self.data_table.setRowCount(1)
                self.data_table.setSpan(0, 0, 1, self.data_table.columnCount())
                no_data_item = QTableWidgetItem("暂无数据")
                no_data_item.setTextAlignment(Qt.AlignCenter)
                self.data_table.setItem(0, 0, no_data_item)

                self.update_pagination_info(0, 1, 1)
                self.prev_btn.setDisabled(True)
                self.next_btn.setDisabled(True)
                return

            # 设置表格行数
            self.data_table.setRowCount(len(datas))
            
            # 填充数据行
            for row, data in enumerate(datas):
                # 序号列
                # index_item = QTableWidgetItem(str((self.current_page-1)*self.per_page + row+1))
                index_item = QTableWidgetItem(str(row+1))
                index_item.setTextAlignment(Qt.AlignCenter)
                
                # 数据类型列
                data_type_item = QTableWidgetItem(DataType.display_of(data.get('data_type', '')))
                data_type_item.setTextAlignment(Qt.AlignCenter)
                
                # 问题类型列
                question_type_item = QTableWidgetItem(QuestionType.display_of(data.get('question_type', '')))
                question_type_item.setTextAlignment(Qt.AlignCenter)
                
                # 上下文列（限制长度并添加省略号）
                context = data.get('context', '')
                if len(context) > 100:
                    context = context[:100] + "..."
                context_item = QTableWidgetItem(context)
                context_item.setToolTip(context)  # 设置鼠标悬停提示
                
                # 问题列
                question = data.get('question', '')
                if len(question) > 100:
                    question = question[:100] + "..."
                question_item = QTableWidgetItem(question)
                question_item.setToolTip(question)
                
                # 答案列
                answer = data.get('answer', '')
                if len(answer) > 100:
                    answer = answer[:100] + "..."
                answer_item = QTableWidgetItem(answer)
                answer_item.setToolTip(answer)
                
                # 标签列
                label_item = QTableWidgetItem(QuestionLabel.display_of(data.get('question_label', '')))
                label_item.setTextAlignment(Qt.AlignCenter)
                
                # 设置所有项
                self.data_table.setItem(row, 0, index_item)
                self.data_table.setItem(row, 1, data_type_item)
                self.data_table.setItem(row, 2, question_type_item)
                self.data_table.setItem(row, 3, context_item)
                self.data_table.setItem(row, 4, question_item)
                self.data_table.setItem(row, 5, answer_item)
                self.data_table.setItem(row, 6, label_item)

            # 更新分页信息
            self.update_pagination_info(total_items, self.current_page, total_pages)

        except Exception as e:
            logger.error(f"加载表格数据失败: {str(e)}", exc_info=True)
            self.data_table.setRowCount(1)
            error_item = QTableWidgetItem("数据加载失败")
            error_item.setFont(QFont("Microsoft YaHei", 12))
            error_item.setTextAlignment(Qt.AlignCenter)
            error_item.setForeground(QColor("#EF4444"))
            self.data_table.setItem(0, 0, error_item)
            self.update_pagination_info(0, 1, 1)
    
    def update_pagination_info(self, total_items, current_page, total_pages):
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
                ellipsis.setStyleSheet(self.page_button_style())
                ellipsis.setFixedSize(24, 24)
                ellipsis.clicked.connect(lambda _, current_page=current_page: self.on_page_button_clicked(max(1,current_page - 5))) # 前省略号
                self.page_button_container.addWidget(ellipsis)
            elif page == "next_ellipsis":
                # 省略号
                ellipsis = QPushButton("···")
                ellipsis.setStyleSheet(self.page_button_style()) # Replace with your actual image path
                ellipsis.setFixedSize(24, 24)
                ellipsis.clicked.connect(lambda _, current_page=current_page: self.on_page_button_clicked(min(total_pages, current_page + 5))) # 后省略号
                self.page_button_container.addWidget(ellipsis)
            else:
                # 分页按钮
                btn = QPushButton(str(page))
                btn.setFixedSize(24, 24)
                btn.setStyleSheet(self.page_button_style(active=(page == current_page)))
                btn.clicked.connect(lambda _, page=page: self.on_page_button_clicked(page))
                self.page_buttons.append(btn)
                self.page_button_container.addWidget(btn)

        # 更新上一页/下一页状态
        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

    def on_search_clicked(self):
        """搜索按钮点击事件"""
        # 根据筛选条件加载数据
        self.current_page = 1
        self.load_table_data()

    
    def on_reset_clicked(self):
        """重置按钮点击事件"""
        self.type_combo.setCurrentIndex(0)
        self.question_type_combo.setCurrentIndex(0)
        self.tag_filter_combo.setCurrentIndex(0)
        self.current_page = 1
        self.load_table_data()
    
    def on_prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_table_data()
    
    def on_next_page(self):
        """下一页"""
        self.current_page += 1
        self.load_table_data()
    
    def on_page_changed(self, page):
        """页码改变事件"""
        self.current_page = page
        self.load_table_data()

    def on_page_button_clicked(self, page):
        """页码按钮点击事件"""
        self.current_page = page
        self.load_table_data()

    def on_export_clicked(self):
        """导出数据"""
        # TODO: 实现导出功能
        print("导出数据")