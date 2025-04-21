from PySide6.QtCore import QObject, Slot
from utils.database import DatabaseManager
from utils.logger import get_logger
from views.dataset.dataset_view import DatasetView
from models.dataset_model import DatasetModel, DatasetStatus
from datetime import datetime, timezone, timedelta

logger = get_logger("dataset_controller")

class DatasetController(QObject):
    def __init__(self, view: DatasetView):
        super().__init__()
        self.view = view
        self.logger = get_logger(__name__)
        self.current_page = 1
        self.items_per_page = 10
        self.connect_signals()
        self.load_initial_data()

    def connect_signals(self):
        """连接所有信号"""
        self.view.query_signal.connect(self.handle_query)
        self.view.reset_signal.connect(self.handle_reset)
        self.view.insert_signal.connect(self.show_inset_dialog)
        self.view.export_signal.connect(self.handle_export)
        self.view.page_changed_signal.connect(self.handle_page_change)
        self.view.page_size_changed_signal.connect(self.handle_page_size_change)
        self.view.modify_signal.connect(self.show_modify_dialog)
        self.view.view_signal.connect(self.handle_view)
        self.view.import_signal.connect(self.handle_import)
        self.view.delete_signal.connect(self.handle_delete)


    @Slot()
    def load_initial_data(self):
        """加载初始数据"""
        self.load_data()

    def load_data(self):
        """加载数据"""
        try:
            with DatabaseManager.get_session() as session:
                datasets, total, pages = DatasetModel.get_paginated_datasets(
                    session,
                    page=self.current_page,
                    per_page=self.items_per_page
                )
                self.view.update_table(datasets, total, self.current_page, pages)
        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
            self.view.show_error("错误", "加载数据失败")
        finally:
            DatabaseManager.remove_session()

    @Slot(dict)
    def handle_query(self, filters):
        """处理查询请求"""
        self.current_page = 1
        try:
            with DatabaseManager.get_session() as session:
                datasets, total, pages = DatasetModel.get_paginated_datasets(
                    session,
                    page=self.current_page,
                    per_page=self.items_per_page,
                    filters=filters
                )
                self.view.update_table(datasets, total, self.current_page, pages)
        except Exception as e:
            self.logger.error(f"查询失败: {e}")
            self.view.show_error("错误", "查询数据失败")
        finally:
            DatabaseManager.remove_session()

    @Slot()
    def handle_reset(self):
        """处理重置请求"""
        self.current_page = 1
        self.load_data()

    @Slot()
    def show_inset_dialog(self):
        """处理新建数据集请求"""
        from views.dataset.dataset_dialog import DatasetDialog
        dialog = DatasetDialog(self.view,mode="insert")
        dialog.confirm_signal.connect(self.handle_dataset_operation)
        dialog.exec()

    @Slot(str)
    def show_modify_dialog(self,dataset_id):
        """处理修改请求"""
        from views.dataset.dataset_dialog import DatasetDialog
        try:
            with DatabaseManager.get_session() as session:
                dataset = DatasetModel.get_dataset_by_id(session, dataset_id)
                if dataset:
                    dialog = DatasetDialog(self.view, dataset = dataset, mode="modify")
                    dialog.confirm_signal.connect(self.handle_dataset_operation)
                    dialog.exec()
                else:
                    self.logger.warning(f"数据集 {dataset_id} 不存在")
                    self.view.show_error("错误", "数据集不存在")
        except Exception as e:
            self.logger.error(f"获取数据集 {dataset_id} 失败: {e}")
            self.view.show_error("错误", "获取数据集失败")

    @Slot(dict)
    def handle_dataset_operation(self, form_data):
        """处理数据集操作(新增/编辑)"""
        if form_data['dataset_name'] == "":
            self.view.show_error("错误", "数据集名称不能为空")
            # 新增弹窗保留
            self.view.emit_confirm_signal()
            return
        try:
            with DatabaseManager.get_session() as session:
                if form_data['mode'] == "insert":
                    DatasetModel.add_dataset(session, {
                        'dataset_name': form_data['dataset_name'],
                        'dataset_category': form_data['dataset_category'],
                        'status': form_data['status'],
                        'remark': form_data['remark']
                    })
                elif form_data['mode'] == "modify":
                    DatasetModel.update_dataset(session, form_data['dataset_id'], {
                        'dataset_name': form_data['dataset_name'],
                        'dataset_category': form_data['dataset_category'],
                       'status': form_data['status'],
                       'remark': form_data['remark']
                    })
                    self.view.show_message("提示", "数据集修改成功")
                self.load_data()
        except Exception as e:
            self.logger.error(f"数据集操作失败: {e}")
            self.view.show_error("错误", "新增数据集失败" if form_data['mode'] == "insert" else "修改数据集失败")
        finally:
            DatabaseManager.remove_session()

    # @Slot(dict)
    # def modify_dataset_confirm(self, dataset):
    #     """修改数据集"""
    #     try:
    #         with DatabaseManager.get_session() as session:
    #             DatasetModel.update_dataset(session, dataset['id'], {
    #                 'dataset_name': dataset['dataset_name'],    
    #                 'status': DatasetStatus.ENABLED,
    #                 'dataset_category': dataset['dataset_category'],
    #                 'remark': dataset['remark']
    #             })
    #             self.load_data()
    #     except Exception as e:
    #         self.logger.error(f"修改数据集失败: {e}")
    #         self.view.show_error("错误", "修改数据集失败")
    #     finally:
    #         DatabaseManager.remove_session()

    @Slot(int)
    def handle_page_change(self, page):
        """处理页码变化"""
        if page != self.current_page:
            self.current_page = page
            self.load_data()

    @Slot(int)
    def handle_page_size_change(self, size):
        """处理每页条数变化"""
        if size != self.items_per_page:
            self.items_per_page = size
            self.current_page = 1
            self.load_data()

    # 新增导出、查看、导入、删除的槽函数模板
    @Slot()
    def handle_export(self):
        """处理导出请求"""
        self.logger.info("导出功能待实现")
        self.view.show_message("提示", "导出功能暂未实现")

    @Slot(str)
    def handle_view(self, dataset_id):
        """处理查看请求"""
        self.logger.info(f"查看数据集 {dataset_id} 功能待实现")
        self.view.show_message("提示", "查看功能暂未实现")

    @Slot(str)
    def handle_import(self, dataset_id):
        """处理导入请求"""
        self.logger.info(f"导入数据集 {dataset_id} 功能待实现")
        self.view.show_message("提示", "导入功能暂未实现")

    @Slot(str)
    def handle_delete(self, dataset_id):
        """处理删除请求"""
        self.logger.info(f"删除数据集 {dataset_id} 功能待实现")
        self.view.show_message("提示", "删除功能暂未实现")