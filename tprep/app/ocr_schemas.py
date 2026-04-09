from pydantic import BaseModel, Field


class OcrRequest(BaseModel):
    image_name: str = Field(..., description="File name or relative path under images/")
