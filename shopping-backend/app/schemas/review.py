from pydantic import BaseModel, Field

class ReviewCreate(BaseModel):

    rating: int = Field(ge=1, le=5)

    comment: str


class ReviewUpdate(BaseModel):

    rating: int = Field(ge=1, le=5)

    comment: str