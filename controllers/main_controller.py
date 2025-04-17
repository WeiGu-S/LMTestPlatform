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