import sys, os
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow
from views.home_view import HomeView
# from models.data_collection_model import DataCollectionModel
from views.dataset.data_collection_view import DataCollectionView # 正确的导入路径
from controllers.data_collection_controller import DataCollectionController
from controllers.main_controller import MainController 
from utils.database import DatabaseManager
from sqlalchemy import text  
from models.data_collection_model import Base 
from utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger("app")

def initialize_database():
    """初始化数据库并创建表结构（仅当表不存在时）"""
    try:
        DatabaseManager.initialize_engine()
        engine = DatabaseManager.get_engine()
        if not engine:
            logger.error("数据库引擎初始化失败")
            return False

        with engine.connect() as conn:
            # 创建数据库（如果不存在）
            conn.execute(text("CREATE DATABASE IF NOT EXISTS testPlatform"))
            conn.execute(text("USE testPlatform"))
            
            # 获取执行顺序（解决外键依赖）
            sql_files = [
                'create_t_data_collections.sql',
                'create_t_data_collection_info.sql',
                'create_t_data_attachment.sql'
            ]
            
            # 检查已存在表
            existing_tables = {t[0] for t in 
                conn.execute(text("SHOW TABLES")).fetchall()}
            
            # 按顺序执行建表SQL
            for sql_file in sql_files:
                table_name = sql_file[7:-4]  # 移除'create_'和'.sql'
                
                if table_name not in existing_tables:
                    sql_path = os.path.join('utils/sql', sql_file)
                    try:
                        with open(sql_path, 'r', encoding='utf-8') as f:
                            sql = f.read().strip()
                            if sql:
                                logger.info(f"正在创建表: {table_name}")
                                conn.execute(text(sql))
                    except Exception as e:
                        logger.error(f"执行 {sql_file} 失败: {str(e)}")
                        raise
                else:
                    logger.debug(f"表 {table_name} 已存在，跳过创建")
            
            conn.commit()
            logger.info("数据库表结构初始化完成")
            return True
            
    except Exception as e:
        logger.critical(f"数据库初始化失败: {str(e)}", exc_info=True)
        return False

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
    dataset_view = DataCollectionView() # 创建数据集页面

    # 添加页面到主窗口
    main_window.add_page(dataset_view, "数据集管理")
    main_window.add_page(home_view, "首页")


    # 创建主控制器，负责主窗口页面切换
    main_controller = MainController(main_window)

    # 创建数据集控制器，负责数据集页面逻辑
    data_collection_controller = DataCollectionController(dataset_view) # 实例化控制器


    # 显示主窗口
    main_window.show()

    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()