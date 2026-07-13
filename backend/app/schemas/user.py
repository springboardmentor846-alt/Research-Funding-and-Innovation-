from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    organization: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str
    organization: str


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    organization: str
    role: str

    class Config:
        from_attributes = True