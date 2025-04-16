from models.dataset_model import Dataset, DatasetStatus, DatasetCategory # Updated import
from utils.database import DatabaseManager # Updated import
from utils.logger import get_logger
from PySide6.QtCore import QObject, Slot, QDate # Added QObject and Slot
from datetime import datetime

class MainController(QObject): # Inherit from QObject for signals/slots
    def __init__(self, view):
        super().__init__() # Call QObject constructor
        self.view = view
        self.session = DatabaseManager.get_session() # Use updated DatabaseManager
        self.logger = get_logger()
        if not self.session:
            self.logger.error("Failed to get database session. Controller initialization aborted.")
            # Handle error appropriately, maybe show a message in the view
            return 
        self.logger.info("Application controller initialized")
        self.current_page = 1
        self.items_per_page = int(self.view.page_size_combo.currentText())
        self.connect_signals()

    def close_app(self):
        self.logger.info("Application shutdown initiated by controller")
        if self.session:
            self.session.close()
            self.logger.info("Database session closed.")
        # View closing is handled by the application's main loop usually
        # self.view.close() # Usually not needed here if app.exec() handles it
