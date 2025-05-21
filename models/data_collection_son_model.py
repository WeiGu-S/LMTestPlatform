from turtle import title
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, Index, true
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum
import math
from utils.database import DatabaseManager
from utils.logger import get_logger, setup_logging
from datetime import datetime, timezone, timedelta
from models.enum import DataType, QuestionType, QuestionLabel
import uuid

Base = declarative_base()
setup_logging()
logger = get_logger("data_collection_son_model")

class DataStatus(enum.Enum):
    DISABLED = "停用"
    ENABLED = "启用"


class DataModel(Base):
    """数据模型"""
    __tablename__ = 't_data_collection_info'

    data_id = Column(String(20), primary_key=True, comment='数据ID')
    collection_id = Column(String(20), nullable=False, comment='数据集ID')
    data_type = Column(Integer, nullable=True, comment='数据分类')
    context = Column(String, nullable=True, comment='上下文')
    question = Column(String(500), nullable=True, comment='问题')
    answer = Column(String(500), nullable=True, comment='答案')
    model_answer = Column(String(500), nullable=True, comment='模型答案') # 大模型答案
    question_type = Column(Integer, nullable=True, comment='题型')
    question_label = Column(Integer, nullable=True, comment='问题标签')
    created_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    created_by = Column(String(20), nullable=True, comment='创建人')
    updated_time = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    updated_by = Column(String(20), nullable=True, comment='更新人')
    del_flag = Column(Integer, nullable=False, default=0, comment='删除标记')

    def to_dict(self):
        """将模型实例转换为字典，便于视图层使用"""
        return {
            "data_id": self.data_id,
            "collection_id": self.collection_id,
            "data_type": self.data_type.value if isinstance(self.data_type, DataType) else self.data_type, # 返回枚举值
            "context": self.context,
            "question": self.question,
            "answer": self.answer, 
            "model_answer": self.model_answer, # 大模型答案
            "question_type": self.question_type.value if isinstance(self.question_type, QuestionType) else self.question_type, # 返回枚举值
            "question_label": self.question_label.value if isinstance(self.question_label, QuestionLabel) else self.question_label, # 返回枚举值,
            "del_flag": self.del_flag,
            "created_time": self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None, # 格式化时间
            "created_by": self.created_by
        }

    @classmethod
    def _apply_filters(cls, query, filters, collection_id):
        """安全地应用过滤条件到查询，兼容QDate类型"""
        if not filters:
            return query.filter(
                cls.del_flag == 0,
                cls.collection_id == collection_id
            )

        try:
            # 过滤已删除的数据集
            query = query.filter(
                cls.del_flag == 0,
                cls.collection_id == collection_id
            )
            # 数据分类过滤
            if filters["data_type"]:
                query = query.filter(cls.data_type == filters["data_type"])

            # 题型过滤
            if filters["question_type"]:
                query = query.filter(cls.question_type == filters["question_type"])

            # 标签过滤
            if filters["question_label"]:
                query = query.filter(cls.question_label == filters["question_label"])

            # 日期处理（兼容QDate和date类型）
            if filters.get('start_date'):
                start_date = filters['start_date']
                if hasattr(start_date, 'toPython'):  # 处理QDate类型
                    start_date = start_date.toPython()
                query = query.filter(cls.created_time >= start_date)
            
            if filters.get('end_date'):
                end_date = filters['end_date']
                if hasattr(end_date, 'toPython'):  # 处理QDate类型
                    end_date = end_date.toPython()
                
                from datetime import datetime, time
                end_of_day = datetime.combine(end_date, time.max)
                query = query.filter(cls.created_time <= end_of_day)

        except Exception as e:
            logger.error(f"Filter application error: {str(e)}", exc_info=True)
            raise ValueError("Filter processing failed") from e

        return query

    @classmethod
    def get_paginated_data(cls, collection_id, session, page=1, per_page=10, filters=None):
        """获取分页的数据集，基于过滤条件"""
        if not session:
            logger.error("数据库会话不可用")
            return [], 0, 1 # 数据、总条目数、总页数

        query = session.query(cls)
        query = cls._apply_filters(query, filters, collection_id)

        try:
            total_items = query.count()
            total_pages = math.ceil(total_items / per_page) if per_page > 0 else 1
            if page < 1:
                page = 1
            elif page > total_pages and total_pages > 0:
                page = total_pages # 若页码超出总页数，则调整为最后一页

            offset = (page - 1) * per_page
            data = query.order_by(cls.created_time.desc()).offset(offset).limit(per_page).all()
            
            # 将数据集对象转换为字典
            data_dicts = [d.to_dict() for d in data]
            
            return data_dicts, total_items, total_pages
        except Exception as e:
            logger.error(f"获取分页数据时出错: {e}", exc_info=True)
            session.rollback() # 出错时回滚
            return [], 0, 1

    @classmethod
    def get_all_data(cls, session, filters=None, collection_id=None):
        """获取所有数据，基于过滤条件（用于导出）"""
        if not session:
            logger.error("获取所有数据时数据库会话不可用")
            return []

        query = session.query(cls)
        query = cls._apply_filters(query, filters, collection_id)

        try:
            data = query.order_by(cls.created_time.desc()).all()
            return [d.to_dict() for d in data]
        except Exception as e:
            logger.error(f"获取所有数据时出错: {e}", exc_info=True)
            session.rollback()
            return []

    @classmethod
    def add_data(cls, session, datas, collection_id):
        """添加新数据"""
        data_type = datas.get('data_type')
        question = datas.get('question')
        answer = datas.get('answer')
        question_label = datas.get('question_label')
        question_type = datas.get('question_type')
        context = datas.get('context')
        model_answer = datas.get('model_answer')

        if datas is None:
            logger.error("数据集数据为空")
            return None
        # 校验上下文、问题、答案是否为空
        if not context or not question or not answer:
            logger.error("上下文、问题或答案为空")
            return None
        # 创建新数据集
        try:
            new_data = DataModel(
                data_id=str(uuid.uuid4().int)[:20] ,
                collection_id=collection_id,
                data_type=data_type,
                question_type=question_type,
                context=context,
                question=question,
                answer=answer,
                model_answer=model_answer,
                question_label=question_label,
                del_flag=0,
                created_time=datetime.now(timezone(timedelta(hours=8))),
                created_by=datas.get('created_by'),
            )
            session.add(new_data)
            session.commit()
            logger.info(f"已成功添加数据集 (名称: {question}, 类别: {answer})")
            return new_data
        except ValueError as ve:
            logger.error(f"无效的类别或状态值 (数据集名称: {question}, 类别: {answer}")
            session.rollback()
            return None
        except Exception as e:
            logger.error(f"添加数据集时出错 (数据集名称: {question}): {e}", exc_info=True)
            session.rollback()
            return None
    
    @classmethod
    def get_datas_by_id(cls,collection_id):
        """根据数据集ID获取所有关联数据"""
        try:
            with DatabaseManager.get_session() as session:
                datas = session.query(cls).filter(cls.collection_id == collection_id).first()
                return datas
        except Exception as e:
            logger.error(f"获取数据时出错 (ID: {collection_id}): {e}", exc_info=True)
            session.rollback()
            return None

    @classmethod
    def get_data_by_id(cls, data_id):
        """根据数据ID获取单个数据"""
        try:
            with DatabaseManager.get_session() as session:
                data = session.query(cls).filter(cls.data_id == data_id).first()
                return data
        except Exception as e:
            logger.error(f"获取数据时出错 (ID: {data_id}): {e}", exc_info=True)
            session.rollback()
            return None

    @classmethod
    def delete_datas(cls,session, collection_id):
        """批量删除所有关联数据"""
        try:
            datas = session.query(cls).filter(cls.collection_id == collection_id,).all() 
            if datas:
                for data in datas:
                    data.del_flag = 1
                session.commit()
                logger.info(f"已成功删除相关联数据 (ID: {collection_id})")
                return True
            else:
                logger.warning(f"相关联数据不存在 (ID: {collection_id})")
                return False
        except Exception as e:
            logger.error(f"删除相关联数据时出错 (ID: {collection_id}): {e}", exc_info=True)
            session.rollback()
            return False

    @classmethod
    def delete_data(cls, data_id):
        """删除单个数据"""
        try:
            with DatabaseManager.get_session() as session:
                data = session.query(cls).filter(cls.data_id == data_id).first()
                print(data)
                if data:
                    data.del_flag = 1
                    session.commit()
                    logger.info(f"已成功删除数据 (ID: {data_id})")
                    return True
                else:
                    logger.warning(f"数据不存在 (ID: {data_id})")
                    return False
                
        except Exception as e:
            logger.error(f"删除数据时出错 (ID: {data_id}): {e}", exc_info=True)
            session.rollback()
            return False

    @classmethod
    def update_data(cls, session, data_id, datas):
        """更新数据"""    
        if not datas:
            logger.error("数据集数据为空")
            return None
        try:
            data = session.query(cls).filter(cls.data_id == data_id).first()
            print(f"datas: {datas}")
            if data:
                # 直接访问对象属性进行赋值
                data.data_type = datas.get('data_type')
                data.question_type = datas.get('question_type')
                data.context = datas.get('context')
                data.question = datas.get('question')
                data.answer = datas.get('answer')
                data.model_answer = datas.get('model_answer')
                data.question_label = datas.get('question_label')
                data.updated_time = datetime.now(timezone(timedelta(hours=8)))
                data.updated_by = datas.get('updated_by')
                session.commit()
                logger.info(f"已成功更新数据集 (ID: {data_id})")
                return True
            else:
                logger.warning(f"数据集不存在 (ID: {data_id})")
                return None
        except Exception as e:
            logger.error(f"更新数据集时出错 (ID: {data_id}): {e}", exc_info=True)
            session.rollback()
            return None