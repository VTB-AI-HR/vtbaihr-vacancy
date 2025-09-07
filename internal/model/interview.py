from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class GeneralResult(Enum):
    NEXT = "next"
    REJECTED = "rejected"
    IN_PROCESS = "in_process"


@dataclass
class Interview:
    id: int
    vacancy_id: int

    candidate_email: str
    candidate_resume_fid: str
    accordance_xp_vacancy_score: float
    accordance_skill_vacancy_score: float

    red_flag_score: float
    hard_skill_score: float
    soft_skill_score: float
    logic_structure_score: float
    accordance_xp_resume_score: float
    accordance_skill_resume_score: float
    strong_areas: str
    weak_areas: str

    general_score: float
    general_result: GeneralResult
    message_to_candidate: str
    message_to_hr: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['Interview']:
        return [
            cls(
                id=row.id,
                vacancy_id=row.vacancy_id,
                candidate_email=row.candidate_email,
                candidate_resume_fid=row.candidate_resume_fid,
                accordance_xp_vacancy_score=row.accordance_xp_vacancy_score,
                accordance_skill_vacancy_score=row.accordance_skill_vacancy_score,
                red_flag_score=row.red_flag_score,
                hard_skill_score=row.hard_skill_score,
                soft_skill_score=row.soft_skill_score,
                logic_structure_score=row.logic_structure_score,
                accordance_xp_resume_score=row.accordance_xp_resume_score,
                accordance_skill_resume_score=row.accordance_skill_resume_score,
                strong_areas=row.strong_areas,
                weak_areas=row.weak_areas,
                general_score=row.general_score,
                general_result=GeneralResult(row.general_result),
                message_to_candidate=row.message_to_candidate,
                message_to_hr=row.message_to_hr,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self):
        return {
            "id": self.id,
            "vacancy_id": self.vacancy_id,
            "candidate_email": self.candidate_email,
            "candidate_resume_fid": self.candidate_resume_fid,
            "general_score": self.general_score,
            "general_result": self.general_result.value,
            "message_to_candidate": self.message_to_candidate,
            "message_to_hr": self.message_to_hr,
            "red_flag_score": self.red_flag_score,
            "hard_skill_score": self.hard_skill_score,
            "soft_skill_score": self.soft_skill_score,
            "logic_structure_score": self.logic_structure_score,
            "accordance_xp_vacancy_score": self.accordance_xp_vacancy_score,
            "accordance_skill_vacancy_score": self.accordance_skill_vacancy_score,
            "accordance_xp_resume_score": self.accordance_xp_resume_score,
            "accordance_skill_resume_score": self.accordance_skill_resume_score,
            "strong_areas": self.strong_areas,
            "weak_areas": self.weak_areas,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class CandidateAnswer:
    id: int
    question_id: int
    interview_id: int
    response_time: int
    message_ids: list[int]
    llm_comment: str
    score: int

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['CandidateAnswer']:
        return [
            cls(
                id=row.id,
                question_id=row.question_id,
                interview_id=row.interview_id,
                response_time=row.response_time,
                message_ids=row.message_ids,
                llm_comment=row.llm_comment,
                score=row.score,
                created_at=row.created_at
            )
            for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "question_id": self.question_id,
            "interview_id": self.interview_id,
            "response_time": self.response_time,
            "message_ids": self.message_ids,
            "llm_comment": self.llm_comment,
            "score": self.score,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class InterviewMessage:
    id: int
    interview_id: int
    question_id: int
    audio_fid: str
    role: str
    text: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                interview_id=row.interview_id,
                question_id=row.question_id,
                audio_fid=row.audio_fid,
                role=row.role,
                text=row.text,
                created_at=row.created_at,
            ) for row in rows
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "interview_id": self.interview_id,
            "question_id": self.question_id,
            "audio_fid": self.audio_fid,
            "role": self.role,
            "text": self.text,
            "created_at": self.created_at.isoformat()
        }
