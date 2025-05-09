from functools import partial
from itertools import count
from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QMessageBox
from models.enum import DataType, QuestionLabel, QuestionType
from utils.database import DatabaseManager
from utils.logger import get_logger
from views.dataset import data_collection_details_dialog
from models.data_collection_model import DataCollectionModel
from datetime import datetime, timezone, timedelta
from views.dataset.data_collection_dialog import DataCollectionDialog
from views.dataset.import_dialog import ImportDialog
from models.data_collection_son_model import DataModel
from functools import partial
from views.dataset.data_operate_dialog import DataDialog

logger = get_logger("data_controller")

class DataController(QObject):
    def __init__(self, view, collection_id):
        super().__init__()
        self.view = view
        self.collection_id = collection_id
        self.logger = get_logger(__name__)
        self.current_page = 1
        self.items_per_page = 10
        self.connect_signals()
        self.load_initial_data()

    def connect_signals(self):
        """连接所有信号"""
        self.view.query_signal.connect(self.handle_query)
        self.view.reset_signal.connect(self.handle_reset)
        self.view.data_operate_signal.connect(self.show_data_operate_dialog)
        self.view.data_delete_signal.connect(self.handle_delete)
        self.view.page_changed_signal.connect(self.handle_page_change)
        self.view.data_delete_confirmed_signal.connect(self.delete_data)
        self.view.insert_signal.connect(self.show_data_operate_dialog)

    @Slot()
    def load_initial_data(self):
        """加载初始数据"""
        self.load_data()

    def load_data(self, filtes=None):
        """加载数据"""
        logger.info("加载数据")
        try:
            with DatabaseManager.get_session() as session:
                datas, total_items, total_pages = DataModel.get_paginated_data(
                    session=session,
                    collection_id=self.collection_id,
                    page=self.current_page,
                    per_page=self.items_per_page,
                    filters=filtes
                )
                print(f"datas:{datas}")
                print(f"filters:{filtes}")
                self.view.load_table_data(datas, total_items, self.current_page, total_pages)
                print(f"total_items:{total_items},total_pages:{total_pages},self.current_page:{self.current_page}")
        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
            self.view.show_message("error", "错误", "加载数据失败")
        finally:
            DatabaseManager.remove_session()

    @Slot(dict)
    def handle_query(self, filters):
        """处理查询请求"""
        self.current_page = 1
        try:
            self.load_data(filters)
        except Exception as e:
            self.logger.error(f"查询失败: {e}")
            # self.view.show_message("error", "错误", "查询数据失败")
        finally:
            DatabaseManager.remove_session()

    @Slot()
    def handle_reset(self):
        """处理重置请求"""
        # 重置所有过滤器  
        self.current_page = 1
        self.load_data()

    @Slot(str)
    def show_data_operate_dialog(self, data_id=None):
        """显示数据对话框,处理新建和修改请求"""
        print(f"对话框data_id:{data_id}")
        try:
            data = {}
            mode = "insert"
            
            if data_id is not None:
                with DatabaseManager.get_session() as session:
                    data = DataModel.get_data_by_id(data_id)
                    if not data:
                        self.logger.warning(f"数据 {data_id} 不存在")
                        self.view.show_message("error", "错误", "数据不存在")
                        return
                mode = "edit"
                data['collection_id'] = self.collection_id
            # print(f"collection_id:{data['colletion_id']}")
            dialog = DataDialog(self.view, data=data, mode=mode)
            dialog.confirmed.connect(self.handle_data_operation)
            dialog.exec()
            
        except Exception as e:
            if data_id:
                self.logger.error(f"获取数据 {data_id} 失败: {e}")
                self.view.show_message("error", "错误", "获取数据集失败")

    @Slot(dict)
    def handle_data_collection_operation(self, form_data):
        """处理数据集操作(新增/编辑)"""
        try:
            with DatabaseManager.get_session() as session:
                if form_data['mode'] == "insert":
                    try:
                        DataCollectionModel.add_data_collection(session, {
                            'project_name': form_data['project_name'],
                            'collection_name': form_data['collection_name']
                        })
                        session.commit()
                        self.view.show_message("info", "提示", "数据集新增成功")
                    except Exception as add_error:
                        session.rollback()
                        self.logger.error(f"新增数据集失败: {add_error}")
                        self.view.show_message("error", "错误", str(add_error))
                        return
                elif form_data['mode'] == "edit":
                    try:
                        DataCollectionModel.update_data_collection(session, form_data['collection_id'], {
                            'project_name': form_data['project_name'],
                            'collection_name': form_data['collection_name']
                        })
                        self.view.show_message("info", "提示", "数据集修改成功")
                    except Exception as update_error:
                        self.logger.error(f"修改数据集失败: {update_error}")
                        self.view.show_message("error", "错误", str(update_error))
                        return
                self.load_data()
        except Exception as e:
            self.logger.error(f"数据集操作失败: {e}")
            self.view.show_message("error", "错误", "数据集操作失败")
        finally:
            DatabaseManager.remove_session()
            
    @Slot(dict)
    def handle_data_operation(self, form_data):
        """处理数据操作(新增/编辑)"""
        try:
            with DatabaseManager.get_session() as session:
                if form_data['mode'] == "insert":
                    try:
                        DataModel.add_data(session, {
                            'collection_id': self.collection_id,
                            'data_type': form_data['data_type'],
                            'question_type': form_data['question_type'],
                            'question_label': form_data['question_label'],
                            'context': form_data['context'],
                            'question': form_data['question'],
                            'answer': form_data['answer']
                        }, self.collection_id)
                        session.commit()
                        self.view.show_message("info", "提示", "数据新增成功")
                    except Exception as add_error:
                        session.rollback()
                        self.logger.error(f"新增数据失败: {add_error}")
                        self.view.show_message("error", "错误", str(add_error))
                        return
                elif form_data['mode'] == "edit":
                    try:
                        DataModel.update_data(session, form_data['data_id'], {
                            'data_type': form_data['data_type'],
                            'question_type': form_data['question_type'],
                            'question_label': form_data['question_label'],
                            'context': form_data['context'],
                            'question': form_data['question'],
                            'answer': form_data['answer']
                        })
                        self.view.show_message("info", "提示", "数据修改成功")
                    except Exception as update_error:
                        self.logger.error(f"修改数据失败: {update_error}")
                        self.view.show_message("error", "错误", str(update_error))
                        return
                self.load_data()
        except Exception as e:
            self.logger.error(f"数据操作失败: {e}")
            self.view.show_message("error", "错误", "数据操作失败")
        finally:
            DatabaseManager.remove_session()

    @Slot(str)
    def show_data_collection_details_dialog(self, collection_id):
        """处理查看请求"""
        data_collection = DataCollectionModel.get_data_collection_by_id(DatabaseManager.get_session(), int(collection_id))
        dialog = DataCollectionDetailsDialog(data_collection=data_collection,parent=self.view,collection_id=collection_id)
        dialog.exec()

    @Slot()
    def handle_export(self):
        """处理导出请求"""
        self.logger.info("导出功能待实现")
        self.view.show_message("info", "提示", "导出功能暂未实现")

    @Slot(str)
    def handle_delete(self, data_id):
        """处理删除请求"""
        print(f"删除data_id:{data_id}")
        self.view.ask_for_confirmation("删除数据集", f"确定要删除该数据吗？",data_id) 

    @Slot(str)
    def delete_data(self, data_id):
        """删除数据"""
        if data_id:
            try:
                # 执行删除操作
                DataModel.delete_data(data_id)
                self.view.show_message("info", "提示", f"删除成功!")
                self.load_data()

            except Exception as e:
                self.logger.error(f"删除数据 {data_id} 失败: {e}")
                self.view.show_message("error", "错误", "删除数据失败")
            finally:
                DatabaseManager.remove_session()
        
    @Slot(int)
    def handle_page_change(self, page):
        """处理页码变化"""
        print(f"Changing page: {self.current_page} -> {page}")
        self.current_page = page
        self.load_data()
