from pydantic import BaseModel
from typing import Optional, List

class Admin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username: str
    password: str

class Label(BaseModel):
    name: str
    desc: Optional[str] = None


class LabelSys(BaseModel):
    name: str
    desc: Optional[str] = None
    multi: int
    # relation with labels:
    labels: List[Label] = []


class Task(BaseModel):
    name: str
    desc: Optional[str] = None
    # relation with label systems:
    label_sys_ids : List[int]
    # label_sys_names: List[str] = [] # 这里只用存放分类体系的名称即可


class TaggingRecord(BaseModel):
    doc_id : int
    label_id_list : List[int] = []


