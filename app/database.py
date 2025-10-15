from sqlmodel import SQLModel, create_engine, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session