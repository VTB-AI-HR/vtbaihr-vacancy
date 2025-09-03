from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class GeneralResult(Enum):
    NEXT = "next"
    REJECTED = "rejected"

@dataclass
class Interview:
    id: int
    vacancy_id: int

    candidate_email: str
    candidate_resume_fid: str  # file_id
    general_score: float  # [0;1]
    general_result: GeneralResult
    general_recommendation: str
    red_flag_score: float  # [0;1]
    hard_skill_score: float  # [0;1]
    soft_skill_score: float  # [0;1]
    logic_structure_score: float  # [0;1]
    accordance_xp_vacancy_score: float  # [0;1]
    accordance_skill_vacancy_score: float  # [0;1]
    accordance_xp_resume_score: float  # [0;1]
    accordance_skill_resume_score: float  # [0;1]
    strong_areas: str
    weak_areas: str

    pause_detection_score: float  # [0;1]
    emotional_coloring: str

    created_at: datetime

    @classmethod
    def serialize(cls, rows) -> list['Interview']:
        return [
            cls(
                id=row.id,
                vacancy_id=row.vacancy_id,
                candidate_email=row.candidate_email,
                candidate_resume_fid=row.candidate_resume_fid,
                general_score=row.general_score,
                general_result=GeneralResult(row.general_result),
                general_recommendation=row.general_recommendation,
                red_flag_score=row.red_flag_score,
                hard_skill_score=row.hard_skill_score,
                soft_skill_score=row.soft_skill_score,
                logic_structure_score=row.logic_structure_score,
                accordance_xp_vacancy_score=row.accordance_xp_vacancy_score,
                accordance_skill_vacancy_score=row.accordance_skill_vacancy_score,
                accordance_xp_resume_score=row.accordance_xp_resume_score,
                accordance_skill_resume_score=row.accordance_skill_resume_score,
                strong_areas=row.strong_areas,
                weak_areas=row.weak_areas,
                pause_detection_score=row.pause_detection_score,
                emotional_coloring=row.emotional_coloring,
                created_at=row.created_at
            )
            for row in rows
        ]

@dataclass
class CandidateAnswer:
    id: int
    question_id: int
    interview_id: int
    response_time: int
    message_ids: list[int]
    llm_comment: str
    score: int  # [0;10]

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