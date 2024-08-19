from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import crud
import models
import schemas
from database import SessionLocal, engine
import uvicorn

import openai
import os


models.Base.metadata.create_all(bind=engine)
app = FastAPI()




@app.get("/")
async def root():
    return {"message": "Hello Azure OpenAI"}

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OpenAIのAPIキーを設定
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/chat/", response_model=List[schemas.Message])
def chat_with_ai(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    # ユーザーメッセージを保存
    user_message = crud.create_message(db=db, message=message)
    
    # OpenAI APIを使用して回答を生成（新しいAPIを使用）
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message.content},
        ]
    )
    
    # AIからの回答を保存
    ai_message_content = response.choices[0].message['content'].strip()
    ai_message = schemas.MessageCreate(content=ai_message_content, is_stupid_question=False)
    crud.create_message(db=db, message=ai_message)
    
    # これまでのメッセージ一覧を取得
    messages = crud.get_all_messages(db=db)
    
    # メッセージ一覧を返す
    return messages

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
        user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.create_message(db=db, message=message)

@app.get("/messages/", response_model=List[schemas.Message])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = crud.get_all_messages(db, skip=skip, limit=limit)
    return messages

@app.delete("/messages/")
def delete_messages(db: Session = Depends(get_db)):
    crud.delete_all_messages(db=db)
    return {"message": "All messages deleted"}  


if __name__ == '__main__':
    uvicorn.run(app=app)


