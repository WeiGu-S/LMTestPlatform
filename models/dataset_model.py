from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, Index
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum
import math
from utils.logger import get_logger
from datetime import datetime, timezone, timedelta
# from views.dataset.dataset_view import DatasetView


Base = declarative_base()
logger = get_logger("dataset_model")

class DatasetStatus(enum.Enum):
    ENABLED = "启用"
    DISABLED = "停用"

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
    remark = Column(String(255), nullable=True, comment='备注')
    del_flag = Column(Integer, nullable=False, default=0, comment='删除标记，0未删除，1已删除')
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
            "remark": self.remark,
            "del_flag": self.del_flag,
            "created_time": self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None # 格式化时间
        }

    @classmethod
    def _apply_filters(cls, query, filters):
        """安全地应用过滤条件到查询，兼容QDate类型"""
        if not filters:
            return query.filter(cls.del_flag == 0)

        logger.debug(f"Applying filters: {str(filters)}")

        try:
            # 过滤已删除的数据集
            query = query.filter(cls.del_flag == 0)
            # 名称过滤
            if filters.get('dataset_name'):
                search_term = f"%{str(filters['dataset_name']).strip()}%"
                query = query.filter(cls.dataset_name.ilike(search_term))

            # 状态过滤
            if filters.get('status') and filters['status'] != '全部':
                status_map = {s.value: s for s in DatasetStatus}
                if str(filters['status']) in status_map:
                    query = query.filter(cls.status == status_map[str(filters['status'])])
                else:
                    logger.warning(f"Invalid status value: {filters['status']}")

            # 分类过滤
            if filters.get('dataset_category') and filters['dataset_category'] != '全部':
                category_map = {c.value: c for c in DatasetCategory}
                if str(filters['dataset_category']) in category_map:
                    query = query.filter(cls.dataset_category == category_map[str(filters['dataset_category'])])
                else:
                    logger.warning(f"Invalid category value: {filters['dataset_category']}")

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

        query = session.query(cls.del_flag == 0)
        query = cls._apply_filters(query, filters)

        try:
            datasets = query.order_by(cls.created_time.desc()).all()
            return [d.to_dict() for d in datasets]
        except Exception as e:
            logger.error(f"获取所有数据集时出错: {e}", exc_info=True)
            session.rollback()
            return []

    
    @classmethod
    def add_dataset(cls, session, dataset_data):
        """添加新数据集"""        
        dataset_name = dataset_data.get('dataset_name')
        dataset_category = DatasetCategory(dataset_data.get('dataset_category'))
        status = DatasetStatus(dataset_data.get('status'))
        remark = dataset_data.get('remark')
        
        # 校验数据集名称是否已存在且未删除且非空
        if not dataset_name:
            logger.error("数据集名称不能为空")
            return None
        try:
            existing_dataset = session.query(cls).filter(
                cls.dataset_name == dataset_name,
                cls.del_flag == 0
            ).first()
            if existing_dataset:
                logger.error(f"数据集名称已存在: {dataset_name}")
                return None
        except Exception as e:
            logger.error(f"查询数据集时出错 (数据集名称: {dataset_name}): {e}", exc_info=True)
            session.rollback()
            return None    
        # 创建新数据集
        try:
            new_dataset = DatasetModel(
                dataset_name=dataset_name,
                dataset_category=dataset_category,
                status=status,
                content_size=0,
                remark=remark,
                del_flag=0,
                created_time=datetime.now(timezone(timedelta(hours=8)))  # 设置为中国时区(UTC+8)
            )
            session.add(new_dataset)
            session.commit()
            logger.info(f"已成功添加数据集 (名称: {dataset_name}, 类别: {dataset_category})")
            return new_dataset
        except ValueError as ve:
            logger.error(f"无效的类别或状态值 (数据集名称: {dataset_name}, 类别: {dataset_category}, 状态: {status}): {ve}")
            session.rollback()
            return None
        except Exception as e:
            logger.error(f"添加数据集时出错 (数据集名称: {dataset_name}): {e}", exc_info=True)
            session.rollback()
            return None
    
    @classmethod
    def get_dataset_by_id(cls, session, dataset_id):
        """根据ID获取数据集"""
        try:
            dataset = session.query(cls).filter(cls.id == dataset_id).first()
            return dataset
        except Exception as e:
            logger.error(f"获取数据集时出错 (ID: {dataset_id}): {e}", exc_info=True)
            session.rollback()
            return None
    @classmethod
    def get_datasetid_by_name(cls, session, dataset_name):
        """根据名称获取数据集ID"""
        try:
            dataset = session.query(cls).filter(cls.name == dataset_name).first()
            return dataset.id if dataset else None
        except Exception as e:
            logger.error(f"获取数据集ID时出错 (名称: {dataset_name}): {e}", exc_info=True)
            session.rollback()
            return None

    @classmethod
    def delete_dataset(cls, session, dataset_id):
        """删除数据集"""
        try:
            dataset = session.query(cls).filter(cls.id == dataset_id).first()
            if dataset:
                dataset.del_flag = 1
                session.commit()
                logger.info(f"已成功删除数据集 (ID: {dataset_id})")
                return True
            else:
                logger.warning(f"数据集不存在 (ID: {dataset_id})")
                return False
        except Exception as e:
            logger.error(f"删除数据集时出错 (ID: {dataset_id}): {e}", exc_info=True)
            session.rollback()
            return False

    @classmethod
    def update_dataset(cls, session, dataset_id, dataset_data):
        """更新数据集"""    
        if dataset_data.get('dataset_name'):
            # 校验数据集名称是否已存在且未删除且非空
            try:
                existing_dataset = session.query(cls).filter(
                    cls.dataset_name == dataset_data.get('dataset_name'),
                    cls.del_flag == 0
                ).first()
                if existing_dataset and existing_dataset.id != dataset_id:
                    logger.error(f"数据集名称已存在: {dataset_data.get('dataset_name')}")
                    return False
                # 更新数据集
                try:
                    dataset = session.query(cls).filter(cls.id == dataset_id).first()
                    if dataset:
                        dataset.dataset_name = dataset_data.get('dataset_name')
                        dataset.dataset_category = DatasetCategory(dataset_data.get('dataset_category'))
                        dataset.status = DatasetStatus(dataset_data.get('status'))
                        dataset.remark = dataset_data.get('remark')
                        dataset.content_size = dataset_data.get('content_size')
                        dataset.updated_time = datetime.now(timezone(timedelta(hours=8)))  # 设置为中国时区(UTC+8)
                        session.commit()
                        logger.info(f"已成功更新数据集 (ID: {dataset_id})")
                        return True
                    else:
                        logger.warning(f"数据集不存在 (ID: {dataset_id})")
                        return False
                except ValueError as ve:
                    logger.error(f"无效的类别或状态值 (数据集名称: {dataset_data.get('dataset_name')}, 类别: {dataset_data.get('dataset_category')}, 状态: {dataset_data.get('status')}): {ve}")
                    session.rollback()
                    return False
                except Exception as e:
                    logger.error(f"更新数据集时出错 (ID: {dataset_id}): {e}", exc_info=True)
                    session.rollback()
                    return False
            except Exception as e:
                logger.error(f"查询数据集时出错 (数据集名称: {dataset_data.get('dataset_name')}): {e}", exc_info=True)
                session.rollback()
                return False