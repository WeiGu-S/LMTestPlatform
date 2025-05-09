import sys, os
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from views.home_view import HomeView
from views.dataset.data_collection_view import DataCollectionView # 正确的导入路径
from controllers.data_collection_controller import DataCollectionController
from controllers.main_controller import MainController 
from utils.database import DatabaseManager
from sqlalchemy import text  
from models.data_collection_model import Base 
from utils.logger import setup_logging, get_logger
from utils.database import DatabaseManager

setup_logging()
logger = get_logger("app")

def main():
    app = QApplication(sys.argv)
    # 首先初始化数据库
    try:
        if not DatabaseManager.initialize_database():
            # 可选：向用户显示错误消息
            logger.critical("因数据库初始化失败，程序退出。")
            sys.exit(1)  # 初始化失败则退出
    except Exception as e:
        logger.critical(f"数据库初始化过程中发生异常: {str(e)}")
        sys.exit(1)  # 遇到异常时退出
    # 创建主窗口
    main_window = MainWindow()

    # 创建各页面
    home_view = HomeView()
    data_collection_view = DataCollectionView() # 创建数据集页面
    # 添加页面到主窗口
    main_window.add_page(data_collection_view, "数据集管理")
    main_window.add_page(home_view, "首页")

    # 创建主控制器，负责主窗口页面切换
    main_controller = MainController(main_window)
    # 创建数据集控制器，负责数据集页面逻辑
    data_collection_controller = DataCollectionController(data_collection_view) # 实例化控制器
    # 显示主窗口
    main_window.show()

    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()