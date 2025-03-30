from pydantic import BaseModel, EmailStr
from typing import Optional 
class Post(BaseModel):
    title: str
    content:str 
    published:bool = True

class PostResponse(BaseModel):
    title: str
    content:str 
    published:bool
    
    class Config:
        orm_mode= True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
