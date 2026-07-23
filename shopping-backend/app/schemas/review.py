from pydantic import BaseModel

class ReviewCreate(BaseModel):

    rating: int

    comment: str


class ReviewUpdate(BaseModel):

    rating: int

    comment: str