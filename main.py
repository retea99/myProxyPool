from datetime import timedelta
from contextlib import asynccontextmanager
import threading

from fastapi import Depends, FastAPI, HTTPException,File,UploadFile,Request
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # startup code
#     timer1 = threading.Timer(600, check, args=None, kwargs=None)
#     timer1.start()
#     yield
#     # shutdown code
    

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/",response_model=schemas.proxy)
def get_proxy(request:Request, db:Session=Depends(get_db)):
    proxy=crud.get_proxy(db,clientIp=request.client.host)
    if proxy is None:
        raise HTTPException(status_code=404,detail="There is no usable proxy or all proxy is being used.")
    return proxy

@app.get("/normal")
def get_proxy(request:Request, db:Session=Depends(get_db)):
    proxy=crud.get_proxy(db,clientIp=request.client.host)
    if proxy is None:
        raise HTTPException(status_code=404,detail="There is no usable proxy or all proxy is being used.")
    return crud.convert(proxy)

@app.post("/add/")
async def add(proxies:UploadFile = File(),db:Session=Depends(get_db)):
    content=await proxies.read()
    content = content.decode()
    lineList=content.split(';')
    proxiesList=[]
    for i in lineList:
        listOfi = i.split(',')
        proxy=schemas.proxy(ip=listOfi[0],port=listOfi[1],protocol=listOfi[2],country=listOfi[3])
        proxiesList.append(proxy)
    crud.add_new_proxies(db,proxiesList)
    return {'message':'got it.'}

# 不确定在不绑定至app的情况下能否这么使用
# 该方法实际上是在不断的回收上一个线程，并创建下一个新的线程，我认为这里可以优化
# 此处不可使用depends，depends只对路由函数可用
def check(db:Session=SessionLocal()):
    crud.check_all(db)
    db.close()
    threading.Timer(600, check, args=None, kwargs=None).start()
