from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QDateEdit, QGridLayout, QFrame,
    QSpacerItem, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon, QColor, QFont, QPalette
from contrrlers.dataset_controller import DatasetController

class DatasetView(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # # 顶部标题区域（高度较小）
        # title_label = QLabel("数据集管理")
        # title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #222; padding: 8px 0 4px 0;")
        # main_layout.addWidget(title_label)
        # 
        # 筛选区域
        filter_frame = QFrame()
        filter_frame.setObjectName("filterFrame")
        filter_frame.setStyleSheet("""
            #filterFrame { 
                background-color: #ffffff; 
                border-radius: 4px; 
                padding: 12px; 
                border: 1px solid #eaeaea; 
                box-shadow: 0 2px 6px rgba(0,0,0,0.05); 
            }
        """)

        # 使用网格布局，设置合理的间距
        filter_layout = QGridLayout(filter_frame)
        filter_layout.setHorizontalSpacing(12)  # 增加水平间距
        filter_layout.setVerticalSpacing(12)
        filter_layout.setContentsMargins(12, 12, 12, 12)  # 统一边距

        # 第一行筛选控件
        # 集合名称
        name_label = QLabel("集合名称")
        name_label.setStyleSheet("""
            font-size: 14px; 
            color: #333333; 
            font-weight: 500;
            min-width: 60px;
        """)
        filter_layout.addWidget(name_label, 0, 0)

        self.name_filter_input = QLineEdit()
        self.name_filter_input.setPlaceholderText("请输入集合名称")
        self.name_filter_input.setStyleSheet("""
            QLineEdit { 
                border: 1px solid #dcdfe6; 
                border-radius: 4px; 
                padding: 6px 12px; 
                background-color: #ffffff; 
                font-size: 14px; 
                color: #606266; 
                min-width: 160px;
            } 
            QLineEdit:focus { 
                border-color: #409eff; 
            }
        """)
        self.name_filter_input.setFixedHeight(32)
        filter_layout.addWidget(self.name_filter_input, 0, 1)

        # 状态
        status_label = QLabel("状态")
        status_label.setStyleSheet("""
            font-size: 14px; 
            color: #333333; 
            font-weight: 500;
            min-width: 40px;
        """)
        filter_layout.addWidget(status_label, 0, 2)

        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems(["全部", "启用", "禁用"])
        self.status_filter_combo.setStyleSheet("""
            QComboBox { 
                border: 1px solid #dcdfe6; 
                border-radius: 4px; 
                padding: 6px 12px 6px 8px; 
                background-color: #ffffff; 
                font-size: 14px; 
                color: #606266;
                min-width: 80px;
            } 
            QComboBox:hover { 
                border-color: #c0c4cc; 
            } 
            QComboBox:focus { 
                border-color: #409eff; 
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 24px;
                border-radius: 0 4px 4px 0;
            }
            QComboBox::down-arrow {
                image: url(utils/img/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.status_filter_combo.setFixedHeight(32)
        filter_layout.addWidget(self.status_filter_combo, 0, 3)

        # 数据分类
        category_label = QLabel("数据分类")
        category_label.setStyleSheet("""
            font-size: 14px; 
            color: #333333; 
            font-weight: 500;
            min-width: 60px;
        """)
        filter_layout.addWidget(category_label, 0, 4)

        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItems(["全部", "视频", "图片", "文本", "音频"])
        self.category_filter_combo.setStyleSheet(self.status_filter_combo.styleSheet())  # 复用样式
        self.category_filter_combo.setFixedHeight(32)
        filter_layout.addWidget(self.category_filter_combo, 0, 5)

        # 第二行筛选 - 日期范围
        date_label = QLabel("创建时间")
        date_label.setStyleSheet("""
            font-size: 14px; 
            color: #333333; 
            font-weight: 500;
            min-width: 60px;
        """)
        filter_layout.addWidget(date_label, 1, 0)

        # 日期范围控件
        date_range_layout = QHBoxLayout()
        date_range_layout.setSpacing(8)  # 减小日期控件之间的间距
        date_range_layout.setContentsMargins(0, 0, 0, 0)

        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setStyleSheet("""
            QDateEdit { 
                border: 1px solid #dcdfe6; 
                border-radius: 4px; 
                padding: 6px 12px 6px 8px; 
                background-color: #ffffff; 
                font-size: 14px; 
                color: #606266; 
                min-width: 120px;
            } 
            QDateEdit:hover { 
                border-color: #c0c4cc; 
            } 
            QDateEdit:focus { 
                border-color: #409eff; 
            }
            QDateEdit::drop-down {
                width: 24px;
                background-color: transparent;
                subcontrol-position: right center;
                border-radius: 0 4px 4px 0;
            }
            QDateEdit::down-arrow {
                image: url(utils/img/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.start_date_edit.setFixedHeight(32)

        to_label = QLabel("至")
        to_label.setStyleSheet("""
            QLabel { 
                font-size: 14px; 
                color: #333333; 
                padding: 0 4px;
                background: transparent;
            }
        """)
        to_label.setAlignment(Qt.AlignCenter)

        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setStyleSheet(self.start_date_edit.styleSheet())  # 复用样式
        self.end_date_edit.setFixedHeight(32)

        date_range_layout.addWidget(self.start_date_edit)
        date_range_layout.addWidget(to_label)
        date_range_layout.addWidget(self.end_date_edit)
        date_range_layout.addStretch()

        filter_layout.addLayout(date_range_layout, 1, 1, 1, 5)

        # 查询/重置按钮 (垂直排列)
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
                padding: 6px 12px; 
                font-size: 14px; 
                font-weight: 500; 
                min-width: 80px;
            } 
            QPushButton:hover { 
                background-color: #40a9ff; 
            } 
            QPushButton:pressed { 
                background-color: #096dd9; 
            }
        """)
        self.query_button.setFixedHeight(32)

        self.reset_button = QPushButton("重置")
        self.reset_button.setStyleSheet("""
            QPushButton { 
                background-color: #ffffff; 
                color: #606266; 
                border: 1px solid #dcdfe6; 
                border-radius: 4px; 
                padding: 6px 12px; 
                font-size: 14px; 
                min-width: 80px;
            } 
            QPushButton:hover { 
                background-color: #f4f4f5; 
                color: #409eff; 
                border-color: #c6e2ff; 
            }
        """)
        self.reset_button.setFixedHeight(32)

        button_layout.addWidget(self.query_button)
        button_layout.addWidget(self.reset_button)
        filter_layout.addLayout(button_layout, 0, 6, 2, 1)

        main_layout.addWidget(filter_frame)

        # 操作按钮区域 (新建/导出)
        action_button_layout = QHBoxLayout()
        self.new_button = QPushButton("+ 新建")
        self.new_button.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 6px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
        """)
        self.new_button.setFixedHeight(32)
        self.new_button.setMinimumWidth(80)
        
        self.export_button = QPushButton("导出")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #606266;
                border: 1px solid #dcdfe6;
                border-radius: 6px;
                padding: 6px 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f4f4f5;
                color: #409eff;
                border-color: #c6e2ff;
            }
        """)
        self.export_button.setFixedHeight(32)
        self.export_button.setMinimumWidth(80)
        
        action_button_layout.addWidget(self.new_button)
        action_button_layout.addWidget(self.export_button)
        action_button_layout.addStretch()
        main_layout.addLayout(action_button_layout)

        # 表格区域
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame { 
                background: transparent; 
                border: none;
                padding: 0;
                max-height: 500px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # 创建表格
        self.dataset_table = QTableWidget()
        self.dataset_table.setColumnCount(7)  # 编号, 名称, 分类, 状态, 内容量, 时间, 操作
        self.dataset_table.setHorizontalHeaderLabels(["集合编号", "集合名称", "数据分类", "状态", "内容量", "时间", "操作"])

        # 表格基本设置
        self.dataset_table.setMinimumHeight(420)
        self.dataset_table.setMaximumHeight(500)
        self.dataset_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.dataset_table.verticalHeader().setVisible(False)
        self.dataset_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dataset_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.dataset_table.setAlternatingRowColors(True)
        self.dataset_table.setSortingEnabled(True)

        # 列宽设置
        self.dataset_table.setColumnWidth(0, 100)  # 集合编号
        self.dataset_table.setColumnWidth(1, 150)  # 集合名称
        self.dataset_table.setColumnWidth(2, 100)  # 数据分类
        self.dataset_table.setColumnWidth(3, 80)   # 状态
        self.dataset_table.setColumnWidth(4, 100)  # 内容量
        self.dataset_table.setColumnWidth(5, 150)  # 时间
        self.dataset_table.setColumnWidth(6, 120)  # 操作

        # 表格样式
        self.dataset_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ebeef5;
                border-radius: 4px;
                background-color: #ffffff;
                gridline-color: #ebeef5;
                outline: none;
                alternate-background-color: #fafafa;
            }
            
            /* 表头样式 */
            QHeaderView::section {
                background-color: #f5f7fa;
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #ebeef5;
                border-right: 1px solid #ebeef5;
                font-weight: 500;
                font-size: 14px;
                color: #606266;
            }
            
            /* 表头最后一项特殊处理 */
            QHeaderView::section:last {
                border-right: none;
            }
            
            /* 单元格样式 */
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #ebeef5;
                font-size: 14px;
                color: #606266;
            }
            
            /* 选中行样式 */
            QTableWidget::item:selected {
                background-color: #ecf5ff;
                color: #606266;
            }
            
            /* 悬停行样式 */
            QTableWidget::item:hover {
                background-color: #f5f7fa;
            }
            
            /* 操作列按钮样式 */
            QPushButton {
                min-width: 60px;
                max-width: 60px;
                padding: 6px 8px;
                font-size: 12px;
                border-radius: 4px;
                margin: 2px;
            }
            
            /* 滚动条样式 */
            QScrollBar:vertical {
                border: none;
                background: #f5f7fa;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #c0c4cc;
                min-height: 20px;
                border-radius: 4px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # 设置表头对齐方式
        for i in range(self.dataset_table.columnCount()):
            header_item = self.dataset_table.horizontalHeaderItem(i)
            if i in [4, 5]:  # 内容量和时间列居中
                header_item.setTextAlignment(Qt.AlignCenter)
            else:
                header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        table_layout.addWidget(self.dataset_table)
        main_layout.addWidget(table_frame)

       # 分页控件区域
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet("""
            QFrame { 
                background: #ffffff; 
                border-radius: 6px; 
                border: 1px solid #eaeaea;
                padding: 0;
                max-height: 36px;
                margin: 0;
            }
        """)
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(12, 4, 12, 4)  # 调整边距
        pagination_layout.setSpacing(8)  # 控件间距

        # 总条数标签
        self.total_items_label = QLabel("共 0 条")
        self.total_items_label.setStyleSheet("""
            QLabel {
                font-size: 14px; 
                border: none;
                color: #333333; 
                padding: 0 ;
                min-width: 80px;
            }
        """)
        pagination_layout.addWidget(self.total_items_label)

        # 上一页按钮
        self.prev_button = QPushButton("<")
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #333333;
                border:none;
                padding: 0;
                margin: 0;
                font-size: 16px; 
                min-width: 24px;
                min-height: 24px;
            }
            QPushButton:hover {
                color: #409eff;
                border-color: #c6e2ff;
                background-color: #f5f9ff;
            }
            QPushButton:pressed {
                background-color: #ecf5ff;
            }
            QPushButton:disabled {
                color: #c0c4cc;
                background-color: #f4f4f5;
                border-color: #e4e7ed;
            }
        """)
        self.prev_button.setCursor(Qt.PointingHandCursor)
        pagination_layout.addWidget(self.prev_button)

        # 页码选择器
        self.page_combo = QComboBox()
        self.page_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 0 0 0 6px ;
                background-color: #ffffff;
                font-size: 14px;
                color: #606266;
                min-width: 26px;
                max-width: 80px;
                min-height: 24px;
            }
            QComboBox:hover {
                border-color: #c0c4cc;
            }
            QComboBox:focus {
                border-color: #409eff;
            }
            QComboBox::drop-down {
                width: 24px;
                subcontrol-position: right center;     
                background-color: transparent;
                border-radius: 0 4px 0 4px;       
            }
            QComboBox::down-arrow {
                image: url(utils/img/down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #dcdfe6;
                selection-background-color: #f5f9ff;
                selection-color: #409eff;
                min-width: 80px;
            }
        """)
        pagination_layout.addWidget(self.page_combo)

        # 下一页按钮
        self.next_button = QPushButton(">")
        self.next_button.setStyleSheet(self.prev_button.styleSheet())  # 复用样式
        self.next_button.setCursor(Qt.PointingHandCursor)
        pagination_layout.addWidget(self.next_button)

        # 每页条数标签
        self.page_size_label = QLabel("10 条/页")
        self.page_size_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333333;
                padding: 0 80px 0 0;
                margin: 0 80px 0 0;
                text-align: center;
                min-width: 80px;
                border: none;
            }
        """)
        pagination_layout.addWidget(self.page_size_label)

        pagination_layout.addStretch()
        main_layout.addWidget(pagination_frame)

    def show_import_dialog(self):
        """显示导入数据集对话框"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("CSV文件 (*.csv);;Excel文件 (*.xlsx);;所有文件 (*)")

        if file_dialog.exec():
            return file_dialog.selectedFiles()
        return []

    def show_export_dialog(self):
        """显示导出数据集对话框"""
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("CSV文件 (*.csv);;Excel文件 (*.xlsx)")

        if file_dialog.exec():
            return file_dialog.selectedFiles()[0]
        return ""

    def show_error(self, message):
        """显示错误消息"""
        QMessageBox.critical(self, "错误", message)

    def update_table(self, datasets, total_items, current_page, total_pages):
        """更新数据集表格和分页控件"""
        self.dataset_table.setRowCount(0) # 清空表格
        self.dataset_table.setRowCount(len(datasets))

        for row, dataset in enumerate(datasets):
            # 假设 dataset 是一个字典或对象，包含所需字段
            # 注意：字段名需要与 controller 和 model 对应
            self.dataset_table.setItem(row, 0, QTableWidgetItem(str(dataset.get("id", ""))))
            self.dataset_table.setItem(row, 1, QTableWidgetItem(dataset.get("dataset_name", "")))
            self.dataset_table.setItem(row, 2, QTableWidgetItem(dataset.get("dataset_category", "")))
            self.dataset_table.setItem(row, 3, QTableWidgetItem(dataset.get("status", "")))   
            self.dataset_table.setItem(row, 4, QTableWidgetItem(str(dataset.get("content_size", "")))) # 假设有内容量字段
            self.dataset_table.setItem(row, 5, QTableWidgetItem(dataset.get("created_time", "")))

            # 操作列 (示例：添加修改和查看按钮)
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(15)  # 增加按钮之间的间距
            
            modify_button = QPushButton("修改")
            view_button = QPushButton("查看")
            
            modify_button.setStyleSheet("""
                QPushButton {
                    color: #1890ff; 
                    background: none; 
                    border: none;
                    font-size: 14px;
                    text-decoration: none;
                }
                QPushButton:hover {
                    color: #40a9ff;
                    text-decoration: underline;
                }
            """) # 链接样式
            
            view_button.setStyleSheet("""
                QPushButton {
                    color: #1890ff; 
                    background: none; 
                    border: none;
                    font-size: 14px;
                    text-decoration: none;
                }
                QPushButton:hover {
                    color: #40a9ff;
                    text-decoration: underline;
                }
            """)   # 链接样式
            
            # TODO: 连接按钮信号到 controller 的槽函数
            modify_button.clicked.connect(lambda checked, r=row: self.controller.modify_item(r))
            view_button.clicked.connect(lambda checked, r=row: self.controller.view_item(r))
            
            action_layout.addWidget(modify_button)
            action_layout.addWidget(view_button)
            action_layout.addStretch()
            self.dataset_table.setCellWidget(row, 6, action_widget)

        # 调整列宽
        self.dataset_table.resizeColumnsToContents()
        self.dataset_table.horizontalHeader().setStretchLastSection(True)

        # 更新分页控件
        self.total_items_label.setText(f"共 {total_items} 条")
        self.prev_button.setEnabled(current_page > 1)
        self.next_button.setEnabled(current_page < total_pages)

        self.page_combo.blockSignals(True) # 防止更新时触发信号
        self.page_combo.clear()
        if total_pages > 0:
            self.page_combo.addItems([str(i) for i in range(1, total_pages + 1)])
            self.page_combo.setCurrentText(str(current_page))
        self.page_combo.setEnabled(total_pages > 1)
        self.page_combo.blockSignals(False)

    def get_selected_ids(self):
        """获取选中的数据集ID"""
        selected_ids = []
        selected_rows = set()
        for item in self.dataset_table.selectedItems():
            selected_rows.add(item.row())

        for row in selected_rows:
            id_item = self.dataset_table.item(row, 0) # ID 在第 0 列
            if id_item:
                try:
                    selected_ids.append(int(id_item.text()))
                except ValueError:
                    print(f"Warning: Could not convert ID '{id_item.text()}' to int at row {row}") # 添加日志或错误处理
        return selected_ids # 不再去重，因为基于行选择，ID应该是唯一的