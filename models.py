from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP

from database import Base


class Proxy(Base):
    '''用于存储我们所拥有的全部代理的数据库。'''
    __tablename__="proxies"
    '''
    协议、IP、端口、国家
    '''
    id = Column(Integer, primary_key=True, index=True)
    # http= Column(String)
    # https= Column(String)
    ip = Column(String)
    port = Column(String)
    protocol = Column(String)
    country = Column(String)
    create_time = Column(TIMESTAMP)
    # 该条代理是否是可用的代理
    usable= Column(Boolean, default=False)
    # 该条代理是否正在被使用
    using= Column(Boolean, default=False)
    # 出于安全性考虑，这里不可以直接使用用户发来的request中的ip作为用来区别用户的特征，例如同一路由器下的几台机器，在外界看来拥有相同的ip地址。
    user = Column(String,default=None)
    

class User(Base):
    '''一个用于存储用户基本信息的表格，为了防止恶意程序去占用数据库中的所有代理，我们设定需要用户进行登录才可以获取连接。'''
    __tablename__="users"

    uid = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True)
    hashedpw = Column(String)
    using=Column(Boolean,default=False)
    # 这两项设置为当用户忘记密码时用于重置密码，但是考虑到安全性问题，不确定是否应该将这两个问题明码放在数据库中或对answer项依旧采用hash处理。
    # question = Column(String)
    # answer = Column(String)

    



    

