from pydantic import BaseModel
from internal import model

class StartInterviewResponse(BaseModel):
    interview_id: int
    is_suitable: bool
    llm_response: str
    total_question: int

class SendAnswerResponse(BaseModel):
    question_id: int
    message_to_candidate: str
    question_order_number: int
    interview_result: dict

class GetCandidateAnswersResponse(BaseModel):
    candidate_answers: list[model.CandidateAnswer]
    interview_messages: list[model.InterviewMessage]
