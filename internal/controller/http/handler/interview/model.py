from pydantic import BaseModel

class StartInterviewResponse(BaseModel):
    is_suitable: bool
    llm_response: str

class SendAnswerResponse(BaseModel):
    question_id: int
    llm_response: str
    question_order_number: int
    interview_result: dict
