from pydantic import BaseModel


class AdminSchema(BaseModel):
    username: str
    password: str
