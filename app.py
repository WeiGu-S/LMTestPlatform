import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from controllers.main_controller import MainController
from utils.logger import setup_logging
from models.employee_model import Base  # 新增导入

def main():
    setup_logging()
    app = QApplication(sys.argv)
    
    # 初始化MVC
    main_window = MainWindow()
    controller = MainController(main_window)
    main_window.controller = controller

    # 新增：自动建表
    #Base.metadata.create_all(controller.engine)
    
    # 加载数据
    controller.load_data()
    main_window.show()
    
    # 退出处理
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
