from re import S
from models.dataset_model import DatasetModel
from utils.database import DatabaseManager
from utils.logger import get_logger
from PySide6.QtCore import QObject, Slot, QDate
from datetime import datetime
from views.dataset.import_dialog import ImportDialog
from views.dataset.dataset_view import DatasetView

logger = get_logger("dataset_controller")
class DatasetController(QObject):
    def __init__(self, view):
        super().__init__()
        self.view = view
        # self.session = DatabaseManager.get_session() # 每次操作时获取 Session
        self.logger = get_logger()
        # 此处无需检查 session，获取时会自动检查
        self.logger.info("DatasetController 初始化完成")
        self.current_page = 1
        # 从视图获取初始每页条数
        self.items_per_page = 10
        self.connect_signals()
        self.load_initial_data() # 加载初始数据

    def connect_signals(self):
        """连接界面信号与控制器槽函数"""
        self.view.query_button.clicked.connect(self.query_data)
        self.view.reset_button.clicked.connect(self.reset_filters)
        self.view.new_button.clicked.connect(self.create_new_dataset)
        self.view.export_button.clicked.connect(self.export_data)
        self.view.prev_button.clicked.connect(self.prev_page)
        self.view.next_button.clicked.connect(self.next_page)
        self.view.page_combo.currentIndexChanged.connect(self.go_to_specific_page)
        # 连接分页控件信号
        self.view.page_combo.currentIndexChanged.connect(self.go_to_page_from_combo)
        #self.view.page_size_combo.currentIndexChanged.connect(self.change_page_size)
        # TODO: 连接表格内操作按钮信号（需视图暴露或通过控制器传递）
        # 示例：self.view.dataset_table.cellWidget(row, 6).findChild(QPushButton, "modify_button").clicked.connect(...)
        # 连接表格内操作按钮信号
        self.view.dataset_table.cellWidget(row, 6).findChild(QPushButton, "modify_button").clicked.connect(self.modify_dataset)

    @Slot()
    def load_initial_data(self):
        """加载初始数据，如设置默认日期并加载第一页"""
        # 设置默认日期范围（如有需要）
        # self.view.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        # self.view.end_date_edit.setDate(QDate.currentDate())
        self.load_data()

    @Slot()
    def load_data(self):
        """加载初始或过滤后的数据到表格"""
        filters = self.get_filters()
        self.logger.info(f"加载数据，过滤条件: {filters}, 页码: {self.current_page}, 每页: {self.items_per_page}")
        try:
            with DatabaseManager.get_session() as session:
                # 假设模型返回 (data_list, total_items, total_pages)
                data, total_items, total_pages = DatasetModel.get_paginated_datasets(
                    session,
                    page=self.current_page,
                    per_page=self.items_per_page,
                    filters=filters
                )
                self.logger.info(f"加载数据集 {len(data)} 条，总数: {total_items}，总页数: {total_pages}")
                # 调用更新后的 update_table 方法
                self.view.update_table(data, total_items, self.current_page, total_pages)
        except Exception as e:
            self.logger.error(f"加载数据出错: {e}", exc_info=True)
            # 可在界面提示错误
            self.view.update_table([], 0, 1, 1)
        finally:
            DatabaseManager.remove_session() # 操作后确保移除 session

    def get_filters(self):
        """从界面收集过滤条件"""
        filters = {
            'dataset_name': self.view.name_filter_input.text().strip(),
            'status': self.view.status_filter_combo.currentText(),
            'dataset_category': self.view.category_filter_combo.currentText(),
            # 仅在日期有效时传递
            'start_date': self.view.start_date_edit.date().toPython() if self.view.start_date_edit.date().isValid() else None,
            'end_date': self.view.end_date_edit.date().toPython() if self.view.end_date_edit.date().isValid() else None,
        }
        # 清理空值和“全部”过滤条件
        cleaned_filters = {}
        for k, v in filters.items():
            if v is not None and v != '':
                if k in ['status', 'dataset_category'] and v == '全部':
                    continue # 不传递“全部”作为过滤条件
                cleaned_filters[k] = v
        return cleaned_filters

    @Slot()
    def query_data(self):
        """查询按钮点击槽函数"""
        self.current_page = 1 # 查询后重置到第一页
        self.load_data()

    @Slot()
    def reset_filters(self):
        """重置筛选条件槽函数"""
        self.view.name_filter_input.clear()
        self.view.status_filter_combo.setCurrentIndex(0) # 假设“全部”在索引 0
        self.view.category_filter_combo.setCurrentIndex(0) # 假设“全部”在索引 0
        # 重置为默认日期或清空
        self.view.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.view.end_date_edit.setDate(QDate.currentDate())
        self.current_page = 1 # 重置到第一页
        self.load_data()

    @Slot()
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    @Slot()
    def next_page(self):
        """下一页"""
        # 需要知道总页数以判断是否能到下一页
        # 该逻辑在 load_data 后由 view.update_table 更新按钮状态
        # 此处只需增加页码并加载
        self.current_page += 1
        self.load_data()

    @Slot(int)
    def go_to_page_from_combo(self, index):
        """通过下拉框跳转到指定页。"""
        if index >= 0:
            try:
                page_num = int(self.view.page_combo.itemText(index))
                if page_num != self.current_page:
                    self.current_page = page_num
                    self.load_data()
            except ValueError:
                self.logger.warning(f"选择了无效页码: {self.view.page_combo.itemText(index)}")
    @Slot(int)
    def go_to_specific_page(self, page_num):
        """跳转到指定页（页码按钮点击）。"""
        if page_num != self.current_page:
            self.logger.info(f"跳转到第 {page_num} 页")
            self.current_page = page_num
            self.load_data()

    # @Slot(int)
    # def change_page_size(self, index):
    #     """更改每页显示条数。"""
    #     try:
    #         new_page_size = int(self.view.page_size_combo.itemText(index))
    #         if new_page_size != self.items_per_page:
    #             self.items_per_page = new_page_size
    #             self.current_page = 1 # 页大小改变，重置到第一页
    #             self.logger.info(f"每页条数更改为: {self.items_per_page}")
    #             self.load_data()
    #     except ValueError:
    #         self.logger.warning(f"选择了无效的每页条数: {self.view.page_size_combo.itemText(index)}")

    @Slot()
    def create_new_dataset(self):
        """新建数据集按钮点击槽函数。"""
        self.logger.info("点击了新建数据集按钮")
        # 导入DatasetDialog
        from views.dataset.dataset_dialog import DatasetDialog
        # 创建对话框实例
        dialog = DatasetDialog(self.view)
        # 连接确认和取消按钮的信号
        dialog.confirm_btn.clicked.connect(lambda: self.handle_dataset_confirm(dialog))
        dialog.cancel_btn.clicked.connect(dialog.close)
        # 显示对话框
        dialog.exec()  # 使用exec()替代show()，使对话框成为模态对话框
        
    def handle_dataset_confirm(self, dialog):
        """处理数据集对话框确认按钮点击"""
        try:
            if dialog.name_input.text().strip() == '':
                self.logger.warning("数据集名称不能为空")
                return
            # 获取对话框中的数据
            dataset_data = {
                'dataset_name': dialog.name_input.text(),
                'dataset_category': dialog.category_combo.currentText(),            
                'status': dialog.status_combo.currentText() if hasattr(dialog, 'status_combo') else '启用',
                'remark': dialog.desc_input.toPlainText()
            }
            
            self.logger.info(f"创建新数据集: {dataset_data}")
            # 调用模型创建数据集
            with DatabaseManager.get_session() as session:
                DatasetModel.add_dataset(session, dataset_data)
        except Exception as e:
            self.logger.error(f"创建数据集失败: {e}", exc_info=True)

        
        # 关闭对话框
        dialog.close()
        # 刷新数据列表
        self.load_data()
    @Slot()    
    def handle_dataset_cancel(self, dialog):
        """处理数据集对话框取消按钮点击"""
        self.logger.info("点击了取消按钮")
        dialog.close()

    @Slot()
    def export_data(self):
        """导出数据按钮点击槽函数（待实现）。"""
        self.logger.info("点击了导出数据按钮（待实现）")
        # 1. 获取当前筛选条件
        filters = self.get_filters()
        # 2. 弹出文件保存对话框 (可以使用 view 的 show_export_dialog)
        # file_path = self.view.show_export_dialog()
        # if file_path:
        #    try:
        #        with DatabaseManager.get_session() as session:
        #            # 3. 调用 model 获取所有符合条件的数据（不分页）
        #            all_data = Dataset.get_all_datasets(session, filters=filters)
        #        # 4. 实现导出逻辑 (e.g., to CSV, Excel)
        #        self.logger.info(f"准备导出 {len(all_data)} 条数据到 {file_path}")
        #        # ... export logic ...
        #    except Exception as e:
        #        self.logger.error(f"导出数据时出错: {e}", exc_info=True)
        #        # Show error message
        #    finally:
        #        DatabaseManager.remove_session()
        #    # ... export logic ...
        pass

    # --- 新增：处理表格内按钮点击 --- (需要 view 配合传递信号或行号)
    @Slot(int)
    def modify_item(self, row_index):
        """处理修改按钮点击 (示例)"""
        dataset_id = self.view.dataset_table.item(row_index, 0).text() # 获取ID
        self.logger.info(f"请求修改行 {row_index}, ID: {dataset_id} (待实现)")
        # 弹出编辑对话框，加载对应 ID 的数据
        # ... dialog logic ...
        # if dialog.exec():
        #    # ... update model ...
        #    self.load_data() # 刷新

    @Slot(int)
    def view_item(self, row_index):
        """处理查看按钮点击 (示例)"""
        dataset_id = self.view.dataset_table.item(row_index, 0).text() # 获取ID
        self.logger.info(f"请求查看行 {row_index}, ID: {dataset_id} (待实现)")
        # 弹出只读详情对话框或导航到详情页
        # ... view/dialog logic ...

    @Slot(int)
    def import_item(self, row_index):
        """处理导入按钮点击 (示例)"""
        dataset_id = self.view.dataset_table.item(row_index, 0).text() # 获取ID
        self.logger.info(f"请求导入行 {row_index}, ID: {dataset_id} (待实现)")
        # 弹出导入对话框
        import_dialog = ImportDialog(self.view, dataset_id)
        import_dialog.exec()
    @Slot(int)
    def delete_item(self, row_index):
        """处理删除按钮点击 (示例)"""
        dataset_id = self.view.dataset_table.item(row_index, 0).text() # 获取ID
        self.logger.info(f"请求删除行 {row_index}, ID: {dataset_id} (待实现)")
        # 弹出确认对话框
        #... confirm dialog logic...
        
        if confirmed:
           with DatabaseManager.get_session() as session:
               # 调用模型删除数据
               Dataset.delete_dataset(session, dataset_id)
           self.load_data() # 刷新

    # def close_app(self):
    #     """应用关闭处理 - Session management is now handled per operation or via remove_session."""
    #     self.logger.info("控制器清理")
    #     DatabaseManager.remove_session() # Ensure session is removed if app closes unexpectedly
        # self.view.close() # 通常由主应用循环处理
