from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QComboBox, QDateEdit, QGridLayout, QFrame,
    QSpacerItem, QSizePolicy, QHeaderView
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon, QColor, QFont, QPalette

class DatasetView(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 顶部标题区域（减小高度）
        title_label = QLabel("数据集管理")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #222; padding: 8px 0 4px 0;")
        main_layout.addWidget(title_label)
        # 筛选区域
        filter_frame = QFrame()
        filter_frame.setObjectName("filterFrame")
        filter_frame.setStyleSheet("#filterFrame { background-color: #ffffff; border-radius: 8px; padding: 8px 10px 8px 10px; border: 1px solid #eaeaea; box-shadow: 0 2px 6px rgba(0,0,0,0.05); }")
        filter_layout = QGridLayout(filter_frame)
        filter_layout.setSpacing(4)
        # 第一行筛选
        name_label = QLabel("集合名称")
        name_label.setStyleSheet("font-size: 14px; color: #333333; font-weight: 500;")
        filter_layout.addWidget(name_label, 0, 0)
        self.name_filter_input = QLineEdit()
        self.name_filter_input.setPlaceholderText("请输入集合名称")
        self.name_filter_input.setStyleSheet("QLineEdit { border: 1px solid #dcdfe6; border-radius: 4px; padding: 6px 8px; background-color: #ffffff; font-size: 14px; color: #606266; min-width: 160px; max-width: 180px; } QLineEdit:focus { border-color: #409eff; }")
        self.name_filter_input.setMinimumHeight(28)
        self.name_filter_input.setMaximumWidth(180)
        filter_layout.addWidget(self.name_filter_input, 0, 1)
        status_label = QLabel("状态")
        status_label.setStyleSheet("font-size: 14px; color: #333333; font-weight: 500;")
        filter_layout.addWidget(status_label, 0, 2)
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems(["全部", "启用", "禁用"])
        self.status_filter_combo.setStyleSheet("QComboBox { border: 1px solid #dcdfe6; border-radius: 4px; padding: 6px 8px; background-color: #ffffff; font-size: 14px; color: #606266; min-width: 70px; max-width: 80px; } QComboBox:hover { border-color: #c0c4cc; } QComboBox:focus { border-color: #409eff; }")
        self.status_filter_combo.setMinimumHeight(28)
        self.status_filter_combo.setMaximumWidth(80)
        filter_layout.addWidget(self.status_filter_combo, 0, 3)
        category_label = QLabel("数据分类")
        category_label.setStyleSheet("font-size: 14px; color: #333333; font-weight: 500;")
        filter_layout.addWidget(category_label, 0, 4)
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItems(["全部", "视频", "图片", "文本", "音频"])
        self.category_filter_combo.setStyleSheet("QComboBox { border: 1px solid #dcdfe6; border-radius: 4px; padding: 6px 8px; background-color: #ffffff; font-size: 14px; color: #606266; min-width: 70px; max-width: 80px; } QComboBox:hover { border-color: #c0c4cc; } QComboBox:focus { border-color: #409eff; }")
        self.category_filter_combo.setMinimumHeight(28)
        self.category_filter_combo.setMaximumWidth(80)
        filter_layout.addWidget(self.category_filter_combo, 0, 5)
        # 第二行筛选
        date_label = QLabel("创建时间")
        date_label.setStyleSheet("font-size: 14px; color: #333333; font-weight: 500;")
        filter_layout.addWidget(date_label, 1, 0)
        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setStyleSheet("QDateEdit { border: 1px solid #dcdfe6; border-radius: 4px; padding: 6px 8px; background-color: #ffffff; font-size: 14px; color: #606266; } QDateEdit:hover { border-color: #c0c4cc; } QDateEdit:focus { border-color: #409eff; }")
        self.start_date_edit.setMinimumHeight(28)
        filter_layout.addWidget(self.start_date_edit, 1, 1)
        to_label = QLabel("至")
        to_label.setStyleSheet("font-size: 14px; color: #333333; font-weight: 500;")
        to_label.setAlignment(Qt.AlignCenter)
        filter_layout.addWidget(to_label, 1, 2, Qt.AlignCenter)
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setStyleSheet("QDateEdit { border: 1px solid #dcdfe6; border-radius: 4px; padding: 6px 8px; background-color: #ffffff; font-size: 14px; color: #606266; } QDateEdit:hover { border-color: #c0c4cc; } QDateEdit:focus { border-color: #409eff; }")
        self.end_date_edit.setMinimumHeight(28)
        filter_layout.addWidget(self.end_date_edit, 1, 3)
        # 查询/重置按钮区域（分两行）
        query_reset_layout = QVBoxLayout()
        self.query_button = QPushButton("查询")
        self.query_button.setStyleSheet("QPushButton { background-color: #1890ff; color: white; border: none; border-radius: 4px; padding: 4px 0; font-size: 14px; font-weight: 500; min-width: 70px; } QPushButton:hover { background-color: #40a9ff; } QPushButton:pressed { background-color: #096dd9; }")
        self.query_button.setMinimumHeight(24)
        self.reset_button = QPushButton("重置")
        self.reset_button.setStyleSheet("QPushButton { background-color: #ffffff; color: #606266; border: 1px solid #dcdfe6; border-radius: 4px; padding: 4px 0; font-size: 14px; min-width: 70px; } QPushButton:hover { background-color: #f4f4f5; color: #409eff; border-color: #c6e2ff; }")
        self.reset_button.setMinimumHeight(24)
        query_reset_layout.addWidget(self.query_button)
        query_reset_layout.addWidget(self.reset_button)
        filter_layout.addLayout(query_reset_layout, 0, 8, 2, 1)
        main_layout.addWidget(filter_frame)
        # 表格区域（提升高度，合理分配列宽）
        table_frame = QFrame()
        table_frame.setStyleSheet("QFrame { background: #fff; border-radius: 8px; border: 1px solid #eaeaea; }")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        self.dataset_table = QTableWidget()
        self.dataset_table.setStyleSheet("QTableWidget { border: none; font-size: 14px; } QHeaderView::section { background: #fafafa; font-weight: 500; font-size: 14px; border: none; height: 36px; } QTableWidget::item { border-bottom: 1px solid #f0f0f0; }")
        self.dataset_table.setMinimumHeight(420)
        self.dataset_table.setMaximumHeight(500)
        self.dataset_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.dataset_table.setColumnWidth(0, 90)
        self.dataset_table.setColumnWidth(1, 120)
        self.dataset_table.setColumnWidth(2, 90)
        self.dataset_table.setColumnWidth(3, 70)
        self.dataset_table.setColumnWidth(4, 90)
        self.dataset_table.setColumnWidth(5, 120)
        self.dataset_table.setColumnWidth(6, 120)
        self.dataset_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.dataset_table.verticalHeader().setVisible(False)
        self.dataset_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dataset_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.dataset_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.dataset_table)
        main_layout.addWidget(table_frame)
        # 分页区域（减小高度，优化样式）
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet("QFrame { background: transparent; border: none; }")
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(2)
        self.prev_button = QPushButton("上一页")
        self.prev_button.setStyleSheet("QPushButton { min-width: 54px; min-height: 22px; font-size: 13px; border-radius: 4px; background: #f5f5f5; border: 1px solid #e0e0e0; } QPushButton:disabled { color: #bbb; background: #fafafa; }")
        self.next_button = QPushButton("下一页")
        self.next_button.setStyleSheet("QPushButton { min-width: 54px; min-height: 22px; font-size: 13px; border-radius: 4px; background: #f5f5f5; border: 1px solid #e0e0e0; } QPushButton:disabled { color: #bbb; background: #fafafa; }")
        self.page_combo = QComboBox()
        self.page_combo.setStyleSheet("QComboBox { min-width: 54px; min-height: 22px; font-size: 13px; border-radius: 4px; background: #fff; border: 1px solid #e0e0e0; }")
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10", "20", "50"])
        self.page_size_combo.setStyleSheet("QComboBox { min-width: 54px; min-height: 22px; font-size: 13px; border-radius: 4px; background: #fff; border: 1px solid #e0e0e0; }")
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_combo)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addWidget(QLabel("每页显示"))
        pagination_layout.addWidget(self.page_size_combo)
        pagination_layout.addStretch()
        main_layout.addWidget(pagination_frame)

        # 操作按钮区域 (新建/导出)
        action_button_layout = QHBoxLayout()
        self.new_button = QPushButton("+ 新建")
        self.new_button.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
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
        self.new_button.setFixedHeight(36)
        self.new_button.setMinimumWidth(90)
        
        self.export_button = QPushButton("导出")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #606266;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f4f4f5;
                color: #409eff;
                border-color: #c6e2ff;
            }
        """)
        self.export_button.setFixedHeight(36)
        self.export_button.setMinimumWidth(90)
        
        action_button_layout.addWidget(self.new_button)
        action_button_layout.addWidget(self.export_button)

        action_button_layout.addStretch()
        main_layout.addLayout(action_button_layout)

        # 数据集表格
        self.dataset_table = QTableWidget()
        # 更新列数和表头以匹配图片
        self.dataset_table.setColumnCount(7) # 编号, 名称, 分类, 状态, 内容量, 时间, 操作
        self.dataset_table.setHorizontalHeaderLabels(["集合编号", "集合名称", "数据分类", "状态", "内容量", "时间", "操作"])
        self.dataset_table.horizontalHeader().setStretchLastSection(True)
        self.dataset_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.dataset_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.dataset_table.setAlternatingRowColors(True)
        self.dataset_table.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.dataset_table.setShowGrid(True)  # 显示网格线
        self.dataset_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ebeef5;
                border-radius: 4px;
                background-color: #ffffff;
                gridline-color: #ebeef5;
                outline: none;
            }
            QHeaderView::section {
                background-color: #f5f7fa;
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid #ebeef5;
                border-right: 1px solid #ebeef5;
                font-weight: 500;
                font-size: 14px;
                color: #606266;
                text-align: left;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #ebeef5;
                font-size: 14px;
                color: #606266;
            }
            QTableWidget::item:selected {
                background-color: #ecf5ff;
                color: #606266;
            }
            QTableWidget::item:alternate {
                background-color: #fafafa;
            }
        """)

        main_layout.addWidget(self.dataset_table)

        # 分页控件区域
        pagination_layout = QHBoxLayout()
        pagination_layout.setContentsMargins(0, 15, 0, 0)  # 增加上边距
        
        self.total_items_label = QLabel("共 0 条")
        self.total_items_label.setStyleSheet("font-size: 14px; color: #606266;")
        
        self.prev_button = QPushButton("<")
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #606266;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 14px;
                min-width: 32px;
            }
            QPushButton:hover {
                color: #409eff;
                border-color: #c6e2ff;
            }
            QPushButton:disabled {
                color: #c0c4cc;
                background-color: #f4f4f5;
                border-color: #e4e7ed;
            }
        """)
        
        self.page_combo = QComboBox()  # 用于显示和选择页码
        self.page_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: #ffffff;
                font-size: 14px;
                color: #606266;
                min-width: 60px;
            }
            QComboBox:hover {
                border-color: #c0c4cc;
            }
            QComboBox:focus {
                border-color: #409eff;
            }
        """)
        
        self.next_button = QPushButton(">")
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #606266;
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 14px;
                min-width: 32px;
            }
            QPushButton:hover {
                color: #409eff;
                border-color: #c6e2ff;
            }
            QPushButton:disabled {
                color: #c0c4cc;
                background-color: #f4f4f5;
                border-color: #e4e7ed;
            }
        """)
        
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10", "20", "50", "100"])
        self.page_size_combo.setCurrentText("50")  # 默认每页显示50条
        self.page_size_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #dcdfe6;
                border-radius: 4px;
                padding: 6px 10px;
                background-color: #ffffff;
                font-size: 14px;
                color: #606266;
                min-width: 60px;
            }
            QComboBox:hover {
                border-color: #c0c4cc;
            }
            QComboBox:focus {
                border-color: #409eff;
            }
        """)
        
        self.page_size_label = QLabel("条/页")
        self.page_size_label.setStyleSheet("font-size: 14px; color: #606266;")

        pagination_layout.addWidget(self.total_items_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_combo)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_size_combo)
        pagination_layout.addWidget(self.page_size_label)

        main_layout.addLayout(pagination_layout)

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
            self.dataset_table.setItem(row, 1, QTableWidgetItem(dataset.get("name", "")))
            self.dataset_table.setItem(row, 2, QTableWidgetItem(dataset.get("category", ""))) # 需要模型返回分类名称
            self.dataset_table.setItem(row, 3, QTableWidgetItem(dataset.get("status", "")))   # 需要模型返回状态名称
            self.dataset_table.setItem(row, 4, QTableWidgetItem(str(dataset.get("content_size", "")))) # 假设有内容量字段
            # 格式化时间
            created_at = dataset.get("created_at", None)
            time_str = created_at.strftime("%Y-%m-%d %H:%M") if created_at else ""
            self.dataset_table.setItem(row, 5, QTableWidgetItem(time_str))

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
            # modify_button.clicked.connect(lambda checked, r=row: self.controller.modify_item(r))
            # view_button.clicked.connect(lambda checked, r=row: self.controller.view_item(r))
            
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