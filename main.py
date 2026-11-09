from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import get_db, engine, Base
from models import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

@app.get("/")
def read_root():
    return {"message": "Fastapi Docker Demo"}

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users", response_model=list[UserResponse])
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users