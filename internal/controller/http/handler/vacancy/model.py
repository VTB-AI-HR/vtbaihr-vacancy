from pydantic import BaseModel


class StartInterviewBody(BaseModel):
    vacancy_id: int
    candidate_email: str
    candidate_resume_fid: str

class StartInterviewResponse(BaseModel):
    is_suitable: bool
    llm_response: str

class SendAnswerResponse(BaseModel):
    question_id: int
    llm_response: str
