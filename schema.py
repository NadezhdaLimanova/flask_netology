from abc import ABC
from pydantic import BaseModel, field_validator
from typing import Optional
import re


class AbstractClass(BaseModel, ABC):
    name: str
    password: str


class Login(AbstractClass):
    pass


class CreateUser(AbstractClass):
    email: str
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        password_length = len(value)
        if password_length < 8 or password_length > 16:
            raise ValueError("The password must be between 8 and 16 characters long")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        if not bool(re.fullmatch(r'[\w.-]+@[\w-]+\.[\w.]+', value)):
            raise ValueError("Email is invalid")
        return value


class PatchUser(CreateUser):
    name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None


class CreateAdv(BaseModel):
    author: str
    title: str
    description: Optional[str]


class PatchAdv(BaseModel):
    author: str
    title: Optional[str] = None
    description: Optional[str] = None


