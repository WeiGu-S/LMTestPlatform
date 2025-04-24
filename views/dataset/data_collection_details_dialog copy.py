from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout,QHBoxLayout, QTabWidget, QWidget,
                            QFormLayout, QLabel, QTableWidget, QTableWidgetItem,
                            QHeaderView, QFrame, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
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
        self.init_ui()
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("数据集详情: " + self.data_collection.collection_name)
        self.resize(1000, 600)
        self.setup_style()
        self.setup_ui()
    def setup_style(self):
        """设置整体样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F5;
            }
            QTabWidget::pane {
                border: 1px solid #CCCCCC;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                padding: 10px 25px;
                background-color: #E8E8E8;
                border: 1px solid #CCCCCC;
                border-bottom: none;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background-color: white;
                font-weight: bold;
                color: #007ACC;
            }
            QTableWidget {
                border: 1px solid #CCCCCC;
                gridline-color: #E8E8E8;
                border-radius: 8px;
                margin: 10px;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                padding: 10px;
                border: none;
                border-right: 1px solid #CCCCCC;
                border-bottom: 1px solid #CCCCCC;
                font-size: 13px;
                font-weight: bold;
            }
        """)
    def setup_ui(self):
        """设置UI布局"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20 , 20, 20)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)
        # 创建标签页控件
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        # 添加基本信息标签页
        tab_widget.addTab(self.create_basic_info_tab(), "基本信息")
        
        # 添加数据子项标签页
        tab_widget.addTab(self.create_items_tab(), "数据子项")
    def create_basic_info_tab(self):
        """创建基本信息标签页（优化布局与样式）"""
        tab = QWidget()
        
        # 主布局 - 居中显示内容容器
        main_layout = QGridLayout(tab)
        main_layout.setContentsMargins(24, 16, 24, 16)
        
        # 表单容器样式
        form_container = QWidget()
        form_container.setFixedWidth(600)
        form_container.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #CCCCCC;
        """)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # 字体与样式
        field_font = QFont("Microsoft YaHei", 14)
        label_style = """
            QLabel {
                color: #424242;
                font-weight: 500;
                padding-right: 12px;
                min-width: 110px;
            }
        """

        # 查询数据数量（添加 del_flag=0 条件）
        with DatabaseManager.get_session() as session:
            count = session.query(DataModel).filter(
                DataModel.collection_id == self.data_collection.collection_id,
                DataModel.del_flag == 0
            ).count()

        # 基本信息字段
        info_fields = [
            ("所属项目", lambda: self.data_collection.project_name, False),
            ("数据集名称", lambda: self.data_collection.collection_name, False),
            ("数据数量", lambda: count if count else "0", False),
        ]

        for label, value_getter, _ in info_fields:
            # 标签控件
            label_widget = QLabel(f"{label}:")
            label_widget.setFont(field_font)
            label_widget.setStyleSheet(label_style)
            label_widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # 值控件
            value = str(value_getter()) if value_getter() else "无"
            value_widget = QLabel(value)
            value_widget.setFont(field_font)
            value_widget.setWordWrap(True)
            value_widget.setStyleSheet("color: #333333; padding-left: 4px;")

            # 包装值控件（留出右侧空隙）
            value_container = QWidget()
            h_layout = QHBoxLayout(value_container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.addWidget(value_widget)
            h_layout.addStretch()

            form_layout.addRow(label_widget, value_container)
        
        form_container.setLayout(form_layout)
        main_layout.addWidget(form_container, 0, 0, Qt.AlignCenter)
        main_layout.setRowStretch(0, 1)
        main_layout.setColumnStretch(0, 1)
        
        return tab

    def create_items_tab(self):
        """创建数据子项标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)  # 

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
        layout.addWidget(table_container)

        # 加载数据
        self.update_tab_table()

        return tab

    def update_tab_table(self, datas=None, current_page=1, total_pages=1):
        """更新数据子项表格（完整实现）"""
        # 表格初始化检查
        if not hasattr(self, 'data_table'):
            logger.error("表格控件未初始化")
            return

        try:
            # 清空现有数据
            self.data_table.setRowCount(0)
            with DatabaseManager.get_session() as session:
                datas, total_items, total_pages = DataModel.get_paginated_data(
                        collection_id=int(self.collection_id),
                        session=session,
                        page=current_page,
                        per_page=10
                    )

            print(f"update_tab_table_datas: {datas}")
            
            # 处理空数据状态
            if not datas:
                self.data_table.setRowCount(1)
                self.data_table.setSpan(0, 0, 1, self.data_table.columnCount())
                no_data_item = QTableWidgetItem("暂无数据")
                no_data_item.setFont(QFont("Microsoft YaHei", 12))
                no_data_item.setTextAlignment(Qt.AlignCenter)
                self.data_table.setItem(0, 0, no_data_item)
                # self.update_pagination(0, 1, 1)
                return

            # 设置表格行数
            self.data_table.setRowCount(len(datas))
            # 填充数据行
            for row, data in enumerate(datas):
                # 填充各列数据
                self.data_table.setItem(row, 0, QTableWidgetItem(str(row+1)))  # 序号
                self.data_table.setItem(row, 1, QTableWidgetItem(data.get('data_type', '')))  # 数据类型
                self.data_table.setItem(row, 2, QTableWidgetItem(data.get('context', '')))  # 上下文
                self.data_table.setItem(row, 3, QTableWidgetItem(data.get('question', '')))  # 问题               
                self.data_table.setItem(row, 4, QTableWidgetItem(data.get('answer', '')))  # 答案                
                self.data_table.setItem(row, 5, QTableWidgetItem(data.get('question_type', '')))  # 问题类型
                self.data_table.setItem(row, 6, QTableWidgetItem(data.get('question_label', '')))  # 标签

                # 添加操作按钮（如需）
                # self._add_action_buttons(row_idx, str(item.get('id', '')))

            # 更新分页控件
            # actual_total = len(datasets) if datasets is not None else total_items
            # self.update_pagination(actual_total, current_page, total_pages)

        except Exception as e:
            logger.error(f"更新表格失败: {str(e)}", exc_info=True)
            self.data_table.setRowCount(0)
            error_item = QTableWidgetItem("数据加载失败")
            error_item.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(0, 0, error_item)

