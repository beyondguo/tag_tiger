"""
跟Document相关的一些api

1. 获取一条新数据
根据当前任务，随机获取一条未打标的数据，返回其id。
一获取就立马将其状态改为3，防止该数据被其他并发获取

2. 更新一条数据
获取用户的打标，在数据库中更新对应的标签值，同时修改state

"""

from fastapi import APIRouter, Depends, Form
from data_oprations import document_op
from schemas.Schemas import TaggingRecord
from data_oprations.users_op import get_admin_id, get_user_id
from pydantic import BaseModel

router = APIRouter()

@router.get('/document/fetch_one_doc')
def fetch_one_doc(task_id:int, user_id: int = Depends(get_user_id)):
    """
    获取一篇随机的未打标的文档的id, title, content
    """
    res = document_op.fetch_one_doc(task_id)
    if not res:
        return {"res": {}, "msg": "No untagged documents left! Woo~~"}
    else:
        return {"res": res, "msg": "I Got You!"}


@router.post('/document/view_one_doc')
def view_one_doc(doc_id:int):
    doc_info = document_op.view_one_doc(doc_id)
    if not doc_info:
        return {"res":{}, "msg":"No such doc id!"}
    return {"res":doc_info, "msg":"Success!"}


@router.post('/document/tag_one_doc')
async def tag_one_doc(tagging_record: TaggingRecord, user_id: int = Depends(get_user_id)):
    print(user_id)
    """
    提交打标页面，给一篇文档打上相应的各种标签.
    入参：tagging_record \
    {
    "doc_id": int,
    "user_id": int,
    "label_id_list": [int]
    }
    """
    res = document_op.tag_one_doc(tagging_record, user_id)
    if not res:
        return {"res": 0, "msg": "Already tagged or No such id!"}
    return {"res": 1, "msg": "Success!"}



@router.post('/document/pass_one_doc')
def pass_one_doc(doc_id: int=Form(...), user_id: int = Depends(get_user_id)):
    """
    跳过一篇文档
    """
    res = document_op.pass_ont_doc(doc_id)
    return res





