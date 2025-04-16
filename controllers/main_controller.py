from models.employee_model import Employee
from utils.database import DataBaseManager, DatabasePool
from utils.logger import get_logger

class MainController:
    def __init__(self, view):
        self.view = view
        self.session = DataBaseManager.get_session()
        self.logger = get_logger()
        self.logger.info("Application controller initialized")
        
    def load_data(self):
        # employees = Employee.get_all(self.session)
        employees = Employee.get_all2(self.session)
        self.logger.info(f"Employee.get_all2 {employees}")
        self.view.update_table(employees)
        
    def close_app(self):
        self.logger.info("Application shutdown initiated")
        self.session.close()
        self.view.close()
