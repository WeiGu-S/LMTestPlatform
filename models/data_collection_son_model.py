from turtle import title
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, Index
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum
import math
from utils.logger import get_logger
from datetime import datetime, timezone, timedelta
from models.eum import DataType, QuestionType, QuestionLabel
import uuid

Base = declarative_base()
logger = get_logger("data_collection_son_model")

class DataStatus(enum.Enum):
    DISABLED = "停用"
    ENABLED = "启用"


class DataModel(Base):
    # __tablename__ = 't_data_info'

    # id = Column(Integer, primary_key=True, autoincrement=True, comment='数据ID，主键自增')
    # collection_id = Column(Integer, nullable=False, comment='数据集ID')
    # title = Column(String(255), nullable=False, comment='数据标题')
    # answer = Column(String(255), nullable=False, comment='数据答案')
    # status = Column(SQLAlchemyEnum(DataStatus), nullable=False, comment='数据状态')
    # tag = Column(String(255), nullable=True, comment='数据标签')
    # del_flag = Column(Integer, nullable=False, default=0, comment='删除标记，0未删除，1已删除')
    # created_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    # updated_time = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='最后更新时间')

    __tablename__ = 't_data_collection_info'

    data_id = Column(String(20), primary_key=True, comment='数据ID')
    collection_id = Column(String(20), nullable=False, comment='数据集ID')
    data_type = Column(Integer, nullable=True, comment='数据分类')
    context = Column(String, nullable=True, comment='上下文')
    question = Column(String(500), nullable=True, comment='问题')
    answer = Column(String(500), nullable=True, comment='答案')
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
        logger.debug(f"Applying filters: {str(filters)}")

        try:
            # 过滤已删除的数据集
            query = query.filter(
                cls.del_flag == 0,
                cls.collection_id == collection_id
            )
            # 名称过滤
            if filters.get('question'):
                search_term = f"%{str(filters['title']).strip()}%"
                query = query.filter(cls.question.like(search_term))

            # 状态过滤
            if filters.get('data_type') and filters['data_type'] != '全部':
                status_map = {s.value: s for s in DataType}
                if str(filters['data_type']) in status_map:
                    query = query.filter(cls.data_type == status_map[str(filters['data_type'])])
                else:
                    logger.warning(f"Invalid data_type value: {filters['data_type']}")

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
            logger.error(f"获取分页数据集时出错: {e}", exc_info=True)
            session.rollback() # 出错时回滚
            return [], 0, 1

    @classmethod
    def get_all_data(cls, session, filters=None, collection_id=None):
        """获取所有数据集，基于过滤条件（用于导出）"""
        if not session:
            logger.error("获取所有数据集时数据库会话不可用")
            return []

        query = session.query(cls)
        query = cls._apply_filters(query, filters, collection_id)

        try:
            data = query.order_by(cls.created_time.desc()).all()
            return [d.to_dict() for d in data]
        except Exception as e:
            logger.error(f"获取所有数据集时出错: {e}", exc_info=True)
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
    def get_datas_by_id(cls, session, collection_id):
        """根据数据集ID获取所有关联数据"""
        try:
            datas = session.query(cls).filter(cls.collection_id == collection_id).first()
            return datas
        except Exception as e:
            logger.error(f"获取数据集时出错 (ID: {collection_id}): {e}", exc_info=True)
            session.rollback()
            return None
    # @classmethod
    # def get_datasetid_by_name(cls, session, question):
    #     """根据名称获取数据集ID"""
    #     try:
    #         dataset = session.query(cls).filter(cls.name == question).first()
    #         return dataset.id if dataset else None
    #     except Exception as e:
    #         logger.error(f"获取数据集ID时出错 (名称: {question}): {e}", exc_info=True)
    #         session.rollback()
    #         return None

    @classmethod
    def delete_datas(cls, session, collection_id):
        """批量删除所有关联数据"""
        try:
            datas = session.query(cls).filter(cls.id == collection_id,).first() 
            if datas:
                for data in datas:
                    data.del_flag = 1
                session.commit()
                logger.info(f"已成功删除数据 (ID: {collection_id})")
                return True
            else:
                logger.warning(f"数据不存在 (ID: {collection_id})")
                return False
        except Exception as e:
            logger.error(f"删除数据时出错 (ID: {collection_id}): {e}", exc_info=True)
            session.rollback()
            return False

    @classmethod
    def update_data_collection(cls, session, collection_id, dataset_data):
        """更新数据"""    
        if dataset_data.get('question'):
            # 校验数据集名称是否已存在且未删除且非空
            try:
                existing_dataset = session.query(cls).filter(
                    cls.question == dataset_data.get('question'),
                    cls.del_flag == 0
                ).first()
                if existing_dataset and existing_dataset.id != collection_id:
                    logger.error(f"数据集名称已存在: {dataset_data.get('question')}")
                    return False
            except Exception as e:
                logger.error(f"查询数据集时出错 (数据集名称: {dataset_data.get('question')}): {e}", exc_info=True)
                session.rollback()
                return False