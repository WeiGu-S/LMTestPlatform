from functools import partial
from itertools import count
from PySide6.QtCore import QObject, Slot
from controllers import data_controller
from models.enum import DataType, QuestionLabel, QuestionType
from utils.database import DatabaseManager
from utils.logger import get_logger
from views.dataset.data_collection_view import DataCollectionView
from models.data_collection_model import DataCollectionModel
from datetime import datetime, timezone, timedelta
from views.dataset.data_collection_dialog import DataCollectionDialog
from views.dataset.data_collection_details_dialog import DataCollectionDetailsDialog
from views.dataset.import_dialog import ImportDialog
from models.data_collection_son_model import DataModel
from functools import partial
from controllers.data_controller import DataController


logger = get_logger("data_collection_controller")

class DataCollectionController(QObject):
    def __init__(self, view: DataCollectionView):
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
        self.view.insert_signal.connect(self.show_data_collection_dialog)
        self.view.export_signal.connect(self.handle_export)
        self.view.page_changed_signal.connect(self.handle_page_change)
        self.view.edit_signal.connect(self.show_data_collection_dialog)
        self.view.view_signal.connect(self.show_data_collection_details_dialog)
        self.view.import_signal.connect(self.show_import_dialog)
        self.view.delete_signal.connect(self.handle_delete)
        self.view.delete_confirm_signal.connect(self.delete_data_collection)

    @Slot()
    def load_initial_data(self):
        """加载初始数据"""
        self.load_data()

    def load_data(self,filtes=None):
        """加载数据"""
        logger.info("加载数据")
        try:
            with DatabaseManager.get_session() as session:
                data_collections, total_items, total_pages = DataCollectionModel.get_paginated_data_collections(
                    session,
                    page=self.current_page,
                    per_page=self.items_per_page,
                    filters=filtes
                )
                logger.info(f"data_collections:{data_collections}")
                self.view.update_table(data_collections, total_items, self.current_page, total_pages)
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
            self.load_data(filters)
        except Exception as e:
            self.logger.error(f"查询失败: {e}")
            self.view.show_error("错误", "查询数据失败")
        finally:
            DatabaseManager.remove_session()

    @Slot()
    def handle_reset(self):
        """处理重置请求"""
        # 重置所有过滤器  
        self.current_page = 1
        self.load_data()

    @Slot(str)
    def show_data_collection_dialog(self, collection_id=None):
        """显示数据集对话框,处理新建和修改请求"""
        try:
            data_collection = None
            mode = "insert"
            
            if collection_id is not None:
                with DatabaseManager.get_session() as session:
                    data_collection = DataCollectionModel.get_data_collection_by_id(session, int(collection_id))
                    if not data_collection:
                        self.logger.warning(f"数据集 {collection_id} 不存在")
                        self.view.show_error("错误", "数据集不存在")
                        return
                mode = "edit"
                    
            dialog = DataCollectionDialog(self.view, data_collection=data_collection, mode=mode)
            dialog.confirmed.connect(self.handle_data_collection_operation)
            dialog.exec()
            
        except Exception as e:
            if collection_id:
                self.logger.error(f"获取数据集 {collection_id} 失败: {e}")
                self.view.show_error("错误", "获取数据集失败")

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
                        self.view.show_message("提示", "数据集新增成功")
                    except Exception as add_error:
                        session.rollback()
                        self.logger.error(f"新增数据集失败: {add_error}")
                        self.view.show_error("错误", str(add_error))
                        return
                elif form_data['mode'] == "edit":
                    try:
                        DataCollectionModel.update_data_collection(session, form_data['collection_id'], {
                            'project_name': form_data['project_name'],
                            'collection_name': form_data['collection_name']
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
    def show_data_collection_details_dialog(self, collection_id):
        """处理查看请求"""
        data_collection = DataCollectionModel.get_data_collection_by_id(DatabaseManager.get_session(), int(collection_id))
        dialog = DataCollectionDetailsDialog(data_collection=data_collection,parent=self.view,collection_id=collection_id)
        data_controller=DataController(dialog, collection_id)
        dialog.exec()

    # 新增导出、查看、导入、删除的槽函数模板
    @Slot()
    def handle_export(self):
        """处理导出请求"""
        self.logger.info("导出功能待实现")
        self.view.show_message("提示", "导出功能暂未实现")

    @Slot()
    def show_import_dialog(self, collection_id):
        """处理导入请求"""
        dialog = ImportDialog(self.view, collection_id)
        # dialog.update_import_table()
        dialog.import_confirmed.connect(lambda datas:self.import_data(collection_id, datas))
        dialog.exec()

    @Slot(int,list)
    def import_data(self, collection_id, datas):
        """导入数据"""
        # 实现导入逻辑
        self.logger.info(f"导入数据到数据集 {collection_id},datas : {datas}")
        try:
            with DatabaseManager.get_session() as session:
                for data in datas:
                    data['collection_id'] = collection_id
                    data['data_type'] = data.get('data_type', '')
                    data['context'] = data.get('context', '') if data.get('context', '') else ''
                    data['question'] = data.get('question', '')
                    data['answer'] = data.get('answer', '')
                    data['quesiton_type'] = data.get('quesiton_type', '')
                    data['question_label'] = data.get('question_label', '')
                    DataModel.add_data(session, data, collection_id)
                    session.commit()
                self.view.show_message("提示", "数据导入成功")
                self.load_data()
                
        except Exception as e:
            self.logger.error(f"导入数据失败: {e}")
            self.view.show_error("错误", f"导入数据失败: {e}")
        finally:
            DatabaseManager.remove_session()

    @Slot(str)
    def handle_delete(self, collection_id):
        """处理删除请求"""
        data_collection = DataCollectionModel.get_data_collection_by_id(DatabaseManager.get_session(), int(collection_id))
        collection_name = data_collection.collection_name
        self.view.ask_for_confirmation("删除数据集", f"确定要删除数据集: \n{collection_name} 吗？",collection_id) 

    @Slot()
    def delete_data_collection(self, collection_id):
        """删除数据集"""
        if collection_id:
            collection_name = DataCollectionModel.get_data_collection_by_id(DatabaseManager.get_session(), int(collection_id)).collection_name
            try:
                with DatabaseManager.get_session() as session:
                    DataModel.delete_datas(session, collection_id)
                    DataCollectionModel.delete_data_collection(session, collection_id)
                    session.commit()
                    self.view.show_message("提示", f"数据集:{collection_name}删除成功")
                    self.load_data()

            except Exception as e:
                self.logger.error(f"删除数据集 {collection_id} 失败: {e}")
                self.view.show_error("错误", "删除数据集失败")
        
    @Slot(int)
    def handle_page_change(self, page):
        """处理页码变化"""
        self.current_page = page
        self.load_data()