from models import User, Token, Task, engine
from sqlmodel import Session, select
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils import *
from DTO import *
from datetime import datetime, timedelta
from typing import List

app = FastAPI()

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/login')
def login(request: UserDTO) -> int:
    '''
    Return: 
      0 - login success
      1 - not found
      2 - invalid password
      3 - internal server error
    '''
    try:
        with Session(engine) as session:
            statement = select(User).where(User.username == request.username)
            user = session.exec(statement).first()
            if user:
                password_db = cripty(request.password)
                if user.password == password_db:
                    generate_token(user.id)
                    return 0
                else:
                    return 2
            else:
                return 1
    except:
        return 3
    
@app.post('/register')
def register(request: UserDTO) -> int:
    '''
    Return:
      0 - created succefull
      1 - user exists
      2 - invalid data
      3 - internal server error
    '''
    
    try:
        with Session(engine) as session:
            statement = select(User).where(User.username == request.username)
            user = session.exec(statement).first()
            if user:
                return 1
            else:
                password_db = cripty(request.password)
                new_user = User(username=request.username, password=password_db)
                session.add(new_user)
                session.commit()
                return 0
                
    except Exception as e:
        print(e)
        return 3
    

@app.post('/getToken')
def token(username):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        if user:
            return generate_token(user.id)
            
def generate_token(user_id: int):
    try:
        with Session(engine) as session:
            user = session.get(User, user_id)
            if not user:
                return None

            statement = select(Token).where(Token.user_id == user.id)
            user_token = session.exec(statement).first()

            expiration = datetime.now() + timedelta(minutes=1440)

            if user_token:
                if datetime.now() > user_token.expiration_at:
                    user_token.token = get_token()
                    user_token.expiration_at = expiration
                    session.add(user_token)
                    session.commit()
                    session.refresh(user_token)
                return user_token.token

            new_user_token = Token(
                user_id=user_id,
                token=get_token(),
                expiration_at=expiration
            )
            session.add(new_user_token)
            session.commit()
            session.refresh(new_user_token)
            return new_user_token.token

    except Exception as e:
        print(e)
        return None
    
@app.get('/tasks')
def get_all_tasks(token):
    '''
    Return:
    [task]
    1 token expirated
    '''
    tasks = []
    try:
        with Session(engine) as session:
            statement = select(Token).where(Token.token == token)
            token = session.exec(statement).first()
            if token.expiration_at < datetime.now():
                return 1
            statement = select(Task).where(Task.user_id == token.user_id)
            tasks = session.exec(statement).all()
        return tasks 
    except:
        ...
    
@app.get('/task')
def get_by_id(id, token):
    '''
    Return:
    object
    1 - expirated token
    '''
    with Session(engine) as session:
        if is_expirated_token(token):
            return 1
        else:
            task = session.get(Task, id)
            return task
    
@app.post('/task')
def create(description, token):
    '''
    Return:
    object
    1 - expirated token
    '''
    with Session(engine) as session:
        if is_expirated_token(token):
            return 1
        else:
            statement = select(Token).where(Token.token == token)
            token_db = session.exec(statement).first()
            if token_db:
                task = Task(user_id=token_db.user_id, description=description)
                session.add(task)
                session.commit()
                session.refresh(task)
                return task
        

@app.put('/task')
def update(task_id, token):
    '''
    Return:
    object
    1 - expirated token
    '''
    with Session(engine) as session:
        if is_expirated_token(token):
            return 1
        else:
            statement = select(Token).where(Token.token == token)
            token_db = session.exec(statement).first()
            if token_db:
                statement = select(Task).where(Task.id == task_id)
                task = session.exec(statement).first()
                task.completed = True
                session.add(task)
                session.commit()
                session.refresh(task)
                return task
    
def is_date_valid(date):
    return date > datetime.now()

def is_expirated_token(token):
    try:
        with Session(engine) as session:
            statement = select(Token).where(Token.token == token)
            current_token = session.exec(statement).first()
            if current_token and is_date_valid(current_token.expiration_at):
                return False
            else:
                return True
    except:
        return True