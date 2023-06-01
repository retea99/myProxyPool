from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP

from database import Base


class Proxy(Base):
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
    
    



    

