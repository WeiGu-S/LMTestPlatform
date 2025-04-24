from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QHBoxLayout, QTabWidget, QWidget,
                            QFormLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
                            QHeaderView, QFrame, QSpacerItem, QSizePolicy, QLineEdit, QComboBox,QDateEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor,QIntValidator
from models import dataset_son_model
from utils.logger import get_logger
from models.data_collection_model import DataCollectionModel
from models.dataset_son_model import DataModel
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
        self.resize(1400, 900)  # 增大窗口尺寸
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
        # 5. 按钮区域
        button_widget = self.create_button_widget()
        main_layout.addWidget(button_widget)
        
        # 初始加载数据
        self.load_table_data()
        
    def create_top_info_widget(self):
        """创建顶部信息区域 - 字段名与值同行展示 + 横向布局"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 16px;
                border: 1px solid #E5E7EB;
            }
        """)
        
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # 标题区域
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("数据集详情")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1F2937;
                padding-bottom: 4px;
                border-bottom: 2px solid #3B82F6;
            }
        """)
        title_label.setFixedHeight(30)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addWidget(title_widget)
        
        # 信息卡片区域（字段名 + 值 在同一行）
        info_card = QWidget()
        info_card.setStyleSheet("""
            QWidget {
                background-color: #F9FAFB;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        
        h_layout = QHBoxLayout(info_card)
        h_layout.setContentsMargins(12, 12, 12, 12)
        h_layout.setSpacing(40)  # 字段之间的间距
        
        fields = [
            ("项目名称", self.data_collection.project_name or "无"),
            ("数据集名称", self.data_collection.collection_name or "无")
        ]
        
        field_style = """
            QLabel {
                font-size: 14px;
                font-family: 'Microsoft YaHei';
            }
        """
        label_color = "color: #6B7280;"  # 灰色（标签）
        value_color = "color: #111827;"  # 深色（值）

        for label_text, value_text in fields:
            field_layout = QHBoxLayout()
            field_layout.setSpacing(4)

            label = QLabel(f"{label_text}:")
            label.setStyleSheet(field_style + label_color)
            value = QLabel(value_text)
            value.setStyleSheet(field_style + value_color)

            field_layout.addWidget(label)
            field_layout.addWidget(value)            
            field_container = QWidget()
            field_container.setLayout(field_layout)
            h_layout.addWidget(field_container)
            h_layout.addStretch()

        h_layout.addStretch()
        main_layout.addWidget(info_card)

        return widget
    # def create_top_info_widget(self):
    #     """创建顶部信息区域"""
    #     widget = QWidget()
    #     widget.setStyleSheet("""
    #         background-color: white;
    #         border-radius: 8px;
    #         padding: 0;
    #     """)
        
    #     layout = QVBoxLayout(widget)
    #     layout.setContentsMargins(0, 0, 0, 0)
    #     layout.setSpacing(12)
        
    #     # 标题
    #     title_label = QLabel("数据集详情")
    #     title_label.setStyleSheet("""
    #         QLabel {
    #             font-size: 18px;
    #             font-weight: bold;
    #             color: #1F2937;
    #             padding-bottom: 8px;
    #         }
    #     """)
    #     layout.addWidget(title_label)
        
    #     # 基本信息网格布局
    #     grid_layout = QGridLayout()
    #     grid_layout.setContentsMargins(0, 0, 0, 0)
    #     grid_layout.setHorizontalSpacing(40)
    #     grid_layout.setVerticalSpacing(12)
        
    #     # 项目名称
    #     project_label = QLabel("所属项目:")
    #     project_value = QLabel(self.data_collection.project_name or "无")
        
    #     # 数据集名称
    #     dataset_label = QLabel("数据集名称:")
    #     dataset_value = QLabel(self.data_collection.collection_name or "无")
        
    #     # 设置字体样式
    #     label_style = "color: #6B7280; font-weight: 500;"
    #     value_style = "color: #111827;"
        
    #     for label in [project_label, dataset_label]:
    #         label.setStyleSheet(label_style)
    #         label.setFont(QFont("Microsoft YaHei", 11))
            
    #     for value in [project_value, dataset_value]:
    #         value.setStyleSheet(value_style)
    #         value.setFont(QFont("Microsoft YaHei", 11))
        
    #     # 添加到网格布局
    #     grid_layout.addWidget(project_label, 0, 0)
    #     grid_layout.addWidget(project_value, 0, 1)
    #     grid_layout.addWidget(dataset_label, 0, 2)
    #     grid_layout.addWidget(dataset_value, 0, 3)
        
    #     layout.addLayout(grid_layout)
        
    #     return widget
    
    def create_filter_widget(self):
        """创建筛选区域"""
        widget = QWidget()
        widget.setStyleSheet("""
            background-color: white;
            border-radius: 8px;
            padding: 16px;
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 数据类型筛选
        type_label = QLabel("数据类型:")
        type_combo = QComboBox()
        type_combo.addItem("全部", "")
        type_combo.addItem("文本", "1")
        type_combo.addItem("图片", "2")
        type_combo.addItem("音频", "3")
        type_combo.addItem("视频", "4")
        
        # 问题类型筛选
        question_type_label = QLabel("问题类型:")
        question_type_combo = QComboBox()
        question_type_combo.addItem("全部", "")
        question_type_combo.addItem("选择题", "1")
        question_type_combo.addItem("填空题", "2")
        question_type_combo.addItem("问答题", "3")
        
        
        # 日期范围
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("yyyy-MM-dd")
        self.date_start.setDate(QDate.currentDate().addMonths(-1))

        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("yyyy-MM-dd")
        self.date_end.setDate(QDate.currentDate())
        
        # 搜索按钮
        search_btn = QPushButton("搜索")
        search_btn.setObjectName("searchBtn")
        search_btn.setProperty("class", "primary")
        
        # 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.setObjectName("resetBtn")
        reset_btn.setProperty("class", "secondary")
        
        # 添加控件到布局
        layout.addWidget(type_label)
        layout.addWidget(type_combo)
        layout.addWidget(question_type_label)
        layout.addWidget(question_type_combo)
        layout.addStretch(1)
        layout.addWidget(search_btn)
        layout.addWidget(reset_btn)
        
        # 保存引用
        self.type_combo = type_combo
        self.question_type_combo = question_type_combo
        self.search_btn = search_btn
        self.reset_btn = reset_btn
        
        # 连接信号
        search_btn.clicked.connect(self.on_search_clicked)
        reset_btn.clicked.connect(self.on_reset_clicked)
        
        return widget
    
    def create_table_widget(self):
        """创建表格区域"""
        # 创建表格容器
        table_container = QWidget()
        table_container.setMinimumSize(1000, 400)
        table_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                padding: 0;
                border: none;
            }
        """)

        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # 初始化表格
        self.data_table = QTableWidget()
        self.data_table.setObjectName("dataTable")

        self.data_table.setFont(QFont("Microsoft YaHei", 14))
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setColumnCount(7)

        headers = ["序号", "数据类型", "上下文", "问题", "答案", "问题类型", "标签"]
        self.data_table.setHorizontalHeaderLabels(headers)
        self.data_table.verticalHeader().setVisible(False)   # 隐藏垂直表头
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁用编辑
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选中
        self.data_table.setSelectionMode(QTableWidget.SingleSelection)  # 单选
        self.data_table.verticalHeader().setDefaultSectionSize(42)  # 行高

        # 表头设置
        header = self.data_table.horizontalHeader() 
        header.setFont(QFont("Microsoft YaHei", 12, QFont.Medium))
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
                border-top: 1px solid #e0e0e0;
                border-right: 1px solid #e0e0e0;
                padding: 0;
                font-family: "Microsoft YaHei";
                font-size: 14pt;
                font-weight: 500;
                qproperty-alignment: AlignCenter;
            }
        """)

        header.setStretchLastSection(False)  
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
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
        self.data_table.setColumnWidth(0, 40) # 序号列
        self.data_table.setColumnWidth(1, 80)  # 数据类型列
        self.data_table.setColumnWidth(2, 200)  # 上下文列
        self.data_table.setColumnWidth(3, 200)  # 问题列
        self.data_table.setColumnWidth(4, 200)  # 答案列
        self.data_table.setColumnWidth(5, 80)  # 问题类型
        self.data_table.setColumnWidth(6, 80)  # 标签列

        table_layout.addWidget(self.data_table)

        return table_container

    def create_pagination_widget(self):
        """创建分页区域"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
                padding: 12px 16px;
            }
            QLabel {
                color: #6B7280;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # 分页信息
        self.page_info_label = QLabel("共 0 条数据，第 0/0 页")  # 初始化为默认值
        self.page_info_label.setFont(QFont("Microsoft YaHei", 10))
        
        # 分页按钮
        self.prev_page_btn = QPushButton("上一页")
        self.prev_page_btn.setProperty("class", "secondary")
        self.prev_page_btn.setDisabled(True)
        
        self.next_page_btn = QPushButton("下一页")
        self.next_page_btn.setProperty("class", "secondary")
        self.next_page_btn.setDisabled(True)
        
        # 页码输入
        self.page_input = QLineEdit()
        self.page_input.setPlaceholderText("页码")
        self.page_input.setFixedWidth(60)
        self.page_input.setValidator(QIntValidator(1, 9999))
        
        self.go_page_btn = QPushButton("跳转")
        self.go_page_btn.setProperty("class", "secondary")
        
        # 添加到布局
        layout.addWidget(self.page_info_label)
        layout.addStretch(1)
        layout.addWidget(self.prev_page_btn)
        layout.addWidget(self.next_page_btn)
        layout.addWidget(QLabel("跳转到:"))
        layout.addWidget(self.page_input)
        layout.addWidget(self.go_page_btn)
        
        # 连接信号
        self.prev_page_btn.clicked.connect(self.on_prev_page)
        self.next_page_btn.clicked.connect(self.on_next_page)
        self.go_page_btn.clicked.connect(self.on_go_page)
        
        return widget

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

        # 确定按钮
        self.confirm_btn = QPushButton("确定")
        self.confirm_btn.setObjectName("confirmBtn")
        self.confirm_btn.setProperty("class", "primary")
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setProperty("class", "secondary")
        # 添加到布局
        layout.addStretch(1)
        layout.addWidget(self.confirm_btn)
        layout.addWidget(self.cancel_btn)
        # 连接信号
        # self.confirm_btn.clicked.connect(self.on_confirm)
        # self.cancel_btn.clicked.connect(self.on_cancel)
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
                "page": self.current_page,
                "per_page": self.per_page
            }
            
            self.data_table.setRowCount(0)
            with DatabaseManager.get_session() as session:
                datas, total_items, total_pages = DataModel.get_paginated_data(
                        collection_id=int(self.collection_id),
                        session=session,
                        page=self.current_page,
                        per_page=10
                    )

            # 处理空数据状态
            if not datas:
                self.data_table.setRowCount(1)
                self.data_table.setSpan(0, 0, 1, self.data_table.columnCount())
                no_data_item = QTableWidgetItem("暂无数据")
                no_data_item.setTextAlignment(Qt.AlignCenter)
                self.data_table.setItem(0, 0, no_data_item)

                self.update_pagination_info(0, 1, 1)
                self.prev_page_btn.setDisabled(True)
                self.next_page_btn.setDisabled(True)
                return

            # 设置表格行数
            self.data_table.setRowCount(len(datas))
            
            # 填充数据行
            for row, data in enumerate(datas):
                # 序号列
                index_item = QTableWidgetItem(str((self.current_page-1)*self.per_page + row+1))
                index_item.setTextAlignment(Qt.AlignCenter)
                
                # 数据类型列
                data_type_item = QTableWidgetItem(data.get('data_type', ''))
                data_type_item.setTextAlignment(Qt.AlignCenter)
                
                # 上下文列（限制长度并添加省略号）
                context = data.get('context', '')
                if len(context) > 100:
                    context = context[:100] + "..."
                context_item = QTableWidgetItem(context)
                
                # 问题列
                question = data.get('question', '')
                if len(question) > 100:
                    question = question[:100] + "..."
                question_item = QTableWidgetItem(question)
                
                # 答案列
                answer = data.get('answer', '')
                if len(answer) > 100:
                    answer = answer[:100] + "..."
                answer_item = QTableWidgetItem(answer)
                
                # 问题类型列
                question_type_item = QTableWidgetItem(data.get('question_type', ''))
                question_type_item.setTextAlignment(Qt.AlignCenter)
                
                # 标签列
                label_item = QTableWidgetItem(data.get('question_label', ''))
                label_item.setTextAlignment(Qt.AlignCenter)
                
                # 设置所有项
                self.data_table.setItem(row, 0, index_item)
                self.data_table.setItem(row, 1, data_type_item)
                self.data_table.setItem(row, 2, context_item)
                self.data_table.setItem(row, 3, question_item)
                self.data_table.setItem(row, 4, answer_item)
                self.data_table.setItem(row, 5, question_type_item)
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
        """更新分页信息"""
        self.page_info_label.setText(f"共 {total_items} 条数据，当前第 {current_page}/{total_pages} 页")
        
        # 更新按钮状态
        self.prev_page_btn.setDisabled(current_page <= 1)
        self.next_page_btn.setDisabled(current_page >= total_pages)
        
        # 清空页码输入
        self.page_input.clear()
    
    def on_search_clicked(self):
        """搜索按钮点击事件"""
        self.current_page = 1
        self.load_table_data()
    
    def on_reset_clicked(self):
        """重置按钮点击事件"""
        self.type_combo.setCurrentIndex(0)
        self.question_type_combo.setCurrentIndex(0)
        self.search_input.clear()
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
    
    def on_go_page(self):
        """跳转到指定页"""
        page = self.page_input.text()
        if page and page.isdigit():
            page_num = int(page)
            if page_num >= 1:
                self.current_page = page_num
                self.load_table_data()
    
    def on_export_clicked(self):
        """导出数据"""
        # TODO: 实现导出功能
        print("导出数据")