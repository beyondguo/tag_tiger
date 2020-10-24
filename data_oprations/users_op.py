import time
from datetime import datetime
from models.Models import Admin_, User_
from fastapi import HTTPException,Cookie,Header
from data_oprations.database import SessionLocal
from data_oprations.snow_flake import MySnow
import hashlib
my_snow = MySnow(2)
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN
import traceback


def generate_token(username: str, password: str):
    s = username + password + 'just for fun'
    token = hashlib.sha256(s.encode('utf-8')).hexdigest()
    return token


def check_login_info(username: str, password: str, user_type: str):
    sess = SessionLocal()
    if user_type == 'admin':
        user = sess.query(Admin_).filter(Admin_.username == username).first()
    else:
        user = sess.query(User_).filter(User_.username == username).first()
    if not user:
        return {"res": 0, "msg": "该用户名不存在！"}
    if user.password != password:
        return {"res": 0, "msg": "密码错误！"}
    token = generate_token(username, password)
    # 把token存入数据库中，便于后面查询对应的用户
    sess = SessionLocal()
    if user_type == 'admin':
        sess.query(Admin_).filter(Admin_.username == user.username).update({Admin_.token: token})
    else:
        sess.query(User_).filter(User_.username == user.username).update({User_.token: token})
    sess.commit()
    return {"res": 1, "token": token}


def get_id_by_token(token: str, admin_only = False):
    sess = SessionLocal()
    admin_user = sess.query(Admin_).filter(Admin_.token == token).first()
    normal_user = sess.query(User_).filter(User_.token == token).first()
    if admin_only:
        user = admin_user
    else:
        if not admin_user:
            user = normal_user
        else:
            user = admin_user
    if not user:
        return None
    return user.id


async def get_admin_id(x_token:str=Header(...)):
    #token: str = request.cookies.get("token")
    admin_id = get_id_by_token(x_token, admin_only=True)
    if not admin_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
        )
    return admin_id


async def get_user_id(x_token:str=Header(...)):
    #token: str = request.cookies.get("token")
    user_id = get_id_by_token(x_token, admin_only=False)
    if not user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
        )
    return user_id
