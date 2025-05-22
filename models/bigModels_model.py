from logging import config
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
logger = get_logger("bigModels_model")

class BigModelsModel(Base):
    __tablename__ = 't_lm_config'

    config_id = Column(String(20), primary_key=True, comment='配置ID')
    model_name = Column(String(200), nullable=True, comment='模型名称')
    config_type = Column(Integer, nullable=True, comment='配置用途(数据字典：被测模型、裁判模型等)')
    model_type = Column(Integer, nullable=True, comment='模型类型(数据字典：远程模型、本地模型等)')
    is_stream = Column(Integer, nullable=True, comment='是否流式') # 0: 非流式 1:流式
    url_info = Column(String(200), nullable=True, comment='URL信息')
    headers = Column(String, nullable=True, comment='请求头')
    body = Column(String, nullable=True, comment='请求体')
    res_path = Column(String, nullable=True, comment='解析路径')
    model_file = Column(String, nullable=True, comment='模型文件')
    created_time = Column(DateTime, nullable=True, default=datetime.utcnow, comment='创建时间')
    created_by = Column(String(20), nullable=True, comment='创建人')
    updated_time = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    updated_by = Column(String(20), nullable=True, comment='更新人')
    del_flag = Column(Integer, nullable=False, default=0, comment='删除标志位(0未删除1删除)')

    def to_dict(self):
        """将模型实例转换为字典，便于视图层使用"""
        return {
            "config_id": self.config_id,
            "model_name": self.model_name,
            "config_type": self.config_type,
            "model_type": self.model_type,
            "is_stream": self.is_stream,
            "url_info": self.url_info,
            "headers": self.headers,
            "body": self.body,
            "res_path": self.res_path,
            "model_file": self.model_file,
            "created_time": self.created_time.strftime('%Y-%m-%d %H:%M:%S') if self.created_time else None, # 格式化时间
            "created_by": self.created_by,
            "updated_time": self.updated_time.strftime('%Y-%m-%d %H:%M:%S') if self.updated_time else None, # 格式化时间
            "updated_by": self.updated_by
        }

    @classmethod
    def _apply_filters(cls, query, filters):
        """安全地应用过滤条件到查询，兼容QDate类型"""
        if not filters:
            return query.filter(cls.del_flag == 0)

        logger.debug(f"Applying filters: {str(filters)}")

        try:
            # 过滤已删除的模型
            query = query.filter(cls.del_flag == 0)
            # 模型名称过滤
            if filters.get('model_name'):
                search_term = f"%{str(filters['model_name']).strip()}%"
                query = query.filter(cls.model_name.ilike(search_term))

            # 模型类型过滤
            if filters.get('model_type'):
                search_term = f"%{str(filters['model_type']).strip()}%"
                query = query.filter(cls.model_type.ilike(search_term))

            # 配置用途过滤
            if filters.get('config_type'):
                search_term = f"%{str(filters['config_type']).strip()}%"
                query = query.filter(cls.config_type.ilike(search_term))

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
    def get_paginated_models(cls, session, page=1, per_page=10, filters=None):
        """获取分页的模型，基于过滤条件"""
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
            models = query.order_by(cls.created_time.desc()).offset(offset).limit(per_page).all()
            
            # 将模型对象转换为字典
            models_dicts = [d.to_dict() for d in models]
            
            return models_dicts, total_items, total_pages
        except Exception as e:
            logger.error(f"获取分页模型时出错: {e}", exc_info=True)
            session.rollback() # 出错时回滚
            return [], 0, 1

    @classmethod
    def get_all_models(cls, session, filters=None):
        """获取所有模型，基于过滤条件（用于导出）"""
        if not session:
            logger.error("获取所有模型时数据库会话不可用")
            return []

        query = session.query(cls.del_flag == 0)
        query = cls._apply_filters(query, filters)

        try:
            models = query.order_by(cls.created_time.desc()).all()
            return [d.to_dict() for d in models]
        except Exception as e:
            logger.error(f"获取所有模型时出错: {e}", exc_info=True)
            session.rollback()
            return []
    
    @classmethod
    def add_model(cls, session, model_datas):
        """添加新模型""" 
        config_id = str(uuid.uuid4().int)[:20]
        model_name = model_datas.get('model_name')
        model_type = model_datas.get('model_type')
        config_type = model_datas.get('config_type')
        is_stream = model_datas.get('is_stream')
        url_info = model_datas.get('url_info')
        key_info = model_datas.get('key_info')  
        headers = model_datas.get('headers')
        body = model_datas.get('body')
        res_path = model_datas.get('res_path')
        # 校验模型名称是否已存在且未删除且非空
        if not model_name:
            logger.error("模型名称不能为空")
            return None
        try:
            existing_model = session.query(cls).filter(
                cls.model_name == model_name,
                cls.del_flag == 0
            ).first()
            if existing_model:
                logger.error(f"模型名称已存在: {model_name}")
                return None
        except Exception as e:
            logger.error(f"查询模型时出错 (模型名称: {model_name}): {e}", exc_info=True)
            session.rollback()
            return None    
        # 创建新模型
        try:
            new_model = BigModelsModel(
                config_id=config_id,
                model_name=model_name,
                config_type=config_type,
                model_type=model_type,
                is_stream=is_stream,
                url_info=url_info,
                headers=headers,
                body=body,
                res_path=res_path,
                del_flag=0,
                created_time=datetime.now(timezone(timedelta(hours=8))),  # 设置为中国时区(UTC+8)
                created_by="user"
            )
            session.add(new_model)
            session.commit()
            logger.info(f"已成功添加模型 (名称: {model_name})")
            return new_model
        except ValueError as ve:
            logger.error(f"无效的类别或状态值 (模型名称: {model_name}")
            session.rollback()
            return None
        except Exception as e:
            logger.error(f"添加模型时出错 (模型名称: {model_name}): {e}", exc_info=True)
            session.rollback()
            return None
    
    @classmethod
    def get_model_info_by_id(cls, session, config_id):
        """根据ID获取模型"""
        try:
            model_data = session.query(cls).filter(cls.config_id == config_id).first()
            return model_data
        except Exception as e:
            logger.error(f"获取模型时出错 (ID: {config_id}): {e}", exc_info=True)
            session.rollback()
            return None

    @classmethod
    def get_config_id_by_name(cls, session, model_name):
        """根据名称获取模型ID"""
        try:
            model_data = session.query(cls).filter(
                cls.model_name == model_name,
                cls.del_flag == 0           
            ).first()
            return model_data.config_id if model_data else None
        except Exception as e:
            logger.error(f"获取模型ID时出错 (名称: {model_name}): {e}", exc_info=True)
            session.rollback()
            return None

    @classmethod
    def delete_model(cls, session, config_id):
        """删除模型"""
        try:
            model = session.query(cls).filter(cls.config_id == config_id).first()
            if model:
                model.del_flag = 1
                session.commit()
                logger.info(f"已成功删除模型 (ID: {config_id})")
                return True
            else:
                logger.warning(f"模型不存在 (ID: {config_id})")
                return False
        except Exception as e:
            logger.error(f"删除模型时出错 (ID: {config_id}): {e}", exc_info=True)
            session.rollback()
            return False

    @classmethod
    def update_model_info(cls, session, config_id, model_datas):
        """更新模型"""    
        if model_datas.get('model_name'):
            # 校验模型名称是否已存在且未删除且非空
            try:
                existing_model = session.query(cls).filter(
                    cls.model_name == model_datas.get('model_name'),
                    cls.del_flag == 0
                ).first()
                if existing_model and existing_model.config_id != config_id:
                    logger.error(f"模型名称已存在: {model_datas.get('model_name')}")
                    return False
                # 更新模型
                try:
                    model = session.query(cls).filter(cls.config_id == config_id).first()
                    if model:
                        model.model_name = model_datas.get('model_name')
                        model.config_type = model_datas.get('config_type')
                        model.model_type = model_datas.get('model_type')
                        model.is_stream = model_datas.get('is_stream')
                        model.url_info = model_datas.get('url_info')
                        model.headers = model_datas.get('headers')
                        model.body = model_datas.get('body')
                        model.res_path = model_datas.get('res_path')
                        model.updated_by = model_datas.get('updated_by')
                        model.updated_time = datetime.now(timezone(timedelta(hours=8)))  # 设置为中国时区(UTC+8)
                        session.commit()
                        logger.info(f"已成功更新模型 (ID: {config_id})")
                        return True
                    else:
                        logger.warning(f"模型不存在 (ID: {config_id})")
                        return False
                except ValueError as ve:
                    logger.error(f"无效的类别或状态值 (模型名称: {model_datas.get('model_name')}")
                    session.rollback()
                    return False
                except Exception as e:
                    logger.error(f"更新模型时出错 (ID: {config_id}): {e}", exc_info=True)
                    session.rollback()
                    return False
            except Exception as e:
                logger.error(f"查询模型时出错 (模型名称: {model_datas.get('model_name')}): {e}", exc_info=True)
                session.rollback()
                return False