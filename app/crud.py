from sqlalchemy.orm import Session
from .models import User, Article
from .auth import get_password_hash, verify_password
from .schemas import UserCreate, ArticleCreate

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def get_articles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Article).offset(skip).limit(limit).all()

def create_article(db: Session, article: ArticleCreate, user_id: int):
    db_article = Article(**article.dict(), author_id=user_id)
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article