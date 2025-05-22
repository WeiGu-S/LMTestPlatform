from crypt import methods
from functools import partial
from itertools import count
from PySide6.QtCore import QObject, Slot
from controllers import data_controller
from models.bigModels_model import BigModelsModel
from models.enum import DataType, QuestionLabel, QuestionType
from utils.database import DatabaseManager
from utils.logger import get_logger
from datetime import datetime, timezone, timedelta
from functools import partial
from views.model_config.model_config_dialog import ModelConfigDialog
from views.model_config.model_config_view import ModelConfigView
import requests
import json


logger = get_logger("model_controller")

class ModelsController(QObject):
    def __init__(self, view: ModelConfigView):
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
        self.view.model_insert_signal.connect(self.show_model_config_dialog)
        self.view.export_signal.connect(self.handle_export)
        self.view.page_changed_signal.connect(self.handle_page_change)
        self.view.edit_signal.connect(self.show_model_config_dialog)
        self.view.delete_signal.connect(self.handle_delete)
        self.view.delete_confirm_signal.connect(self.delete_model)
        self.view.call_signal.connect(self.call_model)

    def load_initial_data(self):
        """加载初始数据"""
        self.load_data()

    def load_data(self, filters=None):
        """加载数据"""
        logger.info("加载数据")
        try:
            with DatabaseManager.get_session() as session:
                models, total_items, total_pages = BigModelsModel.get_paginated_models(
                    session,
                    page=self.current_page,
                    per_page=self.items_per_page,
                    filters=filters
                )
                logger.info(f"models:{models}")
                self.view.update_table(models, total_items, self.current_page, total_pages)
        except Exception as e:
            self.logger.error(f"加载数据失败: {e}")
            self.view.show_message("错误", "加载数据失败", 'error')
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
            self.view.show_message("错误", "查询数据失败", 'error')
        finally:
            DatabaseManager.remove_session()

    @Slot()
    def handle_reset(self):
        """处理重置请求"""
        # 重置所有过滤器  
        self.current_page = 1
        self.load_data()

    @Slot(str)
    def show_model_config_dialog(self, config_id=None):
        """显示模型对话框,处理新建和修改请求"""
        try:
            model = None
            mode = "insert"
            
            if config_id is not None:
                with DatabaseManager.get_session() as session:
                    model = BigModelsModel.get_model_info_by_id(session, config_id).to_dict()
                    if not model:
                        self.logger.warning(f"模型 {config_id} 不存在")
                        self.view.show_message('error', "错误", "模型不存在")
                        return
                mode = "edit"
                    
            dialog = ModelConfigDialog(self.view, model_data=model, mode=mode)
            dialog.confirmed.connect(self.handle_model_operation)
            dialog.exec()
            
        except Exception as e:
            if config_id:
                self.logger.error(f"获取模型配置 {config_id} 失败: {e}")
                self.view.show_message('error', "错误", "获取模型配置失败")
            else:
                self.logger.error(f"显示新增模型对话框失败: {e}")
                self.view.show_message('error', "错误", "显示新增模型对话框失败")

    @Slot(dict)
    def handle_model_operation(self, form_data):
        """处理模型操作(新增/编辑)"""
        try:
            with DatabaseManager.get_session() as session:
                if form_data['mode'] == "insert":
                    try:
                        BigModelsModel.add_model(session, {
                            'model_name': form_data['model_name'],
                            'model_type': form_data['model_type'],
                            'config_type': form_data['config_type'],
                            'is_stream': form_data['is_stream'],
                            'url_info': form_data['url_info'],
                            'headers': form_data['headers'],
                            'body': form_data['body'],
                            'res_path': form_data['res_path']
                        })
                        session.commit()
                        self.view.show_message('info', "提示", "模型新增成功")
                    except Exception as add_error:
                        session.rollback()
                        self.logger.error(f"新增模型失败: {add_error}")
                        self.view.show_message('error', "错误", str(add_error))
                        return
                elif form_data['mode'] == "edit":
                    try:
                        BigModelsModel.update_model_info(session, form_data['config_id'], {
                            'model_name': form_data['model_name'],
                            'model_type': form_data['model_type'],
                            'config_type': form_data['config_type'],
                            'is_stream': form_data['is_stream'],
                            'url_info': form_data['url_info'],
                            'headers': form_data['headers'],
                            'body': form_data['body'],
                            'res_path': form_data['res_path']
                        })
                        self.view.show_message('info', "提示", "模型修改成功")
                    except Exception as update_error:
                        self.logger.error(f"修改模型失败: {update_error}")
                        self.view.show_message('error', "错误", str(update_error))
                        return
                self.load_data()
        except Exception as e:
            self.logger.error(f"模型操作失败: {e}")
            self.view.show_message('error', "错误", "模型操作失败")
        finally:
            DatabaseManager.remove_session()

    # 新增导出、查看、导入、删除的槽函数模板
    @Slot()
    def handle_export(self):
        """处理导出请求"""
        self.logger.info("导出功能待实现")
        self.view.show_message("提示", "导出功能暂未实现")

    @Slot(str)
    def handle_delete(self, config_id):
        """处理删除请求"""
        try:
            with DatabaseManager.get_session() as session:
                model = BigModelsModel.get_model_info_by_id(session, int(config_id))
                if model:
                    model_name = model.model_name
                    self.view.ask_for_confirmation("删除模型", f"确定要删除模型: \n{model_name} 吗？", config_id)
                else:
                    self.view.show_message("错误", "模型不存在", 'error')
        except Exception as e:
            self.logger.error(f"获取待删除模型信息失败: {e}")
            self.view.show_message("错误", "获取模型信息失败", 'error')

    @Slot()
    def delete_model(self, config_id):
        """删除模型"""
        if config_id:
            try:
                with DatabaseManager.get_session() as session:
                    model = BigModelsModel.get_model_info_by_id(session, int(config_id))
                    if not model:
                        self.view.show_message('error',"错误", "模型不存在")
                        return
                    model_name = model.model_name
                    BigModelsModel.delete_model(session, config_id)
                    session.commit()
                    self.view.show_message('info', "提示", f"模型:{model_name}删除成功")
                    self.load_data()
            except Exception as e:
                self.logger.error(f"删除模型 {config_id} 失败: {e}")
                self.view.show_message('error', "错误", "删除模型失败")
        
    @Slot(int)
    def handle_page_change(self, page):
        """处理页码变化"""
        self.current_page = page
        self.load_data()

    @Slot(str)
    def call_model(self, config_id):
        """调用模型"""
        try:
            with DatabaseManager.get_session() as session:
                model = BigModelsModel.get_model_info_by_id(session, int(config_id)).to_dict()
                if not model:
                    self.view.show_message('error',"错误", "模型不存在")
                    return
                url = model['url_info']
                headers = json.loads(model['headers'])
                body = json.loads(model['body'])
            response = requests.post(url=url, headers=headers, json=body)
            if response.status_code == 200:
                self.view.show_message('info', "提示", f"接口调用成功")
                return response.json()
            else:
                self.view.show_message('error', "错误", f"接口调用失败: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"调用模型 {config_id} 失败: {e}")
            self.view.show_message('error', "错误", f"调用模型失败:{e}")