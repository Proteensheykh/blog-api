from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from alembic import command
from alembic.config import Config

from . import models
from .database import engine
from .routers import posts, users, auth, likes

# models.Base.metadata.create_all(bind=engine)

def create_database():
    # Create a Config object, pointing to the alembic.ini file
    alembic_cfg = Config("alembic.ini")
    # Run the Alembic upgrade command to apply all migrations
    command.upgrade(alembic_cfg, "head")

app = FastAPI()

origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(likes.router)

@app.on_event("startup")
async def startup_event():
    create_database()

@app.get("/")
def read_root():
    return {"Hello": "World!!!  :D"}
