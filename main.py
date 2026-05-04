from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import auth, documents, query
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Wiki -Devops knowledge Base",
    description="Rag chatbot for internal Devops documentation",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(query.router)


@app.get("/")
def root():
    return {"message": "Wiki API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
