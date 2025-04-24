from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QGridLayout, QDialog, QFrame
)
from PySide6.QtCore import Qt, Signal
from models.data_collection_model import DataCollectionModel
from models.dataset_son_model import DataModel, DataStatus
from utils.database import DatabaseManager
import pandas as pd
import pandas as pd
from utils.logger import get_logger


logger = get_logger("import_dialog")

class ImportDialog(QDialog):
    import_confirmed = Signal(list)
    def __init__(self, parent=None, dataset_id=None, datas=None):
        super().__init__(parent)
        self.dataset_id = dataset_id
        self.datas = datas
        # 设置对话框标题
        self.setWindowTitle("数据导入")
        # 设置对话框大小
        self.setMinimumSize(800, 600)
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
                border: 1px solid #e4e7ed;
                border-radius: 8px;
            }
        """)
        # 初始化界面布局
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        # 主体布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        # 顶部区域
        top_frame = QFrame()
        top_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e4e7ed;
                border-radius: 8px;
                padding: 0;
                height: 40px;
            }
        """)
        top_layout = QHBoxLayout(top_frame)
        
        # 选择文件按钮
        self.select_file_btn = QPushButton("选择文件")
        self.select_file_btn.setMinimumSize(100, 32)
        self.select_file_btn.setStyleSheet("""
            QPushButton {
                background-color: #409eff;
                color: white;
                border-radius: 4px;
                width: 60px;
                height: 32px;
            }
            QPushButton:hover {
                background-color: #66b1ff;
            }
        """)
        self.select_file_btn.clicked.connect(self.select_file)
        top_layout.addWidget(self.select_file_btn)        
        # 文件名称显示区域
        self.file_name_display = QLineEdit()
        self.file_name_display.setReadOnly(True)
        self.file_name_display.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #e4e7ed;
                border-radius: 6px;
                padding: 0;
                max-width: 200px;
                height: 32px;
            }
            QLineEdit::uneditable {
                background-color: #f5f7fa;
            }
        """)
        top_layout.addWidget(self.file_name_display)
        # 导入模板下载按钮
        self.download_template_btn = QPushButton("下载模板")
        self.download_template_btn.setMinimumSize(100, 32)
        self.download_template_btn.setStyleSheet("""
            QPushButton {
                background-color: #409eff;
                color: white;
                border-radius: 4px; 
                width: 60px;
                height: 32px;
            }
            QPushButton:hover {
                
            }
        """)
        self.download_template_btn.clicked.connect(self.download_template)
        top_layout.addWidget(self.download_template_btn)
        top_layout.addStretch()
        main_layout.addWidget(top_frame)


        # 提示标签
        info_label = QLabel("提示：预览展示前十条数据")
        info_label.setStyleSheet("""
            QLabel {
                color: #606266;
                font-weight: bold;
                border:none;
            }
        """)
        top_layout.addWidget(info_label)
        top_layout.addStretch()

        # 表格区域
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(4)
        self.data_table.setHorizontalHeaderLabels(["序号", "标题", "答案", "标签"])
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e4e7ed;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #f5f7fa;
                padding: 5px;
                border: none;
                border-right: 1px solid #e4e7ed;
                border-bottom: 1px solid #e4e7ed;
            }
        """)
        # 设置列宽
        self.data_table.setColumnWidth(0, 40)
        self.data_table.setColumnWidth(1, 280)
        self.data_table.setColumnWidth(2, 280)
        self.data_table.setColumnWidth(3, 180)
        
        main_layout.addWidget(self.data_table)

        # 底部按钮区域
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e4e7ed;
                border-radius: 8px;
                padding: 5px;
                height: 40px;
            }
        """)
        main_layout.addWidget(button_frame)
        button_layout = QHBoxLayout(button_frame)     
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)   
        # 确定按钮
        self.confirm_btn = QPushButton()
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                image: url(utils/img/confirm.png);
                width: 40px;
                height: 40px;
            }
            QPushButton:hover {
                cursor: pointer;
            }
            QPushButton:pressed {
                padding: 4px;
            }
        """)
        self.confirm_btn.clicked.connect(self.emit_import_confirmed)
        
        # 取消按钮
        self.cancel_btn = QPushButton()
        self.cancel_btn.setMinimumSize(80, 32)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                image: url(utils/img/cancel.png);
                width: 40px;
                height: 40px;
            }
            QPushButton:hover {
                cursor: pointer;
            }
            QPushButton:pressed {
                padding: 4px;
            }
        """)
        
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)

    def select_file(self):
        """选择文件并读取数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;All Files (*)"
        )
        # 更新文件名显示
        fil = file_path.split("/")[-1]
        self.file_name_display.setText(fil)
        if file_path:
            try:
                # 读取数据
                data_list = []
                
                # 根据文件类型选择不同的读取方式
                if file_path.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_path)
                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    QMessageBox.warning(self, "警告", "不支持的文件格式")
                    return None

                # 检查必要的列是否存在
                required_columns = ['title', 'answer', 'tags']
                if not all(col in df.columns for col in required_columns):
                    QMessageBox.warning(self, "警告", "文件格式不正确，请确保包含title、answer和tags列")
                    return None

                # 收集数据
                for index, row in df.iterrows():
                    data_item = {
                        'dataset_id': self.dataset_id,
                        'title': str(row['title']),
                        'answer': str(row['answer']),
                        'tags': str(row['tags']),
                        'status': DataStatus.ENABLED
                    }
                    data_list.append(data_item)
                
                # 使用update_tab_table更新表格显示
                self.update_import_table(datas=data_list)
                self.datas = data_list
                return 

            except Exception as e:
                QMessageBox.critical(self, "错误", f"读取文件时发生错误：{str(e)}")
                return None

    def update_import_table(self, datas=None):
        """更新数据子项表格（完整实现）"""
        # 表格初始化检查
        if not hasattr(self, 'data_table'):
            logger.error("表格控件未初始化")
            return
        try:
            # 清空现有数据
            self.data_table.setRowCount(0)
            # 处理空数据状态
            # print(f"datas:{datas}")
            if not datas:
                self.data_table.setRowCount(1)
                self.data_table.setSpan(0, 0, 1, self.data_table.columnCount())
                no_data_item = QTableWidgetItem("暂无数据")
                no_data_item.setTextAlignment(Qt.AlignCenter)
                self.data_table.setItem(0, 0, no_data_item)
                return

            # 设置表格行数,仅展示前10条数据
            if len(datas) < 10:
                self.data_table.setRowCount(len(datas))
            else:
                self.data_table.setRowCount(10)
            # 填充数据行
            for row, data in enumerate(datas):
                # 填充各列数据
                self.data_table.setItem(row, 0, QTableWidgetItem(str(row+1)))  # 序号
                self.data_table.setItem(row, 1, QTableWidgetItem(data.get('title', '')))  # 标题
                self.data_table.setItem(row, 2, QTableWidgetItem(data.get('answer', '')))  # 答案
                self.data_table.setItem(row, 3, QTableWidgetItem(data.get('tags', '')))  # 标签

        except Exception as e:
            logger.error(f"更新数据子项表格时发生错误：{str(e)}")
    def emit_import_confirmed(self):
        """导入确认"""
        # 检查是否有数据
        if not self.datas:
            QMessageBox.warning(self, "警告", "请先选择文件并导入数据")
            return
        # 发射确认信号，将数据传递给控制器
        # print(f"self.datas:{self.datas}")
        self.import_confirmed.emit(self.datas)

    def download_template(self):
        """下载导入模板"""
        # 打开文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存模板文件",
            "dataset_import_template.xlsx", 
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                # 创建示例数据
                template_data = {
                    'index': [1, 2],  # 序号列，示例数据为1和2,
                    'title': ['如何使用Python进行数据分析?', '机器学习的基本步骤是什么?'],
                    'answer': [
                        'Python数据分析主要使用pandas、numpy等库。基本步骤包括:\n1. 数据导入\n2. 数据清洗\n3. 数据分析\n4. 数据可视化',
                        '机器学习的基本步骤包括:\n1. 数据收集和预处理\n2. 特征工程\n3. 模型选择和训练\n4. 模型评估\n5. 模型优化'
                    ],
                    'tags': ['Python,数据分析,pandas', '机器学习,AI,模型训练']
                }
                
                # 创建DataFrame
                df = pd.DataFrame(template_data)
                
                # 设置列宽
                writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                
                # 获取workbook和worksheet对象
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                
                # 设置列宽
                worksheet.set_column('A:A', 10)  # 序号列
                worksheet.set_column('B:B', 40)  # 标题列
                worksheet.set_column('C:C', 60)  # 答案列
                worksheet.set_column('D:D', 30) # 标签列
                
                # 添加列说明
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'bg_color': '#D9D9D9'
                })
                
                worksheet.write(0, 3, 'tags (标签)', header_format)
                worksheet.write(0, 2, 'answer (答案内容)', header_format)
                worksheet.write(0, 1, 'title (问题标题)', header_format)
                worksheet.write(0, 0, '序号', header_format)
                
                # 保存文件
                writer.close()
                
                QMessageBox.information(self, "成功", "模板文件已成功下载！\n请按照模板格式填写数据后导入。")
                
            except Exception as e:
                logger.error(f"下载模板时发生错误: {str(e)}")
                QMessageBox.critical(self, "错误", f"下载模板时发生错误：{str(e)}")
