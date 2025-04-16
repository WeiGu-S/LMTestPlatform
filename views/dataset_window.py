from PySide6.QtWidgets import (QMainWindow, QTableView, QVBoxLayout, QWidget, 
                             QHBoxLayout, QLabel, QLineEdit, QComboBox, 
                             QDateEdit, QPushButton, QGridLayout, QSpacerItem, 
                             QSizePolicy, QHeaderView)
from PySide6.QtCore import QAbstractTableModel, Qt, QDate

class TableModel(QAbstractTableModel):
    def __init__(self, data): # data should be a list of lists or similar
        super().__init__()
        self._data = data
        # Define headers based on the image
        self._headers = ["集合编号", "集合名称", "数据分类", "状态", "内容量", "创建时间", "操作"]

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        # Updated column count based on headers
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role == Qt.DisplayRole:
            # Assuming self._data is a list of lists/tuples matching the column order
            try:
                return str(self._data[index.row()][index.column()])
            except IndexError:
                return None
        elif role == Qt.TextAlignmentRole:
             return Qt.AlignCenter # Center align text
        # Add handling for buttons in the '操作' column later if needed
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.table_view = QTableView()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("数据集") 
        self.resize(1000, 700) 

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # --- 筛选条件 --- 
        filter_layout = QGridLayout()
        filter_layout.addWidget(QLabel("集合名称"), 0, 0)
        self.name_filter_input = QLineEdit()
        self.name_filter_input.setPlaceholderText("请输入集合编号") # Placeholder text from image
        filter_layout.addWidget(self.name_filter_input, 0, 1)

        filter_layout.addWidget(QLabel("状态"), 0, 2)
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems(["全部", "启用", "禁用"]) # Example statuses
        filter_layout.addWidget(self.status_filter_combo, 0, 3)

        filter_layout.addWidget(QLabel("数据分类"), 0, 4)
        self.category_filter_combo = QComboBox()
        self.category_filter_combo.addItems(["全部", "视频", "图片","文本","音频"]) # Example categories
        filter_layout.addWidget(self.category_filter_combo, 0, 5)
        
        self.query_button = QPushButton("查询")
        filter_layout.addWidget(self.query_button, 0, 6)

        filter_layout.addWidget(QLabel("创建时间"), 1, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1)) # Default start date
        filter_layout.addWidget(self.start_date_edit, 1, 1)

        filter_layout.addWidget(QLabel("至"), 1, 2, Qt.AlignCenter)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate()) # Default end date
        filter_layout.addWidget(self.end_date_edit, 1, 3)
        
        # Add spacer to push buttons to the right
        filter_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 1, 4, 1, 2)

        self.reset_button = QPushButton("重置")
        filter_layout.addWidget(self.reset_button, 1, 6)

        main_layout.addLayout(filter_layout)

        # --- Action Buttons --- 
        action_layout = QHBoxLayout()
        self.new_button = QPushButton("+ 新建")
        self.export_button = QPushButton("导出")
        action_layout.addWidget(self.new_button)
        action_layout.addStretch(1)
        action_layout.addWidget(self.export_button)
        main_layout.addLayout(action_layout)

        # --- Table View --- 
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns
        self.table_view.setAlternatingRowColors(True) # Improve readability
        main_layout.addWidget(self.table_view)

        # --- Pagination Area --- 
        pagination_layout = QHBoxLayout()
        self.total_label = QLabel("共 0 条")
        self.prev_button = QPushButton("<")
        self.page_combo = QComboBox() # Use ComboBox for page selection
        self.next_button = QPushButton(">")
        self.page_size_combo = QComboBox() # For items per page
        # self.page_size_combo.addItems(["10", "20", "50", "100"]) # Example page sizes
        self.page_size_combo.setCurrentText("10") # Default page size

        pagination_layout.addWidget(self.total_label)
        pagination_layout.addStretch(1)
        pagination_layout.addWidget(QLabel("每页"))
        pagination_layout.addWidget(self.page_size_combo)
        pagination_layout.addWidget(QLabel("条"))
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_combo)
        pagination_layout.addWidget(self.next_button)
        main_layout.addLayout(pagination_layout)

        self.setCentralWidget(central_widget)

    def update_table(self, data, total_items=0, current_page=1, total_pages=1):
        """Updates the table view and pagination controls."""
        self.table_view.setModel(TableModel(data))
        self.total_label.setText(f"共 {total_items} 条")
        
        self.page_combo.blockSignals(True) # Prevent signals during update
        self.page_combo.clear()
        if total_pages > 0:
            self.page_combo.addItems([str(i) for i in range(1, total_pages + 1)])
            self.page_combo.setCurrentText(str(current_page))
        self.page_combo.blockSignals(False)

        self.prev_button.setEnabled(current_page > 1)
        self.next_button.setEnabled(current_page < total_pages)

    # Add methods to connect signals later in the controller
