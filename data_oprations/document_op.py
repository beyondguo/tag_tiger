import time
from datetime import datetime
from models.Models import Document_, TaggingRecords_, Label_
from schemas.Schemas import TaggingRecord
from data_oprations.database import SessionLocal
from data_oprations.snow_flake import MySnow
from random import randrange
my_snow = MySnow(3)


def fetch_one_doc(task_id: int):
    sess = SessionLocal()
    # 随机获取一条记录
    docs = sess.query(Document_.id).filter(Document_.task_id == task_id).filter(Document_.state == 0).all()
    if not docs:
        return None
    rand = randrange(len(docs))
    current_doc = docs[rand]
    # sess.query(Document_).filter(Document_.id == current_doc.id).update({Document_.state:1}) # 一经读取，就马上设为“tagged”
    # sess.commit()
    current_doc = sess.query(Document_).filter(Document_.id == current_doc.id).first()
    res = {"id": current_doc.id, "title": current_doc.title, "content": current_doc.content}
    sess.close()
    return res


def view_one_doc(doc_id: int):
    sess = SessionLocal()
    doc = sess.query(Document_.title, Document_.content).filter(Document_.id == doc_id).first()
    if not doc:
        sess.close()
        return None
    labels = sess.query(Label_.id, Label_.name).join(TaggingRecords_).filter(TaggingRecords_.doc_id == doc_id).all()
    doc_info = {'id':doc_id,'title':doc.title,'content':doc.content,
                'labels':[{'id':l.id,'name':l.name} for l in labels]}
    sess.close()
    return doc_info


def check_doc_state(doc_id: int):
    sess = SessionLocal()
    doc = sess.query(Document_.id,Document_.state).filter(Document_.id == doc_id).first()
    sess.close()
    if not doc: # 没有这个doc
        return -1
    if doc.state == 0: # 有，且未打标
        return 0
    else:  # 有，且已打标
        return 1


def tag_one_doc(tagging_record: TaggingRecord, user_id: int):
    """
    tagging_record
    {
    "doc_id": int,
    "user_id": int,
    "label_id_list": [int]
    }
    """
    state = check_doc_state(tagging_record.doc_id)
    if state == -1: # doc_id不存在，这里支持对已打标的文章进行修改
        return None
    sess = SessionLocal()
    current_time_str = str(datetime.fromtimestamp(int(time.time())))
    # 先检查该doc是否已被打标，有的话则删除其记录：
    recs = sess.query(TaggingRecords_).filter(TaggingRecords_.doc_id == tagging_record.doc_id).delete()

    for label_id in tagging_record.label_id_list:
        db_tagging_record = TaggingRecords_(doc_id=tagging_record.doc_id, label_id=label_id,
                                            user_id=user_id, create_time=current_time_str)
        sess.add(db_tagging_record)
        sess.commit()
        sess.refresh(db_tagging_record)
    # 再次确认一下把state设为1：
    sess.query(Document_).filter(Document_.id == tagging_record.doc_id).update({Document_.state: 1})
    sess.commit()
    sess.close()
    return 1


def pass_ont_doc(doc_id):
    sess = SessionLocal()
    sess.query(Document_).filter(Document_.id == doc_id).update({Document_.state:0})
    sess.commit()
    sess.close()
    return 1



