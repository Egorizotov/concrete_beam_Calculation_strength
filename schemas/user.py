from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    user_username: str = Field(..., min_length=3, max_length=50)
    user_email: str = Field(..., min_length=5, max_length=100)
    user_password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    user_username: str
    user_password: str


class UserResponse(BaseModel):
    user_id: int
    user_username: str
    user_email: str

    class Config:
        from_attributes = True