from typing import Union

from pydantic import BaseModel

class proxy(BaseModel):
    # http:str
    # https:str
    ip : str
    port : str
    protocol : str
    country : str

    class Config:
        orm_mode = True


class user(BaseModel):
    username:str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token:str
    token_type:str
