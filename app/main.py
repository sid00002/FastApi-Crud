from fastapi import FastAPI, Response, status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional 
from random import randrange
import psycopg2
import time
from psycopg2.extras import RealDictCursor  
app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(host="localhost", database="fastapi", user="postgres", password="postgres", port="5522",
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



@app.get("/")
def root():
    return {"message": "welcome to my api this is first time i am trying to deploy"}



@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM POSTS""")
    posts = cursor.fetchall()
    return {"data" : posts}



@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):
    try:
        cursor.execute("""
            INSERT INTO posts (title, content, published)
            VALUES (%s, %s, %s) RETURNING *;
        """, (
            new_post.title, new_post.content, bool(new_post.published)
        ))

        post = cursor.fetchone()
        conn.commit()
        return {"new_post": post}
    except Exception as error:
        conn.rollback()
        print("Error occurred:", error)
        return {"error": "Database transaction failed"}




@app.get("/posts/{id}")
def get_post(id:str, response:Response):
    try:
        cursor.execute("""SELECT * FROM posts where id = %s """, (str(id)))
        post = cursor.fetchone()
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
        return {"data" : post}
    except Exception as error:
        return {"error": "Some error occured"}





@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    cursor.execute("""DELETE FROM posts where id = %s RETURNING *;""", (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)





@app.put("/posts/{id}")
def update_post(id:int, post:Post):
    cursor.execute("""UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
                    (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post ==  None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")
    return {"data" :updated_post}