from PySide6.QtCore import QObject, Signal, Slot

class MainController(QObject):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_connections()
    
    def setup_connections(self):
        """设置信号和槽连接"""
        # 主窗口菜单项点击信号已在 MainWindow 内部连接到 set_current_page_from_menu
        # 这里不再需要连接 currentRowChanged
        
        # 初始化显示首页 (通过调用控制器的方法)
        self.switch_page(0)
    
    @Slot(int)
    def switch_page(self, index):
        """切换页面"""
        # 调用 MainWindow 中由控制器调用的方法
        self.main_window.set_current_page_by_controller(index)

    @Slot(int)
    def set_current_page_from_menu(self, index):
        """根据菜单选择设置当前显示的页面"""
        if 0 <= index < self.main_window.stacked_widget.count():
            self.main_window.stacked_widget.setCurrentIndex(index)
            current_widget = self.main_window.stacked_widget.currentWidget()
            title = current_widget.property("page_title")
            self.main_window.title_label.setText(title)

    def set_current_page_by_controller(self, index):
        """由控制器设置当前页面，并同步菜单选中状态"""
        if 0 <= index < self.main_window.stacked_widget.count():
            # 设置堆栈页面
            self.main_window.stacked_widget.setCurrentIndex(index)
            current_widget = self.main_window.stacked_widget.currentWidget()
            title = current_widget.property("page_title")
            self.main_window.title_label.setText(title)
            # 同步菜单选中项，但不触发 currentRowChanged 信号
            self.main_window.menu_list.blockSignals(True)
            self.main_window.menu_list.setCurrentRow(index)
            self.main_window.menu_list.blockSignals(False)