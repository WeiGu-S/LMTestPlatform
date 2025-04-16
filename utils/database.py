import pymysql
from pymysql import Error
from configparser import ConfigParser

from sqlalchemy.sql.functions import user

class DatabaseManager:    
    def __init__(self):
        super().__init__()
        self.connection = None
        self.connect_to_db()
        
    def connect_to_db(self):
        config = ConfigParser()
        config.read('config/database.ini')
        params = config['mysql']
        try:
            self.connection = pymysql.connect(
                user=params['user'],
                password=params['password'],
                host=params['host'],
                port=int(params['port']),
                database=params['database'],
                charset='utf8mb4'
            )
        except Error as e:
            self.connection_error.emit(f"数据库连接失败: {str(e)}")
            self.connection = None                

    @classmethod
    def get_session(cls):
        if not cls._instance:
            cls._instance = cls()
        Session = sessionmaker(bind=cls._instance.engine)
        return Session()

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None
