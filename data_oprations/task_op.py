
import time
from datetime import datetime
from models.Models import Label_, LabelSys_, Task_, TaskRecords_, Document_, TaggingRecords_
from schemas.Schemas import Task
from data_oprations.database import SessionLocal
# 奇怪了，明明在同一个文件夹，为啥不能直接导入database？
from data_oprations.snow_flake import MySnow
import pandas as pd
my_snow = MySnow(2)
import traceback


def get_summary():
    """
    获取所有打标任务的一个总览信息.
    包括名称，描述，分类体系名称列表，创建时间，完成进度（待定）

    返回：None或者summary
    summary格式：
    [{'name':str,'desc':str,'create_time':str,
    'num_docs':int, 'num_tagged_docs':int,
    'label_sys_list':[{'id':int, 'name':str}]}]
    """
    sess = SessionLocal()
    tasks = sess.query(Task_.id,Task_.name,Task_.desc,Task_.create_time).all()
    if not tasks:
        sess.close()
        return None

    task_summary = []
    for task in tasks:
        # 查询label system关联信息：
        label_sys_list = []
        lss = sess.query(LabelSys_.id, LabelSys_.name).join(TaskRecords_)\
                     .filter(TaskRecords_.task_id == task.id).all()
        for ls in lss:
            label_sys_list.append({'id': ls.id, 'name': ls.name})

        # 查询document关联信息：
        docs = sess.query(Document_.id).filter(Document_.task_id == task.id).all()
        tagged_docs = sess.query(Document_.id).filter(Document_.task_id == task.id)\
                                              .filter(Document_.state == 1).all()

        task_summary.append({'id': task.id, 'name': task.name, 'desc': task.desc, 'create_time': task.create_time,
                             'num_docs': len(docs), 'num_tagged_docs': len(tagged_docs), 'label_sys_list': label_sys_list})
    sess.close()
    return task_summary


def count_docs(task_id: int):
    sess = SessionLocal()
    docs = sess.query(Document_.id).filter(Document_.task_id == task_id).all()
    tagged_docs = sess.query(Document_.id).filter(Document_.task_id == task_id) \
        .filter(Document_.state == 1).all()
    # unsure_docs = sess.query(Document_.id).filter(Document_.task_id == task_id) \
    #     .filter(Document_.state == 2).all()
    counts = {"num_docs": len(docs), "num_tagged_docs": len(tagged_docs)} # , "num_unsure_docs": len(unsure_docs)
    sess.close()
    return counts


def get_tagged_docs(task_id: int, user_id: int):
    sess = SessionLocal()
    if user_id == -1:
        docs = sess.query(Document_.id,Document_.title).filter(Document_.task_id == task_id).filter(Document_.state == 1).all()
    else:
        docs = sess.query(Document_.id,Document_.title).filter(Document_.task_id == task_id).filter(Document_.state == 1)\
            .join(TaggingRecords_).filter(TaggingRecords_.user_id == user_id).all()
    sess.close()
    if not docs:
        return None
    return [{'doc_id':doc.id, 'title':doc.title} for doc in docs]


def get_detail_by_id(task_id: int):
    sess = SessionLocal()
    task = sess.query(Task_.id, Task_.name, Task_.desc, Task_.create_time).filter(Task_.id == task_id).first()
    if not task:
        sess.close()
        return None
    ls_list = sess.query(LabelSys_.id, LabelSys_.name, LabelSys_.multi).join(TaskRecords_)\
                         .filter(TaskRecords_.task_id == task_id).all()
    print(ls_list)
    label_sys_list = []
    label_list = []
    for ls in ls_list:
        label_sys_list.append({"id": ls.id, "name": ls.name, "multi":ls.multi})
        l_list = sess.query(Label_.id, Label_.name).join(LabelSys_).filter(Label_.label_sys_id == ls.id).all()
        label_list.append([{"id": l.id, "name": l.name} for l in l_list])
    res = {"name": task.name, "desc": task.desc, "create_time": task.create_time,
           "label_sys_list": label_sys_list, "label_list": label_list}
    sess.close()
    return res


def check_task_name(task_name:str):
    sess = SessionLocal()
    res = sess.query(Task_).filter(Task_.name==task_name).first()
    sess.close()
    if res == None:
        return 0
    else:
        return 1


def add_task_info(task : Task, task_id, admin_id):
    """
    添加新的打标任务的基础信息.
    (当前默认admin_id=1； 暂不考虑state,doc_type信息)

    从前端接收json信息(暂定)
    json格式如下：
    {
     'name':str,
     'desc':str,
     'label_sys_ids':[str]
    }
    """
    sess = SessionLocal()
    # 插入task表：
    current_time_str = datetime.fromtimestamp(int(time.time()))
    db_task = Task_(id=task_id,name=task.name,desc=task.desc,admin_id=admin_id,create_time=current_time_str) # ??
    sess.add(db_task)
    sess.commit()

    # 插入task_records表
    for label_sys_id in task.label_sys_ids:
        db_task_record = TaskRecords_(task_id=int(task_id),label_sys_id=label_sys_id)
        sess.add(db_task_record)
    sess.commit()
    sess.close()
    return {'task_id':task_id}


def upload_to_db(df,task_id):
    """
    df: 通过检查的dataframe
    task_id: task_id
    """
    # 开始往数据库插入：
    sess = SessionLocal()
    num_uploaded_docs = len(df)
    num_success_docs = 0
    for item in df.iterrows():
        try:
            title = item[1]['title']
            content = item[1]['content']
            doc_id = int(my_snow.get_id())
            db_doc = Document_(id=doc_id,task_id=task_id,title=title,content=content,state=0) #初次上传，state都为0
            sess.add(db_doc)
            # sess.refresh(db_doc)
            num_success_docs += 1
        except:
            sess.rollback() # 报错的话需要通过rollback来撤销当前session的操作
            print(traceback.format_exc())
    sess.commit()
    sess.close()
    return {"num_uploaded_docs": num_uploaded_docs, "num_success_docs": num_success_docs}


def delete_task(task_id:int):
    sess = SessionLocal()
    res = sess.query(Task_).filter(Task_.id == task_id).delete()
    sess.commit()
    sess.close()
    return res











