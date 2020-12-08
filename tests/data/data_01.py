from datetime import datetime
from typing import List
from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str
    signup_ts: datetime
    friends: List[int]