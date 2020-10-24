from fastapi import APIRouter, Depends
from typing import Optional, List
from schemas.Schemas import LabelSys
from data_oprations import label_sys_op  # 包含label_sys相关操作的包
from data_oprations.users_op import get_admin_id, get_user_id
from fastapi.responses import FileResponse
from pydantic import BaseModel
router = APIRouter()


# 首页，展示label systems信息总览
@router.get("/label_sys")
@router.get("/label_sys/summary")
def label_sys_summary():
    """
    ## 查看分类体系信息总览
    """
    summary = label_sys_op.get_summary()
    if summary is None:
        return {"res": [], "msg": "Not any label system defined yet!"}
    else:
        return {"res": summary, "msg": "Success!"}


# 根据label system name查看具体详情：
@router.get("/label_sys/detail_by_name/{label_sys_name}")
def label_sys_detail_by_name(label_sys_name: str):
    """
    ## 根据label_sys_name查看具体详情：
    """
    detail = label_sys_op.get_detail_by_name(label_sys_name)
    if detail is None:
        return {"res": {}, "msg": "label_sys_name '%s' not found!" % label_sys_name}
    else:
        return {"res": detail, "msg": "Success!"}


@router.get("/label_sys/detail_by_id/{label_sys_id}")
def label_sys_detail_by_id(label_sys_id: int):
    """
    ## 根据label_sys_id查看具体详情：
    """
    detail = label_sys_op.get_detail_by_id(label_sys_id)
    if detail is None:
        return {"res": {}, "msg": "label_sys_id '%s' not found!" % label_sys_id}
    else:
        return {"res": detail, "msg": "Success!"}


@router.get("/label_sys/check_name/{label_sys_name}")
def check_label_sys_name(label_sys_name: str):
    """
    ## 查看某label system name是否存在：
    """
    return label_sys_op.check_label_sys_name(label_sys_name)


@router.get("/label_sys/get_label_sys_list")
def get_label_sys_list():
    """
    ## 获取分类体系的信息列表，包括id和name
    """
    res =  label_sys_op.get_label_sys_list()
    if res is None:
        return {"res":[], "msg":""}
    else:
        return {"res":res, "msg":"Success!"}



@router.post("/label_sys/add_label_sys")
def add_label_sys(label_sys: LabelSys, admin_id: int = Depends(get_admin_id)):
    """
    ## 新建分类体系：
    从前端接收json信息，这也是LabelSys的格式
    """
    res = label_sys_op.add_label_sys(label_sys, admin_id)
    if res is None:
        return {"res": {}, "msg": "label system already exists!"}
    return {"res": res, "msg": "Success!"}


@router.post("/label_sys/delete_label_sys")
def delete_label_sys(label_sys_id:int, admin_id: int = Depends(get_admin_id)):
    res = label_sys_op.delete_label_sys(label_sys_id)
    if res:
        return {"res":1, "msg":"Delete Successfully!"}
    return {"res":0, "msg":"Nothing to delete!"}


@router.post("/label_sys/get_related_tasks")
def get_related_tasks(label_sys_id:int):
    res = label_sys_op.get_related_tasks(label_sys_id)
    return {"res":res, "msg":"Success!"}


class LsDataRequestBody(BaseModel):
    label_sys_id : int
    task_id_list : List

# 还缺少一个下载完立马删除服务器上文件的功能
@router.post("/label_sys/download")
def download(downlad_request: LsDataRequestBody, user_id: int = Depends(get_user_id)):
    """
    task_id_list为空列表时，默认下载全部任务的打标数据
    """
    label_sys_id = downlad_request.label_sys_id
    task_id_list = downlad_request.task_id_list
    file_name = label_sys_op.label_sys_tagged_data_download(label_sys_id, task_id_list)
    return FileResponse('download_datasets/%s.xlsx'%file_name, filename='%s.xlsx' % file_name)


@router.post("/label_sys/label_counts")
def label_counts(req: LsDataRequestBody):
    label_sys_id = req.label_sys_id
    task_id_list = req.task_id_list
    counts = label_sys_op.label_counts(label_sys_id, task_id_list)
    return counts
