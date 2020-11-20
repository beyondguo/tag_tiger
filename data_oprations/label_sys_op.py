"""
与分类体系、标签相关的各种操作
"""
import time
from datetime import datetime
from sqlalchemy import func
from typing import List, Optional
from models.Models import LabelSys_, Label_, Task_, TaskRecords_, Document_, TaggingRecords_
from schemas.Schemas import LabelSys
from data_oprations.database import SessionLocal
# 奇怪了，明明在同一个文件夹，为啥不能直接导入database？
from data_oprations.snow_flake import MySnow
import pandas as pd
from collections import Counter


my_snow = MySnow(1)

"""
SQL语句：
SELECT label_sys.name, label_sys.desc, label_sys.multi, count(label.name) AS num_labels
FROM label_sys
JOIN label
ON label_sys.id = label.label_sys_id
GROUP BY label.name
"""


def get_summary():
    """
    获取所有分类体系的一个总览信息.
    返回：None或者summary
    summary格式：
    [{'id':int,'name':str,'desc':str,'multi':str,'num_labels':str},...]
    """
    sess = SessionLocal()
    res = sess.query(LabelSys_.id, LabelSys_.name, LabelSys_.desc, LabelSys_.multi,
                     func.count(Label_.id).label('num_labels')).join(Label_) \
                     .group_by(LabelSys_.id).all()
    if not res:
        sess.close()
        return None
    summary = []
    for each in res:
        summary.append({'id': each.id, 'name': each.name, 'desc': each.desc,
                        'multi': str(each.multi), 'num_labels': str(each.num_labels)})
    sess.close()
    return summary


def get_detail_by_name(label_sys_name: str):
    """
    获取某分类体系详情.

    返回：None或label_sys_detail

    label_sys_detail格式：
    {'id':str,'name':str,'desc':str,'multi':str,'num_labels':str,
     'labels':[{'id':str,'name':str,'desc':str},...]}
    """
    sess = SessionLocal()
    label_sys = sess.query(LabelSys_).filter(LabelSys_.name == label_sys_name).first()
    if not label_sys:
        sess.close()
        return None
    labels = sess.query(Label_).filter(Label_.label_sys_id == label_sys.id).all()
    label_sys_detail = {'id': label_sys.id, 'name': label_sys.name, 'desc': label_sys.desc,
                        'multi': str(label_sys.multi), 'num_labels': len(labels), 'labels': []}
    for label in labels:
        label_sys_detail['labels'].append({'id': label.id, 'name': label.name, 'desc': label.desc})
    sess.close()
    return label_sys_detail


def get_detail_by_id(label_sys_id: int):
    sess = SessionLocal()
    label_sys = sess.query(LabelSys_).filter(LabelSys_.id == label_sys_id).first()
    if not label_sys:
        sess.close()
        return None
    labels = sess.query(Label_).filter(Label_.label_sys_id == label_sys_id).all()
    label_sys_detail = {'id': label_sys_id, 'name': label_sys.name, 'desc': label_sys.desc,
                        'multi': str(label_sys.multi), 'num_labels': len(labels), 'labels': []}
    for label in labels:
        label_sys_detail['labels'].append({'id': label.id, 'name': label.name, 'desc': label.desc})
    sess.close()
    return label_sys_detail

def check_label_sys_name(label_sys_name: str):
    sess = SessionLocal()
    res = sess.query(LabelSys_).filter(LabelSys_.name == label_sys_name).first()
    sess.close()
    if res is None:
        return 0
    else:
        return 1


def get_label_sys_list():
    sess = SessionLocal()
    res = sess.query(LabelSys_.id, LabelSys_.name).all()
    sess.close()
    if not res:
        return None
    label_sys_list = []
    for ls in res:
        label_sys_list.append({'id': ls.id, 'name': ls.name})
    return label_sys_list


