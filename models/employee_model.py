from sqlalchemy import Column, Integer, String,text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    department = Column(String(50))

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()
    @classmethod
    def get_all2(cls, session):
        sql = text("""
            SELECT * FROM employee 
            WHERE id = :id 
        """)
        params = {"id": 1}

        # 执行并获取全部结果‌:ml-citation{ref="6" data="citationList"}
        result = session.execute(sql, params)
        return result.all()