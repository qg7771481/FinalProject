from fastapi import FastAPI
from app.routes import auth, users, chat

app = FastAPI(title="Skills Exchange API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(chat.router)

