from models.dataset_model import DatasetModel
from utils.database import DatabaseManager
from utils.logger import get_logger
from PySide6.QtCore import QObject, Slot, QDate
from datetime import datetime

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
        # 连接分页控件信号
        self.view.page_combo.currentIndexChanged.connect(self.go_to_page_from_combo)
        #self.view.page_size_combo.currentIndexChanged.connect(self.change_page_size)
        # TODO: 连接表格内操作按钮信号（需视图暴露或通过控制器传递）
        # 示例：self.view.dataset_table.cellWidget(row, 6).findChild(QPushButton, "modify_button").clicked.connect(...)

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

    # 如果需要通过页码按钮跳转，可以保留或添加此方法
    # @Slot(int)
    # def go_to_specific_page(self, page_num):
    #     """跳转到指定页（页码按钮点击）。"""
    #     if page_num != self.current_page:
    #         self.logger.info(f"跳转到第 {page_num} 页")
    #         self.current_page = page_num
    #         self.load_data()

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
        # 获取对话框中的数据
        dataset_data = {
            'dataset_name': dialog.name_input.text(),
            'dataset_category': dialog.category_combo.currentText(),
            'status': dialog.status_combo.currentText() if hasattr(dialog, 'status_combo') else '启用',
            'remark': dialog.desc_input.toPlainText()
        }
        
        self.logger.info(f"创建新数据集: {dataset_data}")
        # TODO: 调用模型创建数据集
        # with DatabaseManager.get_session() as session:
        #     DatasetModel.create_dataset(session, dataset_data)
        
        # 关闭对话框
        dialog.close()
        # 刷新数据列表
        self.load_data()

