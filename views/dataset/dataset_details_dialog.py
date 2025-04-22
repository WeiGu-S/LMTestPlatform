from PySide6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout,QHBoxLayout, QTabWidget, QWidget,
                            QFormLayout, QLabel, QTableWidget, QTableWidgetItem,
                            QHeaderView, QFrame, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from utils.logger import get_logger
from models.dataset_model import DatasetCategory, DatasetModel, DatasetStatus
logger = get_logger("dataset_details_dialog")
class DatasetDetailsDialog(QDialog):
    def __init__(self, dataset, parent=None):
        super().__init__(parent)
        self.dataset = dataset
        self.init_ui()
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("数据集详情: " + self.dataset.dataset_name)
        self.resize(800, 600)
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
                margin: 10px;
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
        main_layout.setContentsMargins(30, 30, 30, 30)
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
        """创建基本信息标签页（优化行间距和备注处理）"""
        tab = QWidget()
        
        # 主布局 - 使用网格布局确保完美居中
        main_layout = QGridLayout(tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建表单容器（固定宽度+圆角阴影）
        form_container = QWidget()
        form_container.setFixedWidth(650)  # 适当加宽容器
        form_container.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
            padding: 25px 35px;
            border: none;
        """)
        
        # 表单布局 - 紧凑型设计
        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)  # 行间距从15px减小到12px
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # 统一字体配置
        field_font = QFont("Microsoft YaHei", 15)  # 适当增大字体
        label_style = """
            QLabel {
                color: #424242;
                font-weight: 500;
                padding-right: 12px;
                min-width: 90px;
            }
        """
        value_style = """
            QLabel {
                color: #616161;
                background: #FAFAFA;
                padding: 6px 10px;
                min-width: 280px;
                max-height: 36px;
                border-radius: 8px;
                border: 1px solid #EEEEEE;
            }
        """
        remark_style = """
            QLabel {
                color: #616161;
                background: #FAFAFA;
                padding: 12px;
                min-width: 280px;
                max-width: 280px;
                border-radius: 6px;
                border: 1px solid #EEEEEE;
            }
        """

        # 添加基本信息字段
        info_fields = [
            ("数据集名称", lambda: self.dataset.dataset_name, False),
            ("类型", lambda: self.dataset.dataset_category.value, False),
            ("状态", lambda: self.dataset.status.value, False),
            ("内容量", lambda: str(self.dataset.content_size), False),
            ("备注", lambda: self.dataset.remark if self.dataset.remark else "无", True)  # 特殊处理备注
        ]

        for label, value_getter, is_remark in info_fields:
            # 创建标签
            label_widget = QLabel(f"{label}:")
            label_widget.setFont(field_font)
            label_widget.setStyleSheet(label_style)
            label_widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # 创建值控件
            value = str(value_getter()) if value_getter() else "无"
            value_widget = QLabel(value)
            value_widget.setFont(field_font)
            value_widget.setWordWrap(True)
            
            # 备注行特殊样式处理
            if is_remark:
                value_widget.setStyleSheet(remark_style)
                value_widget.setWordWrap(True)
                # 调整备注的高度
                value_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                value_widget.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                value_widget.setMinimumHeight(80)  # 为备注提供足够高度
                value_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            else:
                value_widget.setStyleSheet(value_style)
                value_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # 使用水平布局包装值控件
            value_container = QWidget()
            h_layout = QHBoxLayout(value_container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            h_layout.addWidget(value_widget)
            h_layout.addStretch()  # 右侧留白
            
            # 添加到表单
            form_layout.addRow(label_widget, value_container)
        
        form_container.setLayout(form_layout)
        
        # 将容器放入主布局中心
        main_layout.addWidget(form_container, 0, 0, Qt.AlignCenter)
        main_layout.setRowStretch(0, 1)
        main_layout.setColumnStretch(0, 1)
        
        return tab

    def create_items_tab(self):
        """创建数据子项标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        # 创建表格容器
        table_container = QWidget()
        table_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(10, 10, 10, 10)

        # 创建表格
        table = QTableWidget()
        table.setFont(QFont("Microsoft YaHei", 11))
        table_layout.addWidget(table)

        # 设置表格属性
        headers = ["ID", "标题", "答案", "状态", "标签", "创建时间"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # 设置表格列宽和样式
        header = table.horizontalHeader()
        header.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        header.setDefaultAlignment(Qt.AlignCenter)
        
        # 设置各列的宽度比例
        width_ratios = [1, 2, 2, 1, 1, 1.5]
        total_ratio = sum(width_ratios)
        for i, ratio in enumerate(width_ratios):
            header.setSectionResizeMode(i, QHeaderView.Fixed)
            table.setColumnWidth(i, int(700 * ratio / total_ratio))

        # 设置表格样式
        table.setAlternatingRowColors(True)
        table.setShowGrid(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #E8E8E8;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #E8E8E8;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
        """)

        # 填充数据
        items = getattr(self.dataset, "items", [])
        table.setRowCount(len(items))

        for row, item in enumerate(items):
            columns = [
                str(item.get("id", "")),
                item.get("name", ""),
                item.get("answer", ""),
                item.get("status", ""),
                item.get("tags", ""),
                item.get("created_time", "")
            ]
            for col, value in enumerate(columns):
                table_item = QTableWidgetItem(value)
                table_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, table_item)

        layout.addWidget(table_container)
        return tab