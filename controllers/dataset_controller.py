from PySide6.QtCore import QObject, Slot
from utils.database import DatabaseManager
from utils.logger import get_logger
from views.dataset.dataset_view import DatasetView
from models.dataset_model import DatasetModel, DatasetStatus
from datetime import datetime, timezone, timedelta
from views.dataset.dataset_dialog import DatasetDialog
from views.dataset.dataset_details_dialog import DatasetDetailsDialog
from views.dataset.import_dialog import ImportDialog


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
        self.view.insert_signal.connect(self.show_dataset_dialog)
        self.view.export_signal.connect(self.handle_export)
        self.view.page_changed_signal.connect(self.handle_page_change)
        self.view.page_size_changed_signal.connect(self.handle_page_size_change)
        self.view.edit_signal.connect(self.show_dataset_dialog)
        self.view.view_signal.connect(self.show_dataset_details_dialog)
        self.view.import_signal.connect(self.show_import_dialog)
        self.view.delete_signal.connect(self.handle_delete)
        self.view.delete_confirm_signal.connect(self.delete_dataset)

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
                print(f"datasets:{datasets}")
                self.view.update_table(datasets, total, self.current_page, pages)
        except Exception as e:
            self.logger.error(f"查询失败: {e}")
            self.view.show_error("错误", "查询数据失败")
        finally:
            DatabaseManager.remove_session()

    @Slot()
    def handle_reset(self):
        """处理重置请求"""
        # 重置所有过滤器
        self.load_data()

    @Slot(str)
    def show_dataset_dialog(self, dataset_id=None):
        """显示数据集对话框,处理新建和修改请求"""
        try:
            dataset = None
            mode = "insert"
            
            if dataset_id is not None:
                with DatabaseManager.get_session() as session:
                    dataset = DatasetModel.get_dataset_by_id(session, int(dataset_id))
                    if not dataset:
                        self.logger.warning(f"数据集 {dataset_id} 不存在")
                        self.view.show_error("错误", "数据集不存在")
                        return
                mode = "modify"
                    
            dialog = DatasetDialog(self.view, dataset=dataset, mode=mode)
            dialog.confirmed.connect(self.handle_dataset_operation)
            dialog.exec()
            
        except Exception as e:
            if dataset_id:
                self.logger.error(f"获取数据集 {dataset_id} 失败: {e}")
                self.view.show_error("错误", "获取数据集失败")

    @Slot(dict)
    def handle_dataset_operation(self, form_data):
        """处理数据集操作(新增/编辑)"""
        try:
            with DatabaseManager.get_session() as session:
                if form_data['mode'] == "insert":
                    try:
                        DatasetModel.add_dataset(session, {
                            'dataset_name': form_data['dataset_name'],
                            'dataset_category': form_data['dataset_category'],
                            'status': form_data['status'],
                            'remark': form_data['remark']
                        })
                        session.commit()
                        self.view.show_message("提示", "数据集新增成功")
                    except Exception as add_error:
                        session.rollback()
                        self.logger.error(f"新增数据集失败: {add_error}")
                        self.view.show_error("错误", str(add_error))
                        return
                elif form_data['mode'] == "modify":
                    try:
                        DatasetModel.update_dataset(session, form_data['dataset_id'], {
                            'dataset_name': form_data['dataset_name'],
                            'dataset_category': form_data['dataset_category'],
                            'status': form_data['status'],
                            'remark': form_data['remark']
                        })
                        self.view.show_message("提示", "数据集修改成功")
                    except Exception as update_error:
                        self.logger.error(f"修改数据集失败: {update_error}")
                        self.view.show_error("错误", str(update_error))
                        return
                self.load_data()
        except Exception as e:
            self.logger.error(f"数据集操作失败: {e}")
            self.view.show_error("错误", "数据集操作失败")
        finally:
            DatabaseManager.remove_session()

    @Slot(str)
    def show_dataset_details_dialog(self, dataset_id):
        """处理查看请求"""
        dataset = DatasetModel.get_dataset_by_id(DatabaseManager.get_session(), int(dataset_id))
        dialog = DatasetDetailsDialog(dataset,self.view)
        dialog.exec()

    # 新增导出、查看、导入、删除的槽函数模板
    @Slot()
    def handle_export(self):
        """处理导出请求"""
        self.logger.info("导出功能待实现")
        self.view.show_message("提示", "导出功能暂未实现")


    @Slot(str)
    def show_import_dialog(self, dataset_id):
        """处理导入请求"""
        dialog = ImportDialog(self.view, dataset_id)
        dialog.import_confirmed.connect(self.import_data)
        dialog.exec()

    def import_data(self, dataset_id, file_path):
        """导入数据"""
        # 实现导入逻辑
        self.logger.info(f"导入数据到数据集 {dataset_id}，文件路径: {file_path}")

    @Slot(str)
    def handle_delete(self, dataset_id):
        """处理删除请求"""
        dataset = DatasetModel.get_dataset_by_id(DatabaseManager.get_session(), int(dataset_id))
        dataset_name = dataset.dataset_name
        self.view.ask_for_confirmation("删除数据集", f"确定要删除数据集: \n{dataset_name} 吗？",dataset_id) 

    @Slot()
    def delete_dataset(self, dataset_id):
        """删除数据集"""
        if dataset_id:
            dataset_name = DatasetModel.get_dataset_by_id(DatabaseManager.get_session(), int(dataset_id)).dataset_name
            try:
                with DatabaseManager.get_session() as session:
                    DatasetModel.delete_dataset(session, dataset_id)
                    session.commit()
                    self.view.show_message("提示", f"数据集:{dataset_name}删除成功")
                    self.load_data()

            except Exception as e:
                self.logger.error(f"删除数据集 {dataset_id} 失败: {e}")
                self.view.show_error("错误", "删除数据集失败")
        
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