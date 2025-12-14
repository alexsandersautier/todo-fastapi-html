from sqlmodel import SQLModel, Field, create_engine
from datetime import datetime

class User(SQLModel, table=True):
    
    id: int = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, unique=True, index=True)
    password: str = Field(nullable=False)
    
class Token(SQLModel, table=True):
    
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key=('user.id'))
    token: str = Field(nullable=False, unique=True)
    expiration_at: datetime = Field(nullable=False)
    
class Task(SQLModel, table=True):
    
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key=('user.id'))
    description: str = Field(nullable=False)
    completed: bool = Field(default=False)

CONN = 'sqlite:///database.db'
engine = create_engine(CONN)
SQLModel.metadata.create_all(bind=engine)
    