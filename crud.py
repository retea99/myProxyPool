from sqlalchemy.orm import Session
import requests
import time
import schemas
from requests import Response
from models import Proxy
from schemas import proxy
from datetime import datetime

test_url="xxxxxxxx"

# 需要编写一个用于释放被还回来的代理的方法
def release_proxy(db:Session,clientIp:str):
    proxyUsedByUser = db.query(Proxy).filter(Proxy.user==clientIp).first()
    if proxyUsedByUser != None:
        proxyUsedByUser.user=None
        db.commit()
    if db.query(Proxy).filter(clientIp == Proxy.ip):
        raise RuntimeError("You are using a proxy and the proxy is usable!")






def get_proxy(db:Session,clientIp:str):
    release_proxy(db,clientIp=clientIp)
    proxy= db.query(Proxy).filter(Proxy.usable==True,Proxy.using==False).first()
    # 设置该条代理已经被占用，并且记录下使用者的原始ip地址
    proxy.using = True
    proxy.user=clientIp
    db.commit()
    return proxy


# 目前的想法是使用一个定时器，来周期性验证每条代理是否是可用的代理。但还未计划好将定时器放在哪里。与直接启动一个文件不同，使用fastapi时，似乎并不会直接加载定时器。目前比较理想的地点是在生命周期事件中尝试开启一个循环事件。
# 先从数据库中获取所有条目，随后调用check_one来对其中的每一条数据进行检查
def check_all(db:Session):
    proxies=db.query(Proxy).all()
    for p in proxies:
        p.usable=check_one(p)
        db.commit()
    

def check_one(p:Proxy):
    response=requests.get(test_url,proxies=convert(p))
    if response.text in p.http:
        return True
    else:
        return False
    
# 用于向数据库中加入新的代理的方法
def add_new_proxies(db:Session,proxies:list[schemas.proxy]):
    for proxy in proxies:
        # db_proxy=Proxy(http=proxy.http,https=proxy.https)
        db_proxy = Proxy(ip=proxy.ip,port=proxy.port,protocol = proxy.protocol,country = proxy.country,create_time=datetime.now())
        db.add(db_proxy)
        db.commit()


def convert(p:Proxy):
    return {
        "http": "http://%(ip)s:%(port)s" %{'ip':p.ip,'port':p.port},
        "https": "https://%(ip)s:%(port)s" %{'ip':p.ip,'port':p.port}
    }

