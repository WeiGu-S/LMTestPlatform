from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, Index
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum
import math
from utils.logger import get_logger

Base = declarative_base()
logger = get_logger()

class DatasetStatus(enum.Enum):
    ENABLED = "启用"
    DISABLED = "禁用"

class DatasetCategory(enum.Enum):
    VIDEO = "视频"
    IMAGE = "图片"
    AUDIO = "音频"
    TEXT = "文本"
    # 可根据实际需求添加其他类别

class DatasetModel(Base):
    __tablename__ = 't_dataset_info'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='数据集ID，主键自增')
    dataset_name = Column(String(255), nullable=False, unique=True, comment='数据集名称，不允许为空')
    dataset_category = Column(SQLAlchemyEnum(DatasetCategory), nullable=False, default=DatasetCategory.VIDEO, index=True, comment='数据集类型')
    status = Column(SQLAlchemyEnum(DatasetStatus), nullable=False, default=DatasetStatus.ENABLED, index=True, comment='状态')
    content_size = Column(Integer, nullable=False, default=0, comment='包含的问题数量，默认0')
    description = Column(String(255), nullable=True, comment='数据集描述')
    created_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    updated_time = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='最后更新时间')
    def to_dict(self):
        """将模型实例转换为字典，便于视图层使用"""
        return {
            "id": self.id,
            "dataset_name": self.dataset_name,
            "dataset_category": self.dataset_category.value if isinstance(self.dataset_category, DatasetCategory) else self.dataset_category, # 返回枚举值
            "status": self.status.value if isinstance(self.status, DatasetStatus) else self.status, # 返回枚举值
            "content_size": self.content_size,
            "created_time": self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None # 格式化时间
        }

    @classmethod
    def _apply_filters(cls, query, filters):
        """Applies filtering conditions to the query based on the filters dictionary."""
        if not filters:
            return query

        if filters.get('dataset_name'):
            query = query.filter(cls.dataset_name.ilike(f"%{filters['dataset_name']}%"))
        if filters.get('status') and filters['status'] != '全部':
            try:
                status_enum = DatasetStatus(filters['status'])
                query = query.filter(cls.status == status_enum)
            except ValueError:
                logger.warning(f"无效的状态过滤值: {filters['status']}")
        if filters.get('dataset_category') and filters['dataset_category'] != '全部':
            try:
                category_enum = DatasetCategory(filters['dataset_category'])
                query = query.filter(cls.dataset_category == category_enum)
            except ValueError:
                logger.warning(f"无效的类别过滤值: {filters['dataset_category']}")
        if filters.get('start_date'):
            query = query.filter(cls.created_time >= filters['start_date'])
        if filters.get('end_date'):
            from datetime import timedelta
            end_date_inclusive = filters['end_date'] + timedelta(days=1)
            query = query.filter(cls.created_time < end_date_inclusive)
        return query

    @classmethod
    def get_paginated_datasets(cls, session, page=1, per_page=10, filters=None):
        """获取分页的数据集，基于过滤条件"""
        if not session:
            logger.error("数据库会话不可用")
            return [], 0, 1 # 数据、总条目数、总页数

        query = session.query(cls)
        query = cls._apply_filters(query, filters)

        try:
            total_items = query.count()
            total_pages = math.ceil(total_items / per_page) if per_page > 0 else 1
            if page < 1:
                page = 1
            elif page > total_pages and total_pages > 0:
                page = total_pages # 若页码超出总页数，则调整为最后一页

            offset = (page - 1) * per_page
            datasets = query.order_by(cls.created_time.desc()).offset(offset).limit(per_page).all()
            
            # 将数据集对象转换为字典
            dataset_dicts = [d.to_dict() for d in datasets]
            
            return dataset_dicts, total_items, total_pages
        except Exception as e:
            logger.error(f"获取分页数据集时出错: {e}", exc_info=True)
            session.rollback() # 出错时回滚
            return [], 0, 1

    @classmethod
    def get_all_datasets(cls, session, filters=None):
        """获取所有数据集，基于过滤条件（用于导出）"""
        if not session:
            logger.error("获取所有数据集时数据库会话不可用")
            return []

        query = session.query(cls)
        query = cls._apply_filters(query, filters)

        try:
            datasets = query.order_by(cls.created_time.desc()).all()
            return [d.to_dict() for d in datasets]
        except Exception as e:
            logger.error(f"获取所有数据集时出错: {e}", exc_info=True)
            session.rollback()
            return []

    @classmethod
    def add_dataset(cls, session, dataset_name, dataset_category, status, content_size):
        try:
            new_dataset = Dataset(
                dataset_name=dataset_name,
                dataset_category=DatasetCategory(dataset_category),
                status=DatasetStatus(status),
                content_size=content_size
            )
            session.add(new_dataset)
            session.commit()
            logger.info(f"已添加数据集: {dataset_name}")
            return new_dataset
        except Exception as e:
            logger.error(f"添加数据集时出错: {e}", exc_info=True)
            session.rollback()
            return None