def add_label_sys(label_sys: LabelSys, admin_id: int):
    """
    添加新的分类体系.
    label_sys的json格式如下：
    {
     'name':str,
     'desc':str,
     'multi':int,
     'labels':[{'name':str,'desc':str,'keywords':str},
               {'name':str,'desc':str,'keywords':str},...]
    }
    """
    if check_label_sys_name(label_sys.name):
        return None
    sess = SessionLocal()
    label_sys_id = int(my_snow.get_id())
    db_label_sys = LabelSys_(id=label_sys_id, name=label_sys.name, desc=label_sys.desc,
                             multi=label_sys.multi, admin_id=admin_id)  # （当前默认admin_id=1）
    sess.add(db_label_sys)
    sess.commit()
    sess.refresh(db_label_sys)

    label_id_list = []
    for label in label_sys.labels:
        label_id = int(my_snow.get_id())
        label_id_list.append(label_id)
        db_label = Label_(id=label_id, name=label.name, desc=label.desc, keywords=label.keywords, label_sys_id=label_sys_id)
        sess.add(db_label)
        sess.commit()
        sess.refresh(db_label)

    res = {'label_sys_id': label_sys_id, 'label_id_list': label_id_list}
    sess.close()
    return res


def delete_label_sys(label_sys_id:int):
    sess = SessionLocal()
    res = sess.query(LabelSys_).filter(LabelSys_.id == label_sys_id).delete()
    sess.commit()
    sess.close()
    return res


def get_related_tasks(label_sys_id: int):
    sess = SessionLocal()
    recs = sess.query(Task_).join(TaskRecords_).filter(TaskRecords_.label_sys_id == label_sys_id).all()
    tasks = []
    for rec in recs:
        tasks.append({'id':rec.id, 'name': rec.name})
    sess.close()
    return tasks


def label_counts(label_sys_id, task_id_list):
    """
    目前只统计了单标签的数量
    """
    sess = SessionLocal()
    if not task_id_list:
        res = sess.query(Document_.id, Label_.name).filter(Document_.state == 1).join(TaggingRecords_).join(Label_)\
            .filter(Label_.label_sys_id == label_sys_id).all()
    else:
        res = sess.query(Document_.id, Label_.name).filter(Document_.state == 1).join(TaggingRecords_).join(Label_)\
            .filter(Label_.label_sys_id == label_sys_id).filter(Document_.task_id.in_(task_id_list)).all() ## 特殊的in语句

    doc_label = {}
    for each in res:
        if each.id in doc_label.keys():
            doc_label[each.id] = doc_label[each.id] + ',' + each.name
        else:
            doc_label[each.id] = each.name
    labels = list(doc_label.values())


    # if not task_id_list:
    #     res = sess.query(Label_.name).join(TaggingRecords_).join(Document_).filter(Document_.state == 1) \
    #          .filter(Label_.label_sys_id == label_sys_id).all()
    # else:
    #     res = sess.query(Label_.name).join(TaggingRecords_).join(Document_).filter(Document_.state == 1) \
    #         .filter(Label_.label_sys_id == label_sys_id).filter(Document_.task_id.in_(task_id_list)).all()
    # labels = [each.name for each in res]
    c  =Counter(labels)
    sess.close()
    return c


def label_sys_tagged_data_download(label_sys_id, task_id_list):
    current_time_str = str(datetime.fromtimestamp(int(time.time()))).replace(' ','-').replace(':','-')
    sess = SessionLocal()
    ls_info = sess.query(LabelSys_).filter(LabelSys_.id == label_sys_id).first()
    ls_name = ls_info.name
    file_name = ls_name+'__'+current_time_str
    if not task_id_list:
        res = sess.query(Document_.id, Document_.title, Document_.content, Label_.label_sys_id, Label_.name).filter(Document_.state == 1).join(TaggingRecords_).join(Label_)\
            .filter(Label_.label_sys_id == label_sys_id).all()
    else:
        res = sess.query(Document_.id, Document_.title, Document_.content, Label_.label_sys_id, Label_.name).filter(Document_.state == 1).join(TaggingRecords_).join(Label_)\
            .filter(Label_.label_sys_id == label_sys_id).filter(Document_.task_id.in_(task_id_list)).all() ## 特殊的in语句

    d = {}
    for each in res:
        if each.id in d.keys():
            d[each.id]['label'] = d[each.id]['label'] + ',' + each.name
        else:
            d[each.id] = {'title':each.title, 'content':each.content, 'label':each.name}
    df = pd.concat([pd.DataFrame(d.keys(),columns=['doc_id']),pd.DataFrame(d.values())],axis=1)
    df.to_csv('download_datasets/%s.csv'%file_name)
    sess.close()
    return file_name