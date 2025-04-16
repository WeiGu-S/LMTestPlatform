from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime
import enum

Base = declarative_base()

class DatasetStatus(enum.Enum):
    ENABLED = '启用'
    DISABLED = '禁用'

class DatasetCategory(enum.Enum):
    VIDEO = '视频'
    IMAGE = '图片'
    AUDIO = '音频'
    TEXT = '文本'
    # Add other categories as needed

class Dataset(Base):
    __tablename__ = 't_dataset_info' 

    id = Column(Integer, primary_key=True, comment='集合编号')
    dataset_name = Column(String(255), nullable=False, comment='集合名称')
    dataset_category = Column(SQLEnum(DatasetCategory), comment='数据分类')
    status = Column(SQLEnum(DatasetStatus), default=DatasetStatus.ENABLED, comment='状态')
    content_volume = Column(Integer, default=0, comment='内容量')
    created_time = Column(DateTime, default=datetime.utcnow, comment='创建时间')

    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.dataset_name}', status='{self.status.value}')>"

    @classmethod
    def get_paginated_datasets(cls, session: Session, page: int = 1, per_page: int = 10, 
                               filters: dict = None):
        """Fetches paginated and filtered datasets."""
        query = session.query(cls)

        if filters:
            if filters.get('dataset_name'):
                query = query.filter(cls.dataset_name.like(f"%{filters['dataset_name']}%"))
            if filters.get('status') and filters['status'] != '全部':
                 try:
                     status_enum = DatasetStatus(filters['status'])
                     query = query.filter(cls.status == status_enum)
                 except ValueError:
                     pass # Ignore invalid status filter
            if filters.get('dataset_category') and filters['datasetcategory'] != '全部':
                try:
                    category_enum = DatasetCategory(filters['datasetcategory'])
                    query = query.filter(cls.dataset_category == category_enum)
                except ValueError:
                    pass # Ignore invalid category filter
            if filters.get('start_time'):
                query = query.filter(cls.created_time >= filters['start_time'])
            if filters.get('end_time'):
                # Add 1 day to end_time to include the whole day
                from datetime import timedelta
                end_time_inclusive = filters['end_time'] + timedelta(days=1)
                query = query.filter(cls.created_time < end_time_inclusive)

        total_items = query.count()
        datasets = query.order_by(cls.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        total_pages = (total_items + per_page - 1) // per_page

        # Format data for the view's TableModel
        formatted_data = []
        for ds in datasets:
            formatted_data.append([
                ds.id,
                ds.dataset_name,
                ds.dataset_category.value if ds.dataset_category else '', # Handle potential None
                ds.status.value if ds.status else '', # Handle potential None
                ds.content_volume,
                ds.created_time.strftime('%Y-%m-%d %H:%M:%S') if ds.created_time else '',
                "修改 查看" # Placeholder for actions
            ])

        return formatted_data, total_items, total_pages

    # Add methods for create, update, delete as needed
