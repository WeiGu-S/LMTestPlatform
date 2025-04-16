from PySide6.QtWidgets import QMainWindow, QTableView, QVBoxLayout, QWidget
from PySide6.QtCore import QAbstractTableModel, Qt

class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return 3 if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            employee = self._data[index.row()]
            return [employee.id, employee.name, employee.department][index.column()]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.table_view = QTableView()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Employee Manager")
        self.resize(800, 600)
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_table(self, employees):
        self.table_view.setModel(TableModel(employees))
