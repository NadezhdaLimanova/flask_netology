import datetime
import os
import atexit
from sqlalchemy import UUID, create_engine, DateTime, String, func, ForeignKey
from sqlalchemy.orm import sessionmaker, DeclarativeBase, mapped_column, Mapped, relationship
import uuid
from typing import List, Type


POSTGRES_DB = os.getenv('POSTGRES_DB', 'for_flask')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'pass_postgres')

PG_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    token: Mapped[uuid.UUID] = mapped_column(
            UUID, server_default=func.gen_random_uuid(), unique=True
        )

    # tokens: Mapped[List["Token"]] = relationship(
    #     "Token", back_populates="user", cascade="all, delete-orphan"
    # )
    advertisements: Mapped[List["Advertisement"]] = relationship(
        "Advertisement", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "advertisements": [advertisements.id for advertisements in self.advertisements],
        }


class Advertisement(Base):
    __tablename__ = "app_for_advertisements"

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    registration_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped[User] = relationship(User, back_populates="advertisements")

    @property
    def json(self):
        return {
            "id": self.id,
            "author": self.author,
            "title": self.author,
            "description": self.description,
            "registration_time": self.registration_time.isoformat(),
            "user_id": self.user_id,
        }


# class Token(Base):
#     __tablename__ = "token"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     token: Mapped[uuid.UUID] = mapped_column(
#         UUID, server_default=func.gen_random_uuid(), unique=True
#     )
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     user: Mapped[User] = relationship(User, back_populates="tokens")


# MODEL_TYPE = Type[User | Token | Advertisement]
# MODEL = User | Token | Advertisement

MODEL_TYPE = Type[User | Advertisement]
MODEL = User | Advertisement


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
atexit.register(engine.dispose)
