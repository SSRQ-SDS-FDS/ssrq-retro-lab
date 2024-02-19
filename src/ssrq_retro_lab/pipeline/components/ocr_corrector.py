from pydantic import BaseModel

class CorrectedOCRText(BaseModel):
    text: list[str]
