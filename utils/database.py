from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from configparser import ConfigParser
from utils.logger import get_logger
import os

logger = get_logger()

class DatabaseManager:
    _engine = None
    _session_factory = None
    _scoped_session = None

    @classmethod
    def initialize_engine(cls):
        """Initializes the SQLAlchemy engine based on the config file."""
        if cls._engine is not None:
            logger.info("Database engine already initialized.")
            return

        config_path = 'config/database.ini'
        if not os.path.exists(config_path):
            logger.error(f"Database configuration file not found at: {config_path}")
            raise FileNotFoundError(f"Database configuration file not found: {config_path}")

        config = ConfigParser()
        config.read(config_path)

        try:
            params = config['mysql']
            db_url = f"mysql+pymysql://{params['user']}:{params['password']}@{params['host']}:{params.getint('port', 3306)}/{params['database']}?charset=utf8mb4"
            cls._engine = create_engine(db_url, echo=False) # Set echo=True for debugging SQL
            cls._session_factory = sessionmaker(bind=cls._engine)
            # Use scoped_session for thread-local session management, common in web/GUI apps
            cls._scoped_session = scoped_session(cls._session_factory)
            logger.info("Database engine and session factory initialized successfully.")

            # Test connection
            try:
                with cls._engine.connect() as connection:
                    logger.info("Database connection successful.")
            except Exception as conn_err:
                logger.error(f"Database connection test failed: {conn_err}", exc_info=True)
                cls._engine = None # Reset on connection failure
                cls._session_factory = None
                cls._scoped_session = None
                raise # Re-raise the connection error

        except KeyError as e:
            logger.error(f"Missing key in database config: {e}")
            raise ValueError(f"Missing required key in database config: {e}")
        except Exception as e:
            logger.error(f"Error initializing database engine: {e}", exc_info=True)
            raise

    @classmethod
    def get_engine(cls):
        """Returns the SQLAlchemy engine."""
        if cls._engine is None:
            logger.warning("Engine accessed before initialization. Initializing now.")
            cls.initialize_engine()
        return cls._engine

    @classmethod
    def get_session(cls):
        """Returns a new SQLAlchemy session from the scoped session factory."""
        if cls._scoped_session is None:
            logger.error("Session factory not initialized. Cannot get session.")
            cls.initialize_engine() # Attempt to initialize if not already
            if cls._scoped_session is None:
                 raise RuntimeError("Failed to initialize session factory.")
        # Return a session managed by the scoped_session registry
        return cls._scoped_session()

    @classmethod
    def remove_session(cls):
        """Removes the current session associated with the scope (e.g., thread)."""
        if cls._scoped_session:
            cls._scoped_session.remove()
            logger.debug("SQLAlchemy session removed from scope.")

    @classmethod
    def close_engine(cls):
        """Disposes of the connection pool."""
        if cls._engine:
            cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            cls._scoped_session = None
            logger.info("Database engine disposed.")
