from fastapi import APIRouter, Response, Depends, Form
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from data_oprations import users_op

router = APIRouter()

@router.post('/admin/login')
async def admin_login(response: Response, username: str = Form(...), password: str = Form(...)):
    res_info = users_op.check_login_info(username,password,'admin')
    if res_info["res"] == 0:
        return res_info
    response.set_cookie(key="token", value=res_info["token"])
    return {"res":1, "token": res_info["token"]}


@router.post('/user/login')
async def user_login(response: Response, username: str = Form(...), password: str = Form(...)):
    res_info = users_op.check_login_info(username,password,'normal')
    if res_info["res"] == 0:
        return res_info
    response.set_cookie(key="token", value=res_info["token"])
    return {"res":1, "token": res_info["token"]}

@router.get("/admin/logout")
async def admin_logout(response: Response):
    response.delete_cookie("token")
    # return RedirectResponse("/") # 不知为何这样子cookie就无法删除了
    return 1

@router.get("/user/logout")
async def user_logout(response: Response):
    response.delete_cookie("token")
    # return RedirectResponse("/") # 不知为何这样子cookie就无法删除了
    return 1