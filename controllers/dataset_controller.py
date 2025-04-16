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

    def connect_signals(self):
        """Connect UI signals to controller slots."""
        self.view.query_button.clicked.connect(self.query_data)
        self.view.reset_button.clicked.connect(self.reset_filters)
        self.view.new_button.clicked.connect(self.create_new_dataset) # Placeholder
        self.view.export_button.clicked.connect(self.export_data) # Placeholder
        self.view.prev_button.clicked.connect(self.prev_page)
        self.view.next_button.clicked.connect(self.next_page)
        self.view.page_combo.currentIndexChanged.connect(self.go_to_page) # Use index change
        self.view.page_size_combo.currentIndexChanged.connect(self.change_page_size)

    @Slot()
    def load_data(self):
        """Loads the initial or filtered data into the table."""
        if not self.session:
            self.logger.error("No database session available to load data.")
            self.view.update_table([], 0, 1, 1) # Show empty table
            return

        filters = self.get_filters()
        self.logger.info(f"Loading data with filters: {filters}, page: {self.current_page}, per_page: {self.items_per_page}")
        try:
            data, total_items, total_pages = Dataset.get_paginated_datasets(
                self.session,
                page=self.current_page,
                per_page=self.items_per_page,
                filters=filters
            )
            self.logger.info(f"Loaded {len(data)} datasets. Total items: {total_items}, Total pages: {total_pages}")
            self.view.update_table(data, total_items, self.current_page, total_pages)
        except Exception as e:
            self.logger.error(f"Error loading data: {e}", exc_info=True)
            # Optionally show an error message to the user via the view
            self.view.update_table([], 0, 1, 1) # Show empty table on error

    def get_filters(self):
        """Collects filter values from the UI."""
        filters = {
            'name': self.view.name_filter_input.text(),
            'status': self.view.status_filter_combo.currentText(),
            'category': self.view.category_filter_combo.currentText(),
            # Convert QDate to datetime.date or datetime object
            'start_date': self.view.start_date_edit.date().toPython() if self.view.start_date_edit.date().isValid() else None,
            'end_date': self.view.end_date_edit.date().toPython() if self.view.end_date_edit.date().isValid() else None,
        }
        # Convert end_date to beginning of the next day for inclusive filtering if needed by model
        # The model already handles adding timedelta, so just pass the date.
        return {k: v for k, v in filters.items() if v is not None and v != ''} # Clean empty filters

    @Slot()
    def query_data(self):
        """Slot to handle query button click."""
        self.current_page = 1 # Reset to first page on new query
        self.load_data()

    @Slot()
    def reset_filters(self):
        """Slot to handle reset button click."""
        self.view.name_filter_input.clear()
        self.view.status_filter_combo.setCurrentIndex(0) # Index 0 is '全部'
        self.view.category_filter_combo.setCurrentIndex(0)
        self.view.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.view.end_date_edit.setDate(QDate.currentDate())
        self.current_page = 1
        self.load_data()

    @Slot()
    def prev_page(self):
        """Go to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    @Slot()
    def next_page(self):
        """Go to the next page."""
        # Check against total pages calculated during the last load_data
        # This requires total_pages to be stored or recalculated if necessary
        # For simplicity, we rely on the view's button state, but a more robust
        # approach might store total_pages in the controller.
        self.current_page += 1
        self.load_data()

    @Slot(int)
    def go_to_page(self, index):
        """Go to a specific page selected from the combo box."""
        if index >= 0: # Check if a valid item is selected
            try:
                page_num = int(self.view.page_combo.itemText(index))
                if page_num != self.current_page:
                    self.current_page = page_num
                    self.load_data()
            except ValueError:
                self.logger.warning(f"Invalid page number selected: {self.view.page_combo.itemText(index)}")

    @Slot(int)
    def go_to_specific_page(self, page_num):
        """Slot to handle clicks on specific page number buttons."""
        if page_num != self.current_page:
            self.logger.info(f"Jumping to page: {page_num}")
            self.current_page = page_num
            self.load_data()

    @Slot(int)
    def change_page_size(self, index):
        """Change the number of items displayed per page."""
        try:
            self.items_per_page = int(self.view.page_size_combo.itemText(index))
            self.current_page = 1 # Reset to page 1 when page size changes
            self.logger.info(f"Page size changed to: {self.items_per_page}")
            self.load_data()
        except ValueError:
             self.logger.warning(f"Invalid page size selected: {self.view.page_size_combo.itemText(index)}")

    @Slot()
    def create_new_dataset(self):
        """Placeholder for creating a new dataset."""
        self.logger.info("Placeholder: 'Create New Dataset' button clicked.")
        # Implementation would involve opening a new dialog/window

    @Slot()
    def export_data(self):
        """Placeholder for exporting data."""
        self.logger.info("Placeholder: 'Export Data' button clicked.")
        # Implementation would involve fetching all filtered data and writing to a file (e.g., CSV)

    def close_app(self):
        self.logger.info("Application shutdown initiated by controller")
        if self.session:
            self.session.close()
            self.logger.info("Database session closed.")
        # View closing is handled by the application's main loop usually
        # self.view.close() # Usually not needed here if app.exec() handles it
