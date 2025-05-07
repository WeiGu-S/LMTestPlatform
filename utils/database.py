from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from configparser import ConfigParser
from utils.logger import get_logger
import os

logger = get_logger("database")

class DatabaseManager:
    # 数据库引擎实例
    _engine = None
    _session_factory = None
    _scoped_session = None

    @classmethod
    def initialize_engine(cls):
        """初始化SQLAlchemy引擎，基于配置文件"""
        if cls._engine is not None:
            logger.info("数据库引擎已经初始化。")
            return

        # 配置文件路径
        config_path = 'config/database.ini'
        if not os.path.exists(config_path):
            logger.error(f"未找到数据库配置文件：{config_path}")
            raise FileNotFoundError(f"未找到数据库配置文件：{config_path}")

        # 读取配置文件
        config = ConfigParser()
        config.read(config_path)

        try:
            # 获取MySQL配置参数
            params = config['mysql']
            db_url = f"mysql+pymysql://{params['user']}:{params['password']}@{params['host']}:{params.getint('port', 3306)}"
            cls._engine = create_engine(db_url, echo=False) # 设置echo=True用于调试SQL
            cls._session_factory = sessionmaker(bind=cls._engine)
            # 使用scoped_session进行线程本地会话管理，常用于web/GUI应用
            cls._scoped_session = scoped_session(cls._session_factory)
            logger.info("数据库引擎和会话工厂初始化成功。")

            # 测试数据库连接
            try:
                with cls._engine.connect() as connection:
                    logger.info("数据库连接成功。")
            except Exception as conn_err:
                logger.error(f"数据库连接测试失败：{conn_err}", exc_info=True)
                # 连接失败时重置所有实例
                cls._engine = None
                cls._session_factory = None
                cls._scoped_session = None
                raise

        except KeyError as e:
            logger.error(f"数据库配置中缺少键：{e}")
            raise ValueError(f"数据库配置中缺少必需的键：{e}")
        except Exception as e:
            logger.error(f"初始化数据库引擎时出错：{e}", exc_info=True)
            raise

    @classmethod
    def get_engine(cls):
        """返回SQLAlchemy引擎"""
        if cls._engine is None:
            logger.warning("在初始化之前访问引擎。现在开始初始化。")
            cls.initialize_engine()
        return cls._engine

    @classmethod
    def get_session(cls):
        """从作用域会话工厂返回新的SQLAlchemy会话"""
        if cls._scoped_session is None:
            logger.error("会话工厂未初始化。无法获取会话。")
            cls.initialize_engine() # 如果尚未初始化则尝试初始化
            if cls._scoped_session is None:
                 raise RuntimeError("初始化会话工厂失败。")
        # 返回由scoped_session注册表管理的会话
        return cls._scoped_session()

    @classmethod
    def remove_session(cls):
        """移除当前作用域（如线程）关联的会话"""
        if cls._scoped_session:
            cls._scoped_session.remove()
            logger.debug("已从作用域中移除SQLAlchemy会话。")

    @classmethod
    def close_engine(cls):
        """释放连接池"""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            cls._scoped_session = None
            logger.info("数据库引擎已释放。")

    @classmethod
    def initialize_database(cls):
        """初始化数据库并创建表结构（仅当表不存在时）"""
        try:
            cls.initialize_engine()
            engine = cls.get_engine()
            if not engine:
                logger.error("数据库引擎初始化失败")
                return False

            with engine.connect() as conn:
                # 创建数据库（如果不存在）
                # 检查数据库是否存在
                if not conn.execute(text("SHOW DATABASES LIKE 'testPlatform'")).fetchone():
                    logger.info("数据库不存在，正在创建...")
                    conn.execute(text("CREATE DATABASE testPlatform"))
                    logger.info("创建数据库: testPlatform")
                conn.execute(text("USE testPlatform"))
                
                # 如需创建其他表，请在这里添加
                sql_dir = [
                    'create_t_data_collections.sql',
                    'create_t_data_collection_info.sql',
                    'create_t_data_attachment.sql',
                    'create_t_lm_config.sql',
                    'create_t_test_task_info.sql',
                    'create_t_test_data_snapshot.sql',
                    'create_t_test_attachment_snapshot.sql',
                    'create_t_test_task_info.sql',
                    'create_t_test_round_info.sql',
                    'create_t_dictionary.sql'
                ]
                
                # 检查已存在表
                existing_tables = {t[0] for t in 
                    conn.execute(text("SHOW TABLES")).fetchall()}
                
                # 按顺序执行建表SQL
                for sql_file in sql_dir:
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