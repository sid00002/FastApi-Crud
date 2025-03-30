from fastapi import FastAPI, Response, status,HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional 
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor  
from . import models
from sqlalchemy.orm import Session
from .database import engine, get_db
models.Base.metadata.create_all(bind=engine)
app = FastAPI()




while True:
    try:
        conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres", password="postgres", port="5432",
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connected succefully")
        break
    except Exception as error:
        print("connecting to database failed")
        print("Error ", error)
        time.sleep(2)

my_posts =[{"title":"post1","content":"this is my first post","published":True,"id":1},
           {"title":"post1","content":"this is my first post","published":True,"id":2},
           {"title":"post1","content":"this is my first post","published":True,"id":3},
           {"title":"post1","content":"this is my first post","published":True,"id":4},
           {"title":"post1","content":"this is my first post","published":True,"id":5},]

class Post(BaseModel):
    title: str
    content:str 
    published:bool = True
    rating: Optional[int] = None




def find_index_post(id):
    for i in range(len(my_posts)):
        if my_posts[i]['id'] == id:
            return i
    return None

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"status": posts}


@app.get("/")
def root():
    return {"message": "welcome to my api this is first time i am trying to deploy"}



@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM POSTS""")
    # posts = cursor.fetchall()
    posts =  db.query(models.Post).all()
    return {"data" : posts}



@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    try:
        # cursor.execute("""
        #     INSERT INTO posts (title, content, published)
        #     VALUES (%s, %s, %s) RETURNING *;
        # """, (
        #     new_post.title, new_post.content, bool(new_post.published)
        # ))

        # post = cursor.fetchone()
        # conn.commit()
        new_post = models.Post(**post.dict())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return {"new_post": new_post}
    except Exception as error:
        conn.rollback()
        print("Error occurred:", error)
        return {"error": "Database transaction failed"}




@app.get("/posts/{id}")
def get_post(id:int, db: Session = Depends(get_db)):
    try:
        # cursor.execute("""SELECT * FROM posts where id = %s """, (str(id)))
        # post = cursor.fetchone()
        post = db.query(models.Post).filter(models.Post.id==id).first()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
        return {"data" : post}
    except Exception as error:
        return {"error": "Some error occured"}





@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts where id = %s RETURNING *;""", (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.id==id).delete(synchronize_session=False)
    db.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)





@app.put("/posts/{id}")
def update_post(id:int, post:Post, db: Session = Depends(get_db)):
    # cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
    #                 (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    updated_query = db.query(models.Post).filter(models.Post.id==id)
    updated_post = updated_query.first()
    if updated_post ==  None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    updated_query.update({'title': 'Updated Title'})
    db.commit()
    return {"data" :updated_post}