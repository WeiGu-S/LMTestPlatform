import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from controllers.main_controller import MainController
from utils.logger import setup_logging
# from models.employee_model import Base  # 移除旧的导入
from models.dataset_model import Base as DatasetBase # 导入新的 Base
from utils.database import DatabaseManager # 导入 DatabaseManager

def main():
    setup_logging()
    app = QApplication(sys.argv)
    
    # 初始化数据库和模型
    engine = DatabaseManager.get_engine()
    if not engine:
        print("数据库引擎初始化失败，程序退出。") # 或者显示错误消息框
        sys.exit(1)
        
    # 自动建表 (使用新的 Base)
    try:
        DatasetBase.metadata.create_all(engine)
        print("数据库表检查/创建完成。")
    except Exception as e:
        print(f"数据库表创建失败: {e}")
        # 根据需要决定是否退出

    # 初始化MVC
    main_window = MainWindow()
    controller = MainController(main_window)
    # main_window.controller = controller # Controller now takes view in __init__

    # 加载数据
    controller.load_data() # Controller handles loading
    # Connect dynamic page buttons after data is loaded and table is updated
    main_window.connect_page_buttons(controller.go_to_specific_page)

    main_window.show()
    
    # 退出处理
    exit_code = app.exec()
    # 清理数据库连接池
    db_manager = DatabaseManager() # Get instance
    db_manager.close_connection()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
