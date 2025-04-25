from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QFileDialog, QMessageBox,
    QLabel, QLineEdit, QGridLayout, QDialog, QFrame,QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QFontMetrics
from models.data_collection_model import DataCollectionModel
from models.dataset_son_model import DataModel, DataStatus
from models.eum import BaseEnum, DataType, QuestionLabel, QuestionType
from utils.database import DatabaseManager
import pandas as pd
import pandas as pd
from utils.logger import get_logger


logger = get_logger("import_dialog")

class ImportDialog(QDialog):
    import_confirmed = Signal(list)
    def __init__(self, parent=None, collection_id=None, datas=None):
        super().__init__(parent)
        self.collection_id = collection_id
        self.datas = datas
        # 设置对话框标题
        self.setWindowTitle("数据导入")
        # 设置对话框大小
        self.setMinimumSize(850, 500)
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
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        self.setLayout(self.main_layout)

        # 初始化三个主要区域
        self.init_top_area()
        self.init_table_area()
        self.init_bottom_area()

    def init_top_area(self):
        """初始化顶部区域"""
        # 创建顶部容器
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
        
        # 创建顶部布局
        top_layout = QHBoxLayout(top_frame)
        
        # 创建并添加按钮和显示组件
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
        
        self.file_name_display = QLineEdit()
        self.file_name_display.setPlaceholderText("请选择文件")
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
        """)
        
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
                background-color: #66b1ff;
            }
        """)
        self.download_template_btn.clicked.connect(self.download_template)
        
        # 添加提示文本
        info_label = QLabel("提示：预览展示前十条数据")
        info_label.setStyleSheet("color: #606266; font-weight: bold; border: none;")
        
        # 组装顶部布局
        top_layout.addWidget(self.select_file_btn)
        top_layout.addWidget(self.file_name_display)
        top_layout.addWidget(self.download_template_btn)
        top_layout.addStretch()
        top_layout.addWidget(info_label)
        top_layout.addStretch()
        
        self.main_layout.addWidget(top_frame)

    def init_table_area(self):
        """初始化表格区域"""
        # 创建表格容器
        table_container = QWidget()
        table_container.setMinimumSize(1000, 400)
        table_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                padding: 0;
                border: none;
            }
        """)

        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # 创建表格
        self.data_table = QTableWidget()
        self.data_table.setObjectName("dataTable")
        self.data_table.setFont(QFont("Microsoft YaHei", 14))
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setColumnCount(7)
        self.data_table.setHorizontalHeaderLabels(["序号", "数据分类", "题型", "上下文", "问题", "答案", "问题标签"])
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setSelectionMode(QTableWidget.SingleSelection)
        self.data_table.verticalHeader().setDefaultSectionSize(42)

        # 设置表头
        header = self.data_table.horizontalHeader()
        header.setObjectName("tableHeader")
        header.setStyleSheet("""
            QHeaderView#tableHeader {
                background-color: transparent;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QHeaderView#tableHeader::section {
                background-color: #f5f5f5;
                color: #333333;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                border-left: 1px solid #e0e0e0;
                padding: 10px 12px;
                font-family: "Microsoft YaHei";
                font-size: 13px;
                font-weight: 500;
                qproperty-alignment: AlignCenter;
            }
        """)
        header.setFont(QFont("Microsoft YaHei", 12, QFont.Medium))

        # 设置表头列伸缩模式
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.Fixed)

        # 设置表格样式
        self.data_table.setStyleSheet("""
            QTableWidget#dataTable {
                background-color: #ffffff;
                alternate-background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                gridline-color: #f0f0f0;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
                padding: 0;
            }
            QTableWidget#dataTable::item {
                padding: 0;
                border-bottom: 1px solid #f0f0f0;
                border-left: 1px solid #f0f0f0;
            }
            QTableWidget#dataTable::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)

        # 设置列宽
        self.data_table.setColumnWidth(0, 80)
        self.data_table.setColumnWidth(1, 80)
        self.data_table.setColumnWidth(2, 80)
        self.data_table.setColumnWidth(3, 200)
        self.data_table.setColumnWidth(4, 200)
        self.data_table.setColumnWidth(5, 200)
        self.data_table.setColumnWidth(6, 80)

        table_layout.addWidget(self.data_table)
        
        self.main_layout.addWidget(table_container)

    def init_bottom_area(self):
        """初始化底部区域"""
        # 创建底部容器
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e4e7ed;
                border-radius: 8px;
                padding: 6px;
                height: 40px;
            }
        """)
        
        # 创建底部布局
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(12)
        

        button_style = """
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
        """
        # 创建确认按钮
        self.confirm_btn = QPushButton()
        self.confirm_btn.setStyleSheet(button_style+"""
            QPushButton {
                image: url(utils/img/confirm.png);
            }
        """)
        self.confirm_btn.clicked.connect(self.emit_import_confirmed)
        
        # 创建取消按钮
        self.cancel_btn = QPushButton()
        self.cancel_btn.setMinimumSize(80, 32)
        self.cancel_btn.setStyleSheet(button_style+"""
            QPushButton {
                image: url(utils/img/cancel.png);

            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        # 组装底部布局
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.confirm_btn)
        bottom_layout.addWidget(self.cancel_btn)
        bottom_layout.addStretch()
        
        self.main_layout.addWidget(bottom_frame)

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
                required_columns = ['data_type (数据分类)', 'context (上下文)', 'question (问题)', 
                                 'answer (答案)', 'question_type (题型)', 'question_label (问题标签)']
                if not all(col in df.columns for col in required_columns):
                    error_msg = "文件格式不正确，请确保包含以下列:\n"
                    error_msg += "\n".join(required_columns)
                    QMessageBox.warning(self, "警告", error_msg)
                    return None

                # 收集数据
                for index, row in df.iterrows():
                    data_item = {
                        'data_type': DataType.get_value_by_label(row['data_type (数据分类)']),
                        'context': row['context (上下文)'],
                        'question': row['question (问题)'],
                        'answer': row['answer (答案)'],
                        'question_type': QuestionType.get_value_by_label(row['question_type (题型)']),
                        'question_label': QuestionLabel.get_value_by_label(row['question_label (问题标签)'])
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
                    'index': [1],  # 序号列
                    'data_type': ['文本'],  # 数据分类
                    'context': [
                        '在软件开发和数据分析领域中，Python是一个强大的编程语言。'
                    ],  # 上下文
                    'question': [
                        '如何使用Python进行数据分析?'
                    ],  # 问题
                    'answer': [
                        'Python数据分析主要使用pandas、numpy等库。基本步骤包括:\n1. 数据导入\n2. 数据清洗\n3. 数据分析\n4. 数据可视化'
                    ],  # 答案
                    'question_type': ['问答题'],  # 题型
                    'question_label': ['数学,文字理解,Rag召回']  # 问题标签
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
                worksheet.set_column('B:B', 20)  # 数据分类列
                worksheet.set_column('C:C', 40)  # 上下文列
                worksheet.set_column('D:D', 40)  # 问题列
                worksheet.set_column('E:E', 60)  # 答案列
                worksheet.set_column('F:F', 20)  # 题型列
                worksheet.set_column('G:G', 30)  # 问题标签列
                
                # 添加列说明
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'bg_color': '#D9D9D9'
                })
                
                worksheet.write(0, 0, '序号', header_format)
                worksheet.write(0, 1, 'data_type (数据分类)', header_format)
                worksheet.write(0, 2, 'context (上下文)', header_format)
                worksheet.write(0, 3, 'question (问题)', header_format)
                worksheet.write(0, 4, 'answer (答案)', header_format)
                worksheet.write(0, 5, 'question_type (题型)', header_format)
                worksheet.write(0, 6, 'question_label (问题标签)', header_format)

                # 设置数据验证下拉列表
                data_type_list = ['文本', '图片', '音频', '视频']
                question_type_list = ['选择题', '判断题', '问答题']
                question_label_list = ['数学', '文字理解', 'Rag召回']

                # 为数据分类列添加下拉列表
                worksheet.data_validation('B2:B1048576', {
                    'validate': 'list',
                    'source': data_type_list,
                    'error_message': '请从下拉列表中选择有效的数据分类'
                })

                # 为题型列添加下拉列表
                worksheet.data_validation('F2:F1048576', {
                    'validate': 'list',
                    'source': question_type_list,
                    'error_message': '请从下拉列表中选择有效的题型'
                })

                # 为问题标签列添加下拉列表
                worksheet.data_validation('G2:G1048576', {
                    'validate': 'list',
                    'source': question_label_list,
                    'error_message': '请从下拉列表中选择有效的问题标签'
                })
                
                # 保存文件
                writer.close()
                
                QMessageBox.information(self, "成功", "模板文件已成功下载！\n请按照模板格式填写数据后导入。")
                
            except Exception as e:
                logger.error(f"下载模板时发生错误: {str(e)}")
                QMessageBox.critical(self, "错误", f"下载模板时发生错误：{str(e)}")
