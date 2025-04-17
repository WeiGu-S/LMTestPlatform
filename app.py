import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from views.home_view import HomeView
from models.dataset_model import DatasetModel 
from views.dataset.dataset_view import DatasetView # Corrected import path
from controllers.dataset_controller import DatasetController
from controllers.main_controller import MainController 
from utils.database import DatabaseManager
from models.dataset_model import Base 
from utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger()

def initialize_database():
    """Initializes the database engine and creates tables if they don't exist."""
    try:
        # Initialize the engine using the new DatabaseManager method
        DatabaseManager.initialize_engine()
        engine = DatabaseManager.get_engine()
        if engine:
            # Create tables
            Base.metadata.create_all(engine)
            logger.info("Database tables checked/created successfully.")
            return True # Indicate success
        else:
            logger.error("Failed to get database engine after initialization.")
            return False # Indicate failure
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}", exc_info=True)
        return False # Indicate failure

def main():
    app = QApplication(sys.argv)

    # Initialize Database First
    if not initialize_database():
        # Optionally show an error message to the user
        # QMessageBox.critical(None, "Database Error", "Failed to initialize the database. The application will now exit.")
        logger.critical("Exiting application due to database initialization failure.")
        sys.exit(1) # Exit if database initialization fails

    # 创建主窗口
    main_window = MainWindow()

    # 创建各个页面
    home_view = HomeView()
    dataset_view = DatasetView() # View is created

    # 添加页面到主窗口
    main_window.add_page(home_view, "首页")
    main_window.add_page(dataset_view, "数据集管理")

    # 创建主控制器，负责主窗口的页面切换
    main_controller = MainController(main_window)

    # 创建数据集控制器，负责数据集页面的逻辑
    dataset_controller = DatasetController(dataset_view) # Instantiate the renamed controller

    # Assign controller to the view if needed for signal connections inside the view
    # dataset_view.set_controller(dataset_controller) # Requires adding set_controller method to DatasetView

    # 显示窗口
    main_window.show()

    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()