from fastapi import APIRouter, File, UploadFile, Form, Depends
from data_oprations import task_op
from schemas.Schemas import Task
import json
from data_oprations.snow_flake import MySnow
import pandas as pd
from data_oprations.users_op import get_admin_id, get_user_id
import traceback

my_snow = MySnow(3)

router = APIRouter()


# 首页，查看任务信息总览：
@router.get("/task")
@router.get("/task/summary")
def task_summary():
    """
    ## 查看打标任务的总览信息
    """
    print('hello! summary! ')
    summary = task_op.get_summary()
    if summary is None:
        return {"res": [], "msg": "Not any tagging task defined yet!"}
    else:
        return {"res": summary, "msg": "Success!"}


@router.get('/task/counts')
def count_docs(task_id:int):
    counts = task_op.count_docs(task_id)
    return {"res": counts, "msg": "Success!"}


@router.get('/task/get_tagged_docs')
def get_tagged_docs(task_id:int, user_id:int):
    docs = task_op.get_tagged_docs(task_id, user_id)
    if not docs:
        return {"res":[], "msg": "Nothing here"}
    return {"res":docs, "msg": "Success"}


@router.get("/task/detail_by_id/{task_id}")
def task_detail_by_id(task_id: int):
    """
    ## 根据task_id获取关于这个task的详情
    """
    res = task_op.get_detail_by_id(task_id)
    if not res:
        return {"res": {}, "msg": "id not found!"}
    return {"res": res, "msg": "Success!"}


@router.get("/task/check_name/{task_name}")
def check_task_name(task_name: str):
    """
    ## 检查是否已存在某任务名
    """
    return task_op.check_task_name(task_name)


@router.post("/task/add_task")
def add_task(task_json_str: str = Form(...), file: UploadFile = File(...), admin_id: int = Depends(get_admin_id)):
    """
    ## 添加一个新的打标任务，包括基础信息和数据集

    涉及到文件和其他数据同时上传时，由于FastAPI只能接收一种类型的数据，而这个file是当做Form处理的，
    因此其他的数据也应该用Form的形式提供。

    task_json_str: 按照Task schema的格式提供json字符串
    ```
    {"name":str, "desc":str, "label_sys_ids":[int]}
    ```
    file: 上传的文件
    """
    task_dict = json.loads(task_json_str)
    task = Task(**task_dict)  # 这是Pydantic的对象初始化方式

    # CHECK1: 是否已存在该task name：
    if task_op.check_task_name(task.name):
        return {'res': 0, 'msg': 'Task name already exists!'}
    # CHECK2: 文件后缀
    post = file.filename.split('.')[-1]
    if post in ['xlsx', 'xls']:
        df = pd.read_excel(file.file)
    elif post == 'csv':
        df = pd.read_csv(file.file)
    else:
        return {'res': 0, 'msg': '上传文件必须是.xlsx/.xls/.csv格式！'}
    # CHECK3: 数据字段
    columns = df.columns
    if 'title' not in columns or 'content' not in columns:
        return {'res': 0, 'msg': "数据表首行必须包含 'title' 和 'content' 字段，请检查上传文件！"}
    # 填充缺失值nan，否则数据库无法处理
    df.fillna("", inplace=True)

    # 获取task_id,准备插入task、task_records、document表
    # try:
    task_id = int(my_snow.get_id())
    # 插入task、task_records表：
    task_op.add_task_info(task, task_id, admin_id)
    # 插入document表：
    counts = task_op.upload_to_db(df, task_id)
    return {"res": counts, "msg": "成功创建新任务（id=%s），数据集成功导入数据库！" % task_id}
    # except:
    #     return {"res": 0, "msg": traceback.format_exc()}


@router.post("/task/delete_task")
def delete_task(task_id:int, admin_id: int = Depends(get_admin_id)):
    res = task_op.delete_task(task_id)
    if res:
        return {"res":1, "msg":"Delete Successfully!"}
    return {"res":0, "msg":"Nothing to delete!"}