from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QStackedWidget, QLabel
)
from PySide6.QtCore import Qt, Slot # Add Slot import here

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("上研院 大模型测试平台")
        self.setGeometry(100, 100, 1200, 880)   
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 左侧菜单栏
        self.menu_list = QListWidget()
        self.menu_list.setFixedWidth(200)
        self.menu_list.setStyleSheet("""
            QListWidget {
                background-color: #80a492;
                color: white;
                font-size: 16px;
                border: 1px solid #96a1a0;
                border-radius: 8px;
                padding: 10px
            }
            QListWidget::item {
                height: 50px;
                padding-left: 20px;

            }
            QListWidget::item:selected {
                background-color: #3498db;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(self.menu_list)
        
        # 右侧内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        
        # 标题栏
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px 0;
                border-bottom: 2px solid #3498db;
            }
        """)
        content_layout.addWidget(self.title_label)
        
        # 页面堆栈
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_widget, stretch=1)

        # 连接菜单列表项点击事件
        self.menu_list.currentRowChanged.connect(self.set_current_page_from_menu)
    
    def add_page(self, widget, title):
        """添加页面到堆栈并更新菜单"""
        self.stacked_widget.addWidget(widget)
        # 存储页面标题
        widget.setProperty("page_title", title)
        # 添加到菜单列表
        self.menu_list.addItem(title)
    
    @Slot(int)
    def set_current_page_from_menu(self, index):
        """根据菜单选择设置当前显示的页面"""
        if 0 <= index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)
            current_widget = self.stacked_widget.currentWidget()
            title = current_widget.property("page_title")
            self.title_label.setText(title)

    def set_current_page_by_controller(self, index):
        """由控制器设置当前页面，并同步菜单选中状态"""
        if 0 <= index < self.stacked_widget.count():
            # 设置堆栈页面
            self.stacked_widget.setCurrentIndex(index)
            current_widget = self.stacked_widget.currentWidget()
            title = current_widget.property("page_title")
            self.title_label.setText(title)
            # 同步菜单选中项，但不触发 currentRowChanged 信号
            self.menu_list.blockSignals(True)
            self.menu_list.setCurrentRow(index)
            self.menu_list.blockSignals(False)