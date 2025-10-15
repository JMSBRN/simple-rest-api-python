from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session
from datetime import timedelta
from typing import List

# Импорты для SQLModel
from .database import get_db, engine, create_db_and_tables
from . import models, schemas, crud, auth

app = FastAPI(title="Blog API", version="1.0.0")

# Создаем таблицы при запуске
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Простой тестовый endpoint для проверки
@app.get("/")
def read_root():
    return {"message": "Blog API is working!"}

# Аутентификация
@app.post("/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

# Статьи
@app.get("/articles", response_model=List[schemas.Article])
def read_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return articles

@app.post("/articles", response_model=schemas.Article)
def create_article(
    article: schemas.ArticleCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    return crud.create_article(db=db, article=article, user_id=current_user.id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
