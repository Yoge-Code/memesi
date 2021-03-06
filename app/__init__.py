#!/usr/bin/env python
#  coding=utf-8
#  Author:  Yoge
#  Time:  2021/3/5

import time
from fastapi import FastAPI, Request, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.ext import rdb
from .tasks.fetch import fetch_task, fetch_task_key
from openpyxl import load_workbook


data_path = "data"


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    file_name = rdb.get(fetch_task_key)
    if not file_name:
        msg = "（文件第三列放商品名称，不能出现空行）上传要查询的文件: "
    else:
        down_load_url = str(request.base_url) + file_name.decode()
        msg = "有任务处理中, 稍后可按此链接下载:{}".format(down_load_url)
    return templates.TemplateResponse("index.html", {"request": request, "message": msg})


@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, background_tasks: BackgroundTasks, files: bytes=File(...)):
    key = int(time.time())
    file_name = "{}/{}.xlsx".format(data_path, key)
    with open(file_name, "wb") as f:
        f.write(files)
    # wb = load_workbook(file_name, read_only=True)
    # TODO 检查wb
    # new_file_key = "{}/{}_s.xlsx".format(data_path, key)
    down_load_url = str(request.base_url) + file_name
    background_tasks.add_task(fetch_task, file_name)
    if rdb.get(fetch_task_key):
        msg = "上传成功，处理些许时间，稍后按此链接下载{}".format(down_load_url)
    else:
        msg = "有任务处理中, 按此链接下载{}".format(down_load_url)
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "message": msg
                                       })
