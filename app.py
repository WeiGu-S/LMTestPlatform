import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from views.home_view import HomeView
from models.dataset_model import DatasetModel 
from views.dataset.dataset_view import DatasetView # 正确的导入路径
from controllers.dataset_controller import DatasetController
from controllers.main_controller import MainController 
from utils.database import DatabaseManager
from models.dataset_model import Base 
from utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger("app")

def initialize_database():
    """初始化数据库引擎并创建表（如不存在）"""
    try:
        # 使用新的 DatabaseManager 方法初始化引擎
        DatabaseManager.initialize_engine()
        engine = DatabaseManager.get_engine()
        if engine:
            # 创建数据表
            Base.metadata.create_all(engine)
            logger.info("数据库表检查/创建成功。")
            return True # 成功
        else:
            logger.error("初始化后未获取到数据库引擎。")
            return False # 失败
    except Exception as e:
        logger.critical(f"数据库初始化失败: {e}", exc_info=True)
        return False # 失败

def main():
    app = QApplication(sys.argv)

    # 首先初始化数据库
    if not initialize_database():
        # 可选：向用户显示错误消息
        # QMessageBox.critical(None, "数据库错误", "数据库初始化失败，程序即将退出。")
        logger.critical("因数据库初始化失败，程序退出。")
        sys.exit(1) # 初始化失败则退出

    # 创建主窗口
    main_window = MainWindow()

    # 创建各页面
    home_view = HomeView()
    dataset_view = DatasetView() # 创建数据集页面

    # 添加页面到主窗口
    main_window.add_page(dataset_view, "数据集管理")
    main_window.add_page(home_view, "首页")


    # 创建主控制器，负责主窗口页面切换
    main_controller = MainController(main_window)

    # 创建数据集控制器，负责数据集页面逻辑
    dataset_controller = DatasetController(dataset_view) # 实例化控制器


    # 显示主窗口
    main_window.show()

    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()