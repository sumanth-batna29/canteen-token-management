from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, items, orders, analytics, tokens
from .database.database import engine
from .models import models

# Create tables (though we have schema.sql, this is good for dev)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Canteen Token Management System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(orders.router)
app.include_router(analytics.router)
app.include_router(tokens.router)

@app.get("/")
def home():
    return {"message": "Welcome to Canteen API"}
