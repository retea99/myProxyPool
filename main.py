from datetime import timedelta,datetime
from contextlib import asynccontextmanager
import threading
from typing import Union
from fastapi import Depends, FastAPI, HTTPException,File,UploadFile,Request
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError,jwt

models.Base.metadata.create_all(bind=engine)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # startup code
#     timer1 = threading.Timer(600, check, args=None, kwargs=None)
#     timer1.start()
#     yield
#     # shutdown code
    
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




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
def get_converted_proxy(request:Request, db:Session=Depends(get_db)):
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
# 此方法持续运行并不会不断无止境的占用内存，因为该方法创建的线程会被消除，而不是一直存在于系统中。
def check(db:Session=SessionLocal()):
    crud.check_all(db)
    db.close()
    threading.Timer(600, check, args=None, kwargs=None).start()


def get_current_user(token:str = Depends(oauth2_scheme)):
    user = decode_user(token)
    return user

def decode_user(token:str):
    '''用于解码token来获取token中包含的用户信息。'''
    pass


@app.post("/token")
async def login(user_form:OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)):
    pass

def verify_pw(plain_pw,hashed_pw):
    '''用于检测用户输入的明文密码是否匹配数据库中的hashed password'''
    return pwd_context.verify(plain_pw,hashed_pw)

def hash_password(plain_password):
    '''用于将新用户的明文密码hash'''
    return pwd_context.hash(plain_password)

def authenticate_user(db:Session,username:str,password:str):
    user = crud.get_user_by_username(db,username)
    if not user:
        return False
    if not verify_pw(password,user.hashedpw):
        return False
    return user

def create_access_token(data:dict,expires_delta:Union[timedelta,None]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow+expires_delta
    else:
        expire = datetime.utcnow + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt= jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt






