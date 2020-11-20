import time
from datetime import datetime
from models.Models import *
from schemas.Schemas import TaggingRecord
from data_oprations.database import SessionLocal
from data_oprations.snow_flake import MySnow
from random import randrange
from data_oprations.ac_search import AhoCorasick
my_snow = MySnow(3)


def fetch_one_doc(task_id: int):
    sess = SessionLocal()
    # 随机获取一条记录
    docs = sess.query(Document_.id).filter(Document_.task_id == task_id).filter(Document_.state == 0).all()
    # 由于要显示关键词，所以需要根据task找出对应的label system中的关键词
    # 这里获取关键词有两种办法（TBD）：
    # 1. 通过参数传进来，这样的话就不用每次都查询库了，在同一个task里面，关键词应该是一样的，但是这样就无法实现实时更新地显示
    # 2. 每次都去查询库中的关键词，这样的话查询量会稍大，但是如果临时更新了关键词，也可以马上在系统上反映出来
    # 2020.11.23 按照上的方法2实现：
    labels = sess.query(Label_).join(LabelSys_).join(TaskRecords_).filter(TaskRecords_.task_id == task_id).all()
    # 收集所有关键词，构建AC自动机：
    kws= []
    for l in labels:
        kws += l.keywords.split(' ')
    AC = AhoCorasick(kws)

    if not docs:
        return None
    rand = randrange(len(docs))
    current_doc = docs[rand]
    # sess.query(Document_).filter(Document_.id == current_doc.id).update({Document_.state:1}) # 一经读取，就马上设为“tagged”
    # sess.commit()
    current_doc = sess.query(Document_).filter(Document_.id == current_doc.id).first()
    highlight_kws = list(AC.search(current_doc.content))
    highlighted_content = current_doc.content
    print('***********highlight_kws***********:\n', highlight_kws)
    if highlight_kws:
        for kw in highlight_kws:
            highlighted_content = highlighted_content.replace(kw,"<b style='color:orange'>"+kw+"</b>")
    res = {"id": current_doc.id, "title": current_doc.title, "content": highlighted_content, "highlight_kws": highlight_kws}

    sess.close()
    return res


def view_one_doc(doc_id: int):
    sess = SessionLocal()
    doc = sess.query(Document_.title, Document_.content).filter(Document_.id == doc_id).first()
    if not doc:
        sess.close()
        return None
    labels = sess.query(Label_.id, Label_.name).join(TaggingRecords_).filter(TaggingRecords_.doc_id == doc_id).all()

    ## 也进行关键词高亮：
    labels = sess.query(Label_).join(LabelSys_).join(TaskRecords_).filter(TaskRecords_.task_id == task_id).all()
    # 收集所有关键词，构建AC自动机：
    kws = []
    for l in labels:
        kws += l.keywords.split(' ')
    AC = AhoCorasick(kws)
    highlight_kws = list(AC.search(doc.content))
    highlighted_content = doc.content
    print('***********highlight_kws***********:\n', highlight_kws)
    if highlight_kws:
        for kw in highlight_kws:
            highlighted_content = highlighted_content.replace(kw, "<b style='color:orange'>" + kw + "</b>")

    doc_info = {'id':doc_id,'title':doc.title,'content':highlighted_content,
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



