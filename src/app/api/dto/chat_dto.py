from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class SourceDTO(BaseModel):
    article_id: str
    title: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDTO]
