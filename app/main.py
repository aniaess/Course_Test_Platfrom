from pathlib import Path
from typing import Annotated

from argon2 import PasswordHasher
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, StringConstraints

from psycopg2.errors import UniqueViolation

from app.database import get_connection
from utils.logger import get_logger


app = FastAPI()

password_hasher = PasswordHasher()


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:63342"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    name: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2, max_length=100)
    ]
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


@app.get("/register")
def register_page():
    return FileResponse(FRONTEND_DIR / "register.html")


@app.get("/health")
def health_check():
    """Check if the API is running."""
    return {"status": "MAIN_PY_IS_WORKING"}


@app.get("/db-test")
def database_test():
    """Check if the API can connect to the database."""
    connection = get_connection()
    connection.close()

    return {"database": "connected"}


@app.post("/users", status_code=201)
def create_user(user: User):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (user.name, user.email, password_hasher.hash(user.password))
        )

        user_id = cursor.fetchone()[0]

        connection.commit()

    except UniqueViolation:
        connection.rollback()

        raise HTTPException(
            status_code=409,
            detail="User with this email already exists"
        )

    finally:
        cursor.close()
        connection.close()

    return {
        "id": user_id,
        "name": user.name,
        "email": user.email
    }

app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")