from PySide6.QtWidgets import (QMainWindow, QTableView, QVBoxLayout, QWidget, 
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                             QDateEdit, QPushButton, QGridLayout, QSpacerItem, 
                             QSizePolicy, QHeaderView, QListWidget, QListWidgetItem,
                             QSplitter)
from PySide6.QtGui import QIcon # 如果需要图标，导入 QIcon
from PySide6.QtCore import QSize # 如果需要图标尺寸，导入 QSize
from PySide6.QtCore import QAbstractTableModel, Qt, QDate

# 表格模型类，继承自 QAbstractTableModel
class TableModel(QAbstractTableModel):
    def __init__(self, data): # data 应该是一个列表的列表或类似的结构
        super().__init__()
        self._data = data
        # 根据图像定义表头
        self._headers = ["集合编号", "集合名称", "数据分类", "状态", "内容量", "创建时间", "操作"]

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        # 根据表头更新列数
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole:
            # 假设 self._data 是一个列表的列表/元组，匹配列顺序
            try:
                return str(self._data[index.row()][index.column()])
            except IndexError:
                return None
        elif role == Qt.TextAlignmentRole:
             return Qt.AlignCenter # 文本居中对齐
        # 如果需要，在 '操作' 列中添加按钮处理
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

# 主窗口类，继承自 QMainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化需要稍后访问的控件（如侧边栏）
        self.sidebar = QListWidget()
        self.table_view = QTableView()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("数据集") 
        self.resize(1200, 800) # 调整侧边栏的大小

        central_widget = QWidget()
        self.setCentralWidget(central_widget) # 首先设置中央控件

        # 中央控件的整体布局
        overall_layout = QHBoxLayout(central_widget)
        overall_layout.setContentsMargins(0, 0, 0, 0)
        overall_layout.setSpacing(0)

        # --- 侧边栏 --- 
        # self.sidebar = QListWidget() # 将初始化移到 __init__
        self.sidebar.setFixedWidth(180)
        self.sidebar.addItem(QListWidgetItem("仪表盘"))
        self.sidebar.addItem(QListWidgetItem("数据可视化"))
        list_page_item = QListWidgetItem("列表页")
        self.sidebar.addItem(list_page_item)
        sub_item1 = QListWidgetItem("  查询表格")
        self.sidebar.addItem(sub_item1)
        sub_item2 = QListWidgetItem("  卡片列表")
        self.sidebar.addItem(sub_item2)
        self.sidebar.setCurrentItem(sub_item1)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #f0f2f5;
                border: none;
                padding-top: 10px;
            }
            QListWidget::item {
                padding: 10px 15px;
                border-bottom: 1px solid #e8e8e8;
            }
            QListWidget::item:selected {
                background-color: #e6f7ff;
                color: #1890ff;
                border-left: 3px solid #1890ff;
            }
        """)

        # --- 主内容区域 --- 
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)

        # --- 面包屑导航 --- 
        breadcrumb_layout = QHBoxLayout()
        breadcrumb_label = QLabel(" / 列表页 / 查询表格")
        breadcrumb_layout.addWidget(breadcrumb_label)
        breadcrumb_layout.addStretch(1)
        content_layout.addLayout(breadcrumb_layout)

        # --- 筛选区域 --- 
        filter_layout = QGridLayout()
        filter_layout.addWidget(QLabel("集合名称"), 0, 0)
        self.name_filter_input = QLineEdit()
        self.name_filter_input.setPlaceholderText("请输入集合编号")
        filter_layout.addWidget(self.name_filter_input, 0, 1)
        filter_layout.addWidget(QLabel("状态"), 0, 2)
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems(["全部", "启用", "禁用"])
        filter_layout.addWidget(self.status_filter_combo, 0, 3)
        filter_layout.addWidget(QLabel("数据分类"), 0, 4)
        self.category_filter_combo = QComboBox()
        # 根据图像提示更新类别
        self.category_filter_combo.addItems(["全部", "竖版视频", "横版视频", "图片", "文本", "音频"])
        filter_layout.addWidget(self.category_filter_combo, 0, 5)
        self.query_button = QPushButton("查询")
        filter_layout.addWidget(self.query_button, 0, 6)
        filter_layout.addWidget(QLabel("创建时间"), 1, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.start_date_edit, 1, 1)
        filter_layout.addWidget(QLabel("至"), 1, 2, Qt.AlignCenter)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date_edit, 1, 3)
        filter_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 4, 1, 2)
        self.reset_button = QPushButton("重置")
        filter_layout.addWidget(self.reset_button, 1, 6)
        content_layout.addLayout(filter_layout)

        # --- 操作按钮 --- 
        action_layout = QHBoxLayout()
        self.new_button = QPushButton("+ 新建")
        self.export_button = QPushButton("导出")
        action_layout.addWidget(self.new_button)
        action_layout.addStretch(1)
        action_layout.addWidget(self.export_button)
        content_layout.addLayout(action_layout)

        # --- 表格视图 --- 
        # self.table_view = QTableView() # 将初始化移到 __init__
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setAlternatingRowColors(True)
        content_layout.addWidget(self.table_view)

        # --- 分页区域 --- 
        pagination_layout = QHBoxLayout()
        self.total_label = QLabel("共 0 条")
        self.prev_button = QPushButton("<")
        # self.page_combo = QComboBox() # 用布局替换 ComboBox 以显示页码
        self.page_numbers_layout = QHBoxLayout() # 布局用于放置页码按钮/标签
        self.page_numbers_layout.setSpacing(2) # 页码之间的小间距
        self.next_button = QPushButton(">")
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10", "20", "50", "100"]) # 示例页大小
        self.page_size_combo.setCurrentText("50") # 默认页大小来自图像（假设为 50）

        pagination_layout.addWidget(self.total_label)
        pagination_layout.addStretch(1)
        # 恢复页大小控件（之前注释掉）
        pagination_layout.addWidget(QLabel("每页")) 
        pagination_layout.addWidget(self.page_size_combo)
        pagination_layout.addWidget(QLabel("条")) 
        pagination_layout.addWidget(self.prev_button)
        # pagination_layout.addWidget(self.page_combo) # 移除 ComboBox
        pagination_layout.addLayout(self.page_numbers_layout) # 添加页码布局
        pagination_layout.addWidget(self.next_button)
        # 如果需要，稍后添加跳转到页输入
        content_layout.addLayout(pagination_layout)

        # --- 分割器 --- 
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(content_widget)
        splitter.setSizes([180, 1020]) # 调整初始大小
        splitter.setStretchFactor(1, 1)

        overall_layout.addWidget(splitter)

    def update_table(self, data, total_items=0, current_page=1, total_pages=1):
        """更新表格视图和分页控件。"""
        self.table_view.setModel(TableModel(data))
        # 根据图像更新分页
        self.total_label.setText(f"共 {total_items} 条")
        
        # --- 更新页码显示 --- 
        # 清除现有的页码控件
        while self.page_numbers_layout.count():
            item = self.page_numbers_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if total_pages > 0:
            # 显示页码的逻辑，如图像所示（例如，< 50 [51] 52 53 54 ... 90 >）
            max_visible_pages = 5 # 显示在当前页周围的页码数量
            pages_to_display = []

            if total_pages <= max_visible_pages + 2: # 如果页数少，显示所有
                pages_to_display = list(range(1, total_pages + 1))
            else:
                pages_to_display.append(1)
                start_page = max(2, current_page - (max_visible_pages // 2))
                end_page = min(total_pages - 1, current_page + (max_visible_pages // 2))
                
                # 如果接近开头，调整窗口
                if current_page <= max_visible_pages // 2 + 1:
                    end_page = max_visible_pages
                # 如果接近结尾，调整窗口
                elif current_page >= total_pages - (max_visible_pages // 2):
                    start_page = total_pages - max_visible_pages + 1

                if start_page > 2:
                    pages_to_display.append('...') # 省略号
                
                for i in range(start_page, end_page + 1):
                    pages_to_display.append(i)
                
                if end_page < total_pages - 1:
                    pages_to_display.append('...') # 省略号
                
                pages_to_display.append(total_pages)

            # 创建并添加页码控件
            for page in pages_to_display:
                if page == '...':
                    label = QLabel('...')
                    self.page_numbers_layout.addWidget(label)
                else:
                    button = QPushButton(str(page))
                    button.setFlat(True) # 使其看起来像文本
                    button.setFixedSize(25, 25) # 根据需要调整大小
                    if page == current_page:
                        button.setStyleSheet("background-color: #1890ff; color: white; border-radius: 4px;")
                        button.setEnabled(False)
                    else:
                        # 将按钮点击连接到 go_to_specific_page 插槽（需要实现或连接）
                        # button.clicked.connect(lambda checked, p=page: self.go_to_specific_page(p))
                        # 我们需要访问控制器来连接信号。
                        # 这个连接应该理想地发生在控制器实例化并访问视图时。
                        # 目前，我们假设连接在其他地方设置或传递控制器实例。
                        # 占位符：print(f"Button for page {page} created, connect me!")
                        button.setStyleSheet("color: #1890ff;") # 可点击页的样式
                        self.page_numbers_layout.addWidget(button)
        else: # 没有项目/页
             label = QLabel('1') # 即使没有页也显示 '1'
             label.setEnabled(False)
             self.page_numbers_layout.addWidget(label)

        # --- 结束更新页码显示 ---

        self.prev_button.setEnabled(current_page > 1)
        self.next_button.setEnabled(current_page < total_pages)

    # 添加方法以在控制器中稍后连接信号
    # 需要一个插槽，如 go_to_specific_page(page_num) 在控制器中，并将页按钮连接到它。

    # 连接页按钮的方法（需要控制器实例）
    def connect_page_buttons(self, controller_slot):
        """将动态创建的页按钮连接到控制器的插槽。"""
        for i in range(self.page_numbers_layout.count()):
            widget = self.page_numbers_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.isEnabled(): # 仅连接已启用的按钮
                try:                    
                    page_num = int(widget.text())
                    # 首先断开以前的连接，以避免在多次调用 update_table 时出现重复
                    try:
                        widget.clicked.disconnect()
                    except RuntimeError: # 没有连接可断开
                        pass 
                    widget.clicked.connect(lambda checked, p=page_num: controller_slot(p))
                    # print(f"Connected button for page {page_num}") # 调试
                except Exception as e:
                    print(f"Error connecting button {widget.text()}: {e}") # 调试
