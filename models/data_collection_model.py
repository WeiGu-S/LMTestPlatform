from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, Index
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
# import enum
import math
from utils.logger import get_logger
from datetime import datetime, timezone, timedelta
import uuid

Base = declarative_base()
logger = get_logger("data_collection_model")

class DataCollectionModel(Base):

    __tablename__ = 't_data_collections'

    collection_id = Column(String(20), primary_key=True, comment='数据集ID')
    project_name = Column(String(20), nullable=True, comment='所属项目')
    collection_name = Column(String(20), nullable=False, comment='数据集名称')
    created_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment='创建时间')
    created_by = Column(String(20), nullable=True, comment='创建人')
    updated_time = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    updated_by = Column(String(20), nullable=True, comment='更新人')
    del_flag = Column(Integer, nullable=False, default=0, comment='删除标志位: 0未删除 1删除')

    def to_dict(self):
        """将模型实例转换为字典，便于视图层使用"""
        return {
            "collection_id": self.collection_id,
            "project_name": self.project_name,
            "collection_name": self.collection_name,
            "del_flag": self.del_flag,
            "created_time": self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None, # 格式化时间
            "created_by": self.created_by
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
            if filters.get('collection_name'):
                search_term = f"%{str(filters['collection_name']).strip()}%"
                query = query.filter(cls.collection_name.ilike(search_term))

            # 项目名称过滤
            if filters.get('project_name'):
                search_term = f"%{str(filters['project_name']).strip()}%"
                query = query.filter(cls.project_name.ilike(search_term))

            # # 状态过滤
            # if filters.get('status') and filters['status'] != '全部':
            #     status_map = {s.value: s for s in data_collectionStatus}
            #     if str(filters['status']) in status_map:
            #         query = query.filter(cls.status == status_map[str(filters['status'])])
            #     else:
            #         logger.warning(f"Invalid status value: {filters['status']}")

            # # 分类过滤
            # if filters.get('data_collection_category') and filters['data_collection_category'] != '全部':
            #     category_map = {c.value: c for c in data_collectionCategory}
            #     if str(filters['data_collection_category']) in category_map:
            #         query = query.filter(cls.data_collection_category == category_map[str(filters['data_collection_category'])])
            #     else:
            #         logger.warning(f"Invalid category value: {filters['data_collection_category']}")

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
    def get_paginated_data_collections(cls, session, page=1, per_page=10, filters=None):
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
            data_collections = query.order_by(cls.created_time.desc()).offset(offset).limit(per_page).all()
            
            # 将数据集对象转换为字典
            data_collection_dicts = [d.to_dict() for d in data_collections]
            
            return data_collection_dicts, total_items, total_pages
        except Exception as e:
            logger.error(f"获取分页数据集时出错: {e}", exc_info=True)
            session.rollback() # 出错时回滚
            return [], 0, 1

    @classmethod
    def get_all_data_collections(cls, session, filters=None):
        """获取所有数据集，基于过滤条件（用于导出）"""
        if not session:
            logger.error("获取所有数据集时数据库会话不可用")
            return []

        query = session.query(cls.del_flag == 0)
        query = cls._apply_filters(query, filters)

        try:
            data_collections = query.order_by(cls.created_time.desc()).all()
            return [d.to_dict() for d in data_collections]
        except Exception as e:
            logger.error(f"获取所有数据集时出错: {e}", exc_info=True)
            session.rollback()
            return []

    
    @classmethod
    def add_data_collection(cls, session, collection_datas):
        """添加新数据集""" 
        project_name = collection_datas.get('project_name')     
        collection_name = collection_datas.get('collection_name')
        # 生成不超过 20 位的纯数字唯一标识符
        collection_id = str(uuid.uuid4().int)[:20]        
        # 校验数据集名称是否已存在且未删除且非空
        if not collection_name:
            logger.error("数据集名称不能为空")
            return None
        try:
            existing_data_collection = session.query(cls).filter(
                project_name == project_name,
                cls.collection_name == collection_name,
                cls.del_flag == 0
            ).first()
            if existing_data_collection:
                logger.error(f"项目{project_name}下数据集名称已存在: {collection_name}")
                return None
        except Exception as e:
            logger.error(f"查询数据集时出错 (数据集名称: {collection_name}): {e}", exc_info=True)
            session.rollback()
            return None    
        # 创建新数据集
        try:
            new_data_collection = DataCollectionModel(
                collection_id=collection_id,
                project_name=project_name,
                collection_name=collection_name,
                del_flag=0,
                created_time=datetime.now(timezone(timedelta(hours=8))),  # 设置为中国时区(UTC+8)
                created_by="user"
            )
            session.add(new_data_collection)
            session.commit()
            logger.info(f"已成功添加数据集 (名称: {collection_name})")
            return new_data_collection
        except ValueError as ve:
            logger.error(f"无效的类别或状态值 (数据集名称: {collection_name}")
            session.rollback()
            return None
        except Exception as e:
            logger.error(f"添加数据集时出错 (数据集名称: {collection_name}): {e}", exc_info=True)
            session.rollback()
            return None
    
    @classmethod
    def get_data_collection_by_id(cls, session, collection_id):
        """根据ID获取数据集"""
        try:
            data_collection = session.query(cls).filter(cls.collection_id == collection_id).first()
            return data_collection
        except Exception as e:
            logger.error(f"获取数据集时出错 (ID: {collection_id}): {e}", exc_info=True)
            session.rollback()
            return None
    @classmethod
    def get_data_collectionid_by_name(cls, session, collection_name, project_name):
        """根据名称获取数据集ID"""
        try:
            data_collection = session.query(cls).filter(
                cls.collection_name == collection_name,
                cls.project_name == project_name,
                cls.del_flag == 0           
            ).first()
            return data_collection.collection_id if data_collection else None
        except Exception as e:
            logger.error(f"获取数据集ID时出错 (名称: {collection_name}): {e}", exc_info=True)
            session.rollback()
            return None

    @classmethod
    def delete_data_collection(cls, session, collection_id):
        """删除数据集"""
        try:
            data_collection = session.query(cls).filter(cls.collection_id == collection_id).first()
            if data_collection:
                data_collection.del_flag = 1
                session.commit()
                logger.info(f"已成功删除数据集 (ID: {collection_id})")
                return True
            else:
                logger.warning(f"数据集不存在 (ID: {collection_id})")
                return False
        except Exception as e:
            logger.error(f"删除数据集时出错 (ID: {collection_id}): {e}", exc_info=True)
            session.rollback()
            return False

    @classmethod
    def update_data_collection(cls, session, collection_id, collection_datas):
        """更新数据集"""    
        if collection_datas.get('collection_name'):
            # 校验数据集名称是否已存在且未删除且非空
            try:
                existing_data_collection = session.query(cls).filter(
                    collection_datas.get('project_name') == cls.project_name, # 确保项目名称匹配，防止误删除其他项目下的同名数据集
                    cls.collection_name == collection_datas.get('collection_name'),
                    cls.del_flag == 0
                ).first()
                if existing_data_collection and existing_data_collection.collection_id != collection_id:
                    logger.error(f"数据集名称已存在: {collection_datas.get('collection_name')}")
                    return False
                # 更新数据集
                try:
                    data_collection = session.query(cls).filter(cls.collection_id == collection_id).first()
                    if data_collection:
                        data_collection.collection_name = collection_datas.get('collection_name')
                        data_collection.project_name = collection_datas.get('project_name')
                        data_collection.updated_by = collection_datas.get('updated_by')
                        data_collection.updated_time = datetime.now(timezone(timedelta(hours=8)))  # 设置为中国时区(UTC+8)
                        session.commit()
                        logger.info(f"已成功更新数据集 (ID: {collection_id})")
                        return True
                    else:
                        logger.warning(f"数据集不存在 (ID: {collection_id})")
                        return False
                except ValueError as ve:
                    logger.error(f"无效的类别或状态值 (数据集名称: {collection_datas.get('collection_name')}")
                    session.rollback()
                    return False
                except Exception as e:
                    logger.error(f"更新数据集时出错 (ID: {collection_id}): {e}", exc_info=True)
                    session.rollback()
                    return False
            except Exception as e:
                logger.error(f"查询数据集时出错 (数据集名称: {collection_datas.get('collection_name')}): {e}", exc_info=True)
                session.rollback()
                return False