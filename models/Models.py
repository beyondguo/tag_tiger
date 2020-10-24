from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from data_oprations.database import Base

"""
注：
在mysql中已经定义的表，在这里必须全部定义，才能进行插入操作！
"""


class Admin_(Base):
    __tablename__ = "administrator"
    # 已建表则添加此参数
    __table_args__ = {"useexisting": True} 

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    token = Column(String, nullable=True)


class User_(Base):
    __tablename__ = "user"
    __table_args__ = {"useexisting": True}
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    token = Column(String, nullable=True)



class LabelSys_(Base):
    __tablename__ = "label_sys"
    __table_args__ = {"useexisting": True} 

    id = Column(Integer, primary_key=True)
    name = Column(String)
    desc = Column(String)
    multi = Column(Integer)
    admin_id = Column(Integer, ForeignKey("administrator.id"))


class Label_(Base):
    __tablename__ = "label"
    __table_args__ = {"useexisting": True} 
    id = Column(Integer, primary_key=True)
    name = Column(String)
    desc = Column(String)
    label_sys_id = Column(Integer, ForeignKey("label_sys.id"))


class Task_(Base):
    __tablename__ = "task"
    __table_args__ = {"useexisting": True} 

    id = Column(Integer, primary_key=True)
    name = Column(String)
    desc = Column(String)
    create_time = Column(Date)
    admin_id = Column(Integer, ForeignKey("administrator.id"))
    # docs = relationship("Document_", backref="task", passive_deletes=True)
    # 牛逼，只要Navicat里面设置了外键的CASCADE，就不用在这里设置了


class TaskRecords_(Base):
    __tablename__ = "task_records"
    __table_args__ = {"useexisting": True}
    id = Column(Integer, primary_key=True) # mysql中是自增的
    task_id = Column(Integer, ForeignKey("task.id"))
    label_sys_id = Column(Integer, ForeignKey("label_sys.id"))


class Document_(Base):
    __tablename__ = "document"
    __table_args__ = {"useexisting": True}    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id"))
    title = Column(String)
    content = Column(String)
    state = Column(Integer)
            

class TaggingRecords_(Base):
    __tablename__ = "tagging_records"
    __table_args__ = {"useexisting": True}
    id = Column(Integer, primary_key=True) # mysql中是自增的
    doc_id = Column(Integer, ForeignKey("document.id"))
    label_id = Column(Integer, ForeignKey("label.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    create_time = Column(Date)