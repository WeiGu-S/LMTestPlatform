from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from configparser import ConfigParser
from utils.logger import get_logger

class DatabaseManager:
    _instance = None
    _engine = None
    _Session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.logger = get_logger()
        config = ConfigParser()
        try:
            config.read('config/database.ini')
            params = config['mysql']
            db_url = f"mysql+pymysql://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['database']}?charset=utf8mb4"
            
            pool_size = int(params.get('pool_size', 5))
            pool_recycle = int(params.get('pool_recycle', 3600))

            self._engine = create_engine(
                db_url,
                pool_size=pool_size,
                pool_recycle=pool_recycle,
                echo=False # Set to True for debugging SQL queries
            )
            self._Session = sessionmaker(bind=self._engine)
            self.logger.info("Database engine and session maker initialized successfully.")
            # Test connection
            try:
                with self._engine.connect() as connection:
                    self.logger.info("Database connection successful.")
            except SQLAlchemyError as e:
                self.logger.error(f"Database connection test failed: {e}")
                self._engine = None
                self._Session = None

        except Exception as e:
            self.logger.error(f"Failed to initialize database manager: {e}")
            self._engine = None
            self._Session = None

    @classmethod
    def get_session(cls) -> Session:
        """Provides a new database session."""
        if cls._instance is None:
            cls() # Initialize if not already done
        
        if cls._Session:
            try:
                session = cls._Session()
                # self.logger.debug("Database session created.") # Optional: log session creation
                return session
            except Exception as e:
                cls._instance.logger.error(f"Failed to create database session: {e}")
                return None
        else:
            cls._instance.logger.error("Session maker not initialized. Cannot create session.")
            return None

    @classmethod
    def get_engine(cls):
        """Returns the SQLAlchemy engine."""
        if cls._instance is None:
            cls()
        return cls._engine

    def close_connection(self):
        """Disposes the engine connection pool."""
        if self._engine:
            self._engine.dispose()
            self.logger.info("Database engine disposed.")
            self._engine = None
            self._Session = None
            DatabaseManager._instance = None # Reset instance

# Optional: Instantiate the manager once if needed globally, 
# but get_session() handles instantiation on demand.
# db_manager = DatabaseManager()
