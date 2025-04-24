from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from configparser import ConfigParser
from utils.logger import get_logger
import os

logger = get_logger()

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
            db_url = f"mysql+pymysql://{params['user']}:{params['password']}@{params['host']}:{params.getint('port', 3306)}/{params['database']}?charset=utf8mb4"
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
