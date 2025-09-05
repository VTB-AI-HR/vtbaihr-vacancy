from pydantic import BaseModel
from internal import model

class StartInterviewResponse(BaseModel):
    is_suitable: bool
    resume_accordance_score: int
    message_to_candidate: str
    total_question: int
    interview_id: int
    question_id: int

class SendAnswerResponse(BaseModel):
    question_id: int
    message_to_candidate: str
    interview_result: dict

class GetCandidateAnswersResponse(BaseModel):
    candidate_answers: list[model.CandidateAnswer]
    interview_messages: list[model.InterviewMessage]
