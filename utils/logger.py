import logging.config
from pathlib import Path

def setup_logging():
    """
    初始化日志配置，确保日志目录存在并加载配置文件。
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logging.config.fileConfig(
        fname='config/logging.conf',
        disable_existing_loggers=False
    )

def get_logger(name: str = "appLogger"):
    """
    获取指定名称的日志记录器。
    :param name: 日志记录器名称
    :return: Logger 实例
    """
    return logging.getLogger(name)
