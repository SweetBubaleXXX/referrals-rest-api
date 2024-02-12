from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCredentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